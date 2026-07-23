from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import Annonce,Users,LowCategorie
from .serializers import AnnonceSerializer
from .permissions import AnnoncePermission
from .views import verifier_token
from .serializers import AnnonceSerializer
import jwt
from django.conf import settings
from rest_framework.permissions import AllowAny

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

class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [AnnoncePermission]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendeur=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class AllAnnonces(APIView):
    def get(self, request):
        annonces = Annonce.objects.select_related('sous_categorie__categorie', 'vendeur').all()
        serializer = AnnonceSerializer(annonces, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AnnonceParSousCategorie(APIView):
    def get(self, request, low_categorie_code):
        if not LowCategorie.objects.filter(code=low_categorie_code).exists():
            return Response(
                {"error":"Sous catégorie introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        annonces = Annonce.objects.filter(sous_categorie=low_categorie_code)
        serializer = AnnonceSerializer(annonces,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RechercherAnnonce(APIView):
    permission_classes = []
    def get(self,request):
        titre = request.query_params.get('titre', '').strip()
        categorie_id = request.query_params.get('categorie', None)

        if not titre:
            return Response(
                {'error':'Le champ de recherche d\'un produit est requis! veuillez le remplir'},
                status=status.HTTP_400_BAD_REQUEST
            )
        annonces = Annonce.objects.filter(titre__icontains=titre)
        if categorie_id:
            annonces = annonces.filter(sous_categorie__categorie__code=categorie_id)
        serializer = AnnonceSerializer(annonces,many=True,context={'request':request})
        return Response(serializer.data,status=status.HTTP_200_OK)

class AnnonceByUser(APIView):
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
        annonces = Annonce.objects.filter(vendeur=user)
        serializer = AnnonceSerializer(annonces,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class SuspendreAnnonceView(APIView):
    def patch(self, request, code):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != "admin":
            return Response(
                {"error": "Accès réservé aux administrateurs"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            annonce = Annonce.objects.get(code=code)
        except Annonce.DoesNotExist:
            return Response({"error": "Annonce introuvable"}, status=status.HTTP_404_NOT_FOUND)

        nouveau_statut = request.data.get("statut")
        statuts_valides = ["Disponible", "Suspendu"]
        if nouveau_statut not in statuts_valides:
            return Response(
                {"error": f"Statut invalide. Valeurs acceptées : {', '.join(statuts_valides)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        annonce.statut = nouveau_statut
        annonce.save()
        serializer = AnnonceSerializer(annonce, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)