from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import Annonce,Users
from .serializers import AnnonceSerializer
from .permissions import AnnoncePermission
from .views import verifier_token
class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [AnnoncePermission]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        payload, erreur = verifier_token(request)
        if erreur:
            return self.response({"error":erreur},status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = Users.objects.get(id=payload['id'])
        except Users.DoesNotExist:
            return Response({"error":"Utilisateur introuvable"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendeur=user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)