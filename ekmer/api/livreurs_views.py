from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers_livreur import LivreurDisponibleSerializer,LivreurSerializer,TrajetLivreurSerializer
from .models import Livreur,TrajetLivreur,Users
from .views import verifier_token
from django.shortcuts import get_object_or_404
import jwt
import datetime
from django.conf import settings
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

class LivreurMeView(APIView):
    def get(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        return Response(LivreurSerializer(livreur).data)

    def patch(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        serializer = LivreurSerializer(livreur, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TrajetLivreurListCreateView(APIView):
    def get(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        return Response(TrajetLivreurSerializer(livreur.trajets.all(), many=True).data)

    def post(self, request):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        serializer = TrajetLivreurSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(livreur=livreur)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TrajetLivreurDetailView(APIView):
    def patch(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        trajet = get_object_or_404(TrajetLivreur, id=id, livreur=livreur)
        serializer = TrajetLivreurSerializer(trajet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        user, erreur = verifier_token(request)
        if erreur:
            return Response({"error": erreur}, status=status.HTTP_401_UNAUTHORIZED)
        livreur = get_object_or_404(Livreur, user=user)
        trajet = get_object_or_404(TrajetLivreur, id=id, livreur=livreur)
        trajet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LivreurLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({"error": "Email ou mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        if user.password != password:
            return Response({"error": "Email ou mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        if user.role != 'livreur':
            return Response({"error": "Ce compte n'est pas un compte livreur"}, status=status.HTTP_403_FORBIDDEN)

        token = jwt.encode(
            {'id': str(user.id), 'email': user.email, 'role': user.role,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
            settings.SECRET_KEY, algorithm='HS256'
        )
        return Response({
            "token": token,
            "user": {"id": str(user.id), "email": user.email, "username": user.username,
                      "telephone": user.telephone, "role": user.role, "is_active": user.is_active}
        })

class LivreurRegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username')
        telephone = request.data.get('telephone')

        if not all([email, password, username, telephone]):
            return Response({"error": "Email, mot de passe, nom et téléphone sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)
        if Users.objects.filter(email=email).exists():
            return Response({"error": "Un utilisateur utilise déjà cet email."}, status=status.HTTP_400_BAD_REQUEST)
        if Users.objects.filter(telephone=telephone).exists():
            return Response({"error": "Un utilisateur utilise déjà ce numéro."}, status=status.HTTP_400_BAD_REQUEST)

        user = Users.objects.create(
            username=username, telephone=telephone, email=email,
            password=password, role='livreur',
        )
        Livreur.objects.create(
            user=user,
            type_vehicule=request.data.get('type_vehicule', ''),
            num_permis=request.data.get('num_permis', ''),
            num_plaque=request.data.get('num_plaque', ''),
        )
        return Response(
            {"message": "Compte créé."},
            status=status.HTTP_201_CREATED
        )

