import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .utils import verifier_token, get_payment_client, CinetPayError
from .models import Transaction, Order, Livraison
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

def _traiter_resultat_paiement(transaction, verification):
    if verification.get('code') == '00' and verification['data']['status'] == 'ACCEPTED':
        transaction.statut = 'reussi'
        transaction.operateur = verification['data'].get('payment_method', '')
        transaction.save()

        order = transaction.order
        try:
            order.confirmer()
            order.statut_paiement = 'paye'
            order.save()
        except ValueError:
            transaction.statut = 'echoue'
            transaction.save()
            order.statut_paiement = 'echoue'
            order.statut = Order.Statut.ANNULEE
            order.save()
    else:
        transaction.statut = 'echoue'
        transaction.save()


@api_view(['POST'])
@permission_classes([AllowAny])
def initier_paiement(request):
    user, erreur = verifier_token(request)
    if erreur:
        return Response({"erreur": erreur}, status=status.HTTP_401_UNAUTHORIZED)

    order = get_object_or_404(Order, id=request.data.get('order_id'), user=user)
    if order.statut_paiement == 'paye':
        return Response({"erreur": "Cette commande est déjà payée"}, status=status.HTTP_400_BAD_REQUEST)

    telephone_paiement = request.data.get('telephone') or user.telephone
    cinetpay_transaction_id = f"EKMER{uuid.uuid4().hex[:16].upper()}"
    transaction = Transaction.objects.create(
        order=order, type_transaction='paiement', montant=order.total,
        cinetpay_transaction_id=cinetpay_transaction_id, statut='en_attente',
    )
    client_data = {
        "nom": user.username or "", "prenom": "",
        "telephone": telephone_paiement or "", "email": user.email or "",
        "ville": order.livraison.ville_livraison if hasattr(order, 'livraison') else "Douala",
    }
    try:
        resultat = get_payment_client().initier_paiement(
            transaction_id=cinetpay_transaction_id, montant=order.total,
            description=f"Paiement commande E-KMER #{order.id}", client=client_data,
            notify_url="https://tondomaine.com/api/paiements/webhook/",
            return_url="https://tondomaine.com/paiement/retour",
        )
        transaction.payment_token = resultat['payment_token']
        transaction.save()
    except CinetPayError as e:
        transaction.statut = 'echoue'
        transaction.save()
        return Response({"erreur": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({
        "payment_url": resultat['payment_url'],
        "transaction_id": cinetpay_transaction_id,
        "mode": "production" if getattr(settings, 'PAIEMENT_MODE', 'simulation') == 'production' else "simulation",
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_callback(request):
    cinetpay_transaction_id = request.data.get('cpm_trans_id') or request.data.get('transaction_id')
    if not cinetpay_transaction_id:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    transaction = get_object_or_404(Transaction, cinetpay_transaction_id=cinetpay_transaction_id)
    verification = get_payment_client().verifier_paiement(cinetpay_transaction_id)  # ← utilisait CinetPayClient() en dur
    _traiter_resultat_paiement(transaction, verification)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def simuler_paiement(request):
    if getattr(settings, 'PAIEMENT_MODE', 'simulation') == 'production':
        return Response({"erreur": "Simulation désactivée en production"}, status=status.HTTP_403_FORBIDDEN)

    transaction_id = request.data.get('transaction_id')
    transaction = get_object_or_404(Transaction, cinetpay_transaction_id=transaction_id)
    verification = get_payment_client().verifier_paiement(transaction_id)
    _traiter_resultat_paiement(transaction, verification)
    return Response({"statut": transaction.statut, "order_statut": transaction.order.statut})

def declencher_remboursement(order):
    transaction_paiement = order.transactions.filter(
        type_transaction='paiement', statut='reussi'
    ).first()
    if not transaction_paiement:
        return None

    client_transaction_id = f"REMB{uuid.uuid4().hex[:16].upper()}"

    transaction_remboursement = Transaction.objects.create(
        order=order,
        type_transaction='remboursement',
        montant=transaction_paiement.montant,
        numero_telephone=order.client.telephone,
        cinetpay_transaction_id=client_transaction_id,
        statut='en_attente',
    )

    try:
        cinetpay_client = get_payment_client()
        resultat = cinetpay_client.initier_remboursement(
            client_transaction_id=client_transaction_id,
            montant=transaction_paiement.montant,
            numero_telephone=order.client.telephone,
            notify_url="https://tondomaine.com/api/paiements/webhook-transfert/",
        )
        transaction_remboursement.statut = 'en_attente'
        transaction_remboursement.save()
        return resultat
    except CinetPayError as e:
        transaction_remboursement.statut = 'echoue'
        transaction_remboursement.save()
        raise