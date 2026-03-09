from django.shortcuts import render
from rest_framework import viewsets
from .models import Users
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
import datetime
class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field='id'

class LoginWithEmailAndPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password') 

        try:
            user = Users.objects.get(email=email,password=password)
        except Users.DoesNotExist:
            return Response(
                {"error":"Email ou mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = jwt.encode(
            {
                'id':str(user.id),
                'email':user.email,
                'role':user.role,
                'exp':datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, 'SECRET_KEY',algorithm='HS256'
        )
        return Response({
            "token":token,
            "user":{
                "id": str(user.id),
                "email":user.email,
                "username":user.username,
                "telephone":user.telephone,
                "role": user.role,
                "is_active":user.is_active
            }
        })
    
def verifier_token(request):
    token = request.headers.get('Authorization')
    if not token:
        return None,"Token Manquant"
    try:
        payload = jwt.decode(token,'SECRET_KEY',algorithms=['HS256'])
        return payload,None
    except jwt.ExpiredSignatureError:
        return None,"Token expiré, reconnectez vous ..."
    except jwt.DecodeError:
        return None,"Token invalide !"

class ProfileView(APIView):
    def get(self,request):
        payload,erreur = verifier_token(request=request)
        if erreur:
            return Response(
                {"error":erreur},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = Users.objects.get(id=payload['id'])
        except jwt.ExpiredSignatureError:
            return Response({"error":"Token expiré..."})
        except jwt.DecodeError:
            return Response({"error":"Token invalide..."})
        
        return Response({
            "id": str(user.id),
            "email":user.email,
            "username":user.username,
            "telephone":user.telephone,
            "role":user.role
        })

class SignInWithEmailAndPassword(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username')
        telephone = request.data.get('telephone')
        role = request.data.get('role','user')

        if not email or not password or not telephone or not username:
            return Response(
                {"error":"l'adresse mail, le mot de passe, le numéro de télephone et le nom d'utilisateur sont des champs obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Users.objects.filter(email=email).exists():
            return Response({
                "error":"Un utilisateur utilise déjà cet adresse email."
            },status=status.HTTP_400_BAD_REQUEST)
        
        if Users.objects.filter(telephone=telephone).exists():
            return Response({
                "error":"Un utilisateur utilise déjà ce numéro de téléphone."
            },status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Users.objects.create(
                username = username,
                telephone = telephone,
                email = email,
                password = password,
                role = role,
            )
            return Response(
                {
                    "message":"Compte crée avec succès",
                    "user":{
                        "id":user.id,
                        "username":user.username,
                        "email":user.email,
                        "telephone":user.telephone
                    }
                },status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
