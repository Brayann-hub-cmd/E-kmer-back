from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers_livreur import LivreurDisponibleSerializer,LivreurSerializer
from .models import Livreur
from .views import verifier_token
class LivreurListView(APIView):
    def get(self, request):
        ville_arrivee = request.query_params.get('ville_arrivee')

        livreurs = Livreur.objects.filter(disponible=True).select_related('user').prefetch_related('trajets')

        if ville_arrivee:
            livreurs = livreurs.filter(
                trajets__ville_arrivee__iexact=ville_arrivee,
                trajets__actif=True
            ).distinct()

        serializer = LivreurDisponibleSerializer(livreurs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LivreurValiderView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        if user.role != "admin":
            return Response({"error": "Accès réservé aux administrateurs"}, status=status.HTTP_403_FORBIDDEN)
        try:
            livreur = Livreur.objects.get(id=id)
        except Livreur.DoesNotExist:
            return Response({"error": "Livreur introuvable"}, status=status.HTTP_404_NOT_FOUND)
        livreur.is_validated = True
        livreur.save()
        return Response(LivreurSerializer(livreur).data, status=status.HTTP_200_OK)

class LivreurUpdateView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        if user.role != "admin":
            return Response({"error": "Accès réservé aux administrateurs"}, status=status.HTTP_403_FORBIDDEN)
        try:
            livreur = Livreur.objects.get(id=id)
        except Livreur.DoesNotExist:
            return Response({"error": "Livreur introuvable"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LivreurSerializer(livreur, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)    
