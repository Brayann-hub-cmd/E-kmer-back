from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers_livreur import LivreurDisponibleSerializer
from .models import Livreur
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