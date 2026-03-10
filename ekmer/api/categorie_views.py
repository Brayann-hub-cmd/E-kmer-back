from .models import Categorie,LowCategorie
from rest_framework import viewsets
from .serializers import CategorieSerializer,LowCategorieSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRole,IsUserRole

class CategorieViewSet(viewsets.ModelViewSet):

    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminRole]

class LowCategorieViewSet(viewsets.ModelViewSet):
    queryset = LowCategorie.objects.all()
    serializer_class = LowCategorieSerializer
    permission_classes = [IsAdminRole]