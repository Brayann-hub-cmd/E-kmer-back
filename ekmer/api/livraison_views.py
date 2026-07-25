from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Livraison, Livreur, Order
from .serializers import (
    LivraisonSerializer, LivraisonCreateSerializer,
    LivraisonReponseLivreurSerializer, LivraisonMarquerLivreeSerializer,
    LivraisonConfirmationClientSerializer,
)
from .views import verifier_token

class LivraisonCreateView(APIView):
    def post(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        order = get_object_or_404(Order, id=request.data.get('order'), user=user)
        serializer = LivraisonCreateSerializer(data={**request.data, "order": order.id})
        serializer.is_valid(raise_exception=True)
        livraison = serializer.save()
        return Response(LivraisonSerializer(livraison).data, status=status.HTTP_201_CREATED)

class MesLivraisonsLivreurView(APIView):
    def get(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        livraisons = Livraison.objects.filter(livreur=livreur).order_by('-created_at')
        return Response(LivraisonSerializer(livraisons, many=True).data)

def _get_livraison_du_livreur(id, user):
    livraison = get_object_or_404(Livraison, id=id)
    if not livraison.livreur or livraison.livreur.user != user:
        return None
    return livraison

class LivraisonRepondreView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livraison = _get_livraison_du_livreur(id, user)
        if not livraison:
            return Response({"error": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        serializer = LivraisonReponseLivreurSerializer(livraison, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LivraisonSerializer(livraison).data)

class LivraisonDemarrerView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livraison = _get_livraison_du_livreur(id, user)
        if not livraison:
            return Response({"error": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        if livraison.statut != 'acceptee':
            return Response({"error": "La livraison doit être acceptée d'abord."}, status=status.HTTP_400_BAD_REQUEST)
        livraison.statut = 'en_cours'
        livraison.save()
        return Response(LivraisonSerializer(livraison).data)

class LivraisonMarquerLivreeView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livraison = _get_livraison_du_livreur(id, user)
        if not livraison:
            return Response({"error": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        serializer = LivraisonMarquerLivreeSerializer(livraison, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LivraisonSerializer(livraison).data)

class LivraisonConfirmerView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livraison = get_object_or_404(Livraison, id=id)
        if livraison.order.user != user:
            return Response({"error": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        serializer = LivraisonConfirmationClientSerializer(livraison, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LivraisonSerializer(livraison).data)

class LivraisonParCommandeView(APIView):
    def get(self, request, order_id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        order = get_object_or_404(Order, id=order_id, user=user)
        if not hasattr(order, 'livraison'):
            return Response({"error": "Aucune livraison associée à cette commande"}, status=status.HTTP_404_NOT_FOUND)
        return Response(LivraisonSerializer(order.livraison).data)