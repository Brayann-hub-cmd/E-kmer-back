from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import VenteSerializer,VenteDetailSerializer,LigneDetailVenteSerializer,PanierSerializer,PanierItemSerializer,OrderSerializer
from .models import Vente, Users, Annonce,Panier,PanierItem,Order,OrderItems
from django.conf import settings
from django.shortcuts import get_object_or_404
import jwt
def verify(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None,"Token Manquant,connectez vous!"
    if not auth_header.startswith('Bearer '):
        return None, "Format du token invalide"
    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        user = Users.objects.get(id=payload['id'])
        return user,None
    except jwt.ExpiredSignatureError:
        return None,"Token expiré, reconnectez vous ..."
    except jwt.DecodeError:
        return None,"Token invalide !"
    except Users.DoesNotExist:
        return None, "Utilisateur introuvable" 
    except Exception as e:
        return None,str(e)

class VenteView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        if user.role == 'admin':
            ventes = Vente.objects.all()
        else:
            ventes = Vente.objects.filter(lignes__annonce__vendeur=user).distinct()
        serializer = VenteSerializer(ventes,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user

        lignes_data = request.data.get('lignes',[])

        if not lignes_data:
            return Response({'error':'Aucune annonce enregistré dans la vente !'},status=status.HTTP_400_BAD_REQUEST)
        
        for ligne in lignes_data:
            annonce_code = ligne.get('annonce')
            quantite = int(ligne.get('quantite', 1))

            try:
                annonce = Annonce.objects.get(code = annonce_code)
            except Annonce.DoesNotExist:
                return Response({'error':f'Annonce {annonce_code} introuvable.'}, status=status.HTTP_404_NOT_FOUND)
            
            if annonce.vendeur == user:
                return Response({'error':f'Vous ne pouvez pas commander votre propre annonce : {annonce.titre}'},status=status.HTTP_403_FORBIDDEN)
            
            if quantite > annonce.qte:
                return Response({'error':f'la quantité commandé insuffisante pour {annonce.titre}, il en reste que {annonce.qte} disponible(s)'},status=status.HTTP_400_BAD_REQUEST)
            
        serializer = VenteSerializer(data=request.data)
        if serializer.is_valid():
            vente = serializer.save(acheteur = user)
            for ligne in vente.lignes.all():
                ligne.annonce.qte -= ligne.quantite
                ligne.annonce.save()
                return Response(VenteSerializer(vente).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VenteDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self,request,code):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        try:
            vente = Vente.objects.prefetch_related('lignes').get(code=code)
        except Vente.DoesNotExist:
            return Response(
                {"error":"Vente introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        if vente.acheteur != user:
            return Response(
                {"error":"Accès refusé"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = VenteDetailSerializer(vente)
        return Response(serializer.data,status=status.HTTP_200_OK)

class VentesVendeurView(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user

        ventes = Vente.objects.filter(
            lignes__annonce__vendeur=user
        ).distinct()

        result = []
        for vente in ventes:
            lignes = vente.lignes.filter(annonce__vendeur=user)
            result.append({
                "code":vente.code,
                "acheteur":vente.acheteur.id,
                "acheteur_nom":vente.acheteur.username,
                "status":vente.statut,
                "mode_paiement":vente.mode_paiement,
                "created_at":vente.created_at.isoformat(),
                "lignes":LigneDetailVenteSerializer(lignes,many=True).data
            })
        return Response(result,status=status.HTTP_200_OK)
    
class AchatUtilisateurView(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        ventes = Vente.objects.filter(acheteur=user).order_by('-created_at')
        serializer = VenteDetailSerializer(ventes,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    
class PanierView(APIView):
    def get(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        panier,_=Panier.objects.get_or_create(user=user)
        return Response(PanierSerializer(panier).data)
    
class PanierItemAddView(APIView):
    def post(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        panier,_ = Panier.objects.get_or_create(user=user)
        serializer = PanierItemSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        annonce = serializer.validated_data["annonce"]
        quantite = serializer.validated_data["quantite"]

        item,created = PanierItem.objects.get_or_create(
            panier = panier, annonce=annonce, defaults={"quantite":quantite}
        )
        if not created:
            return Response({"error":"Cette annonce est déjà dans le panier."},status=status.HTTP_400_BAD_REQUEST)

        return Response(PanierItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
class PanierItemDetailView(APIView):
    def patch(self, request, item_id):
        auth, error = verify(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        request.user = auth
        user = request.user
        try:
            panier = Panier.objects.get(user=user)
            item = PanierItem.objects.get(id=item_id, panier=panier)
        except (Panier.DoesNotExist, PanierItem.DoesNotExist):
            return Response({"error": "Introuvable"}, status=status.HTTP_404_NOT_FOUND)
        quantite = request.data.get("quantite")
        if not quantite or int(quantite) < 1:
            return Response({"error": "Quantité invalide !"}, status=status.HTTP_400_BAD_REQUEST)
        item.quantite = int(quantite)
        item.save()
        return Response(PanierItemSerializer(item).data)

    def delete(self, request, item_id):
        auth, error = verify(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        request.user = auth
        user = request.user
        try:
            panier = Panier.objects.get(user=user)
            item = PanierItem.objects.get(id=item_id, panier=panier)
        except (Panier.DoesNotExist, PanierItem.DoesNotExist):
            return Response({"error": "Introuvable"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message": "Article retiré du panier."}, status=status.HTTP_204_NO_CONTENT)

class PanierViderView(APIView):    
    def delete(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        try:
            user.panier.vider()
        except Panier.DoesNotExist:
            pass
        return Response({"message":"Panier vidé."})

class OrderListCreateView(APIView):
    def get(self,request):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        orders = Order.objects.filter(user=user).order_by("-created_at")
        return Response(OrderSerializer(orders,many=True).data)
  
    def post(self, request):
        auth, error = verify(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        request.user = auth
        user = request.user

        try:
            panier = user.panier
        except Panier.DoesNotExist:
            return Response({"error": "Panier Introuvable"}, status=status.HTTP_404_NOT_FOUND)

        items = panier.items.select_related("annonce").all()
        if not items.exists():
            return Response({"error": "Le panier est vide."}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.sous_total() for item in items)
        order = Order.objects.create(user=user, total=total)
        OrderItems.objects.bulk_create([
            OrderItems(
                order=order, annonce=item.annonce, titre=item.annonce.titre,
                prix=item.annonce.prix, quantite=item.quantite
            ) for item in items
        ])
        items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class OrderConfirmerView(APIView):
    def post(self,request,order_id):
        auth,error = verify(request)
        if error:
            return Response(
                {'error':error},
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.user = auth
        user = request.user
        order = get_object_or_404(Order,id=order_id,user=user)
        if order.statut == Order.Statut.ANNULEE:
            return Response({"error":"Commande annulée."},status=status.HTTP_400_BAD_REQUEST)
        order.confirmer()
        return Response(OrderSerializer(order).data)
    
class WebhookCinetPayView(APIView):
    def post(self, request):
        transaction_id = request.data.get('cpm_trans_id')
        statut_paiement = request.data.get('cpm_result')
        order = get_object_or_404(Order, id=transaction_id)
        if statut_paiement == "00":
            try:
                order.confirmer()
            except ValueError as e:
                order.statut = Order.Statut.ANNULEE
                order.save()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            order.statut = Order.Statut.ANNULEE
            order.save()
        return Response(status=status.HTTP_200_OK)         
        
