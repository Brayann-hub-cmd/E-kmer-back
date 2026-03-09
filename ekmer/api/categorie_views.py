from .models import Categorie
from rest_framework import viewsets
from .serializers import CategorieSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRole

class CategorieViewSet(viewsets.ModelViewSet):

    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminRole]