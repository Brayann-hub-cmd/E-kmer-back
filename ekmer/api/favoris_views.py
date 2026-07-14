from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FavorisSerializer
from .models import Favoris,Annonce
from .vente_views import verify
class FavorisView(APIView):

    def get(self,request):
        user,error = verify(request)
        if error:
            return Response({"error":error},status=status.HTTP_401_UNAUTHORIZED)
        favoris = Favoris.objects.filter(user=user)
        serializer = FavorisSerializer(favoris,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        user,error = verify(request)
        if error:
            return Response({"error":error},status=status.HTTP_401_UNAUTHORIZED)
        annonce_code = request.data.get('annonce')
        if not annonce_code:
            return Response({"error":"Annonce réquis"},status=status.HTTP_400_BAD_REQUEST)
        try:
            annonce = Annonce.objects.get(code=annonce_code)
        except Annonce.DoesNotExist:
            return Response({"error":"Annonce introuvable"},status=status.HTTP_404_NOT_FOUND)
        favori,created = Favoris.objects.get_or_create(user=user,annonce=annonce)
        if not created:
            return Response({"message":"Déjà en favoris"},status=status.HTTP_200_OK)
        serializer = FavorisSerializer(favori)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self,request,annonce_code):
        user,error = verify(request)
        if error:
            return Response({"error":error},status=status.HTTP_401_UNAUTHORIZED)
        
        deleted, _ = Favoris.objects.filter(user=user,annonce__code=annonce_code).delete()
        if deleted == 0:
            return Response({"error":"Favoris introuvable."},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Rétiré des favoris"},status=status.HTTP_204_NO_CONTENT)