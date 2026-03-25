from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import Annonce,Users,LowCategorie
from .serializers import AnnonceSerializer
from .permissions import AnnoncePermission
from .views import verifier_token
from .serializers import AnnonceSerializer
class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [AnnoncePermission]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        payload, erreur = verifier_token(request)
        if erreur:
            return Response({"error":erreur},status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Users.objects.get(id=payload['id'])
        except Users.DoesNotExist:
            return Response({"error":"Utilisateur introuvable"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendeur=user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class AnnonceParSousCategorie(APIView):
    def get(self, request, low_categorie_code):
        if not LowCategorie.objects.filter(code=low_categorie_code).exists():
            return Response(
                {"error":"Sous catégorie introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        annonces = Annonce.objects.filter(sous_categorie=low_categorie_code)
        serializer = AnnonceSerializer(annonces,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)