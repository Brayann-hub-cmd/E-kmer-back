from .models import Categorie,LowCategorie
from rest_framework import viewsets
from .serializers import CategorieSerializer,LowCategorieSerializer
from rest_framework.permissions import AllowAny
from .permissions import IsAdminRole,IsUserRole

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
