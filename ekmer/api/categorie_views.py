from .models import Categorie,LowCategorie
from rest_framework import viewsets,status
from .serializers import CategorieSerializer,LowCategorieSerializer
from rest_framework.permissions import AllowAny
from .permissions import IsAdminRole,IsUserRole
from rest_framework.views import APIView
from rest_framework.response import Response
class CategorieViewSet(viewsets.ModelViewSet):

    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        return [IsAdminRole()]

class LowCategorieViewSet(viewsets.ModelViewSet):
    queryset = LowCategorie.objects.all()
    serializer_class = LowCategorieSerializer
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        return [IsAdminRole()]

class SousCategorieParCategorieView(APIView):
    def get(self, request, categorie_code):
        if not Categorie.objects.filter(code=categorie_code).exists():
            return Response(
                {"error":"Catégorie introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        sous_categories = LowCategorie.objects.filter(categorie=categorie_code)
        serializer = LowCategorieSerializer(sous_categories,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    