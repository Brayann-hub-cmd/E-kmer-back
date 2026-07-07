from django.shortcuts import render
from rest_framework import viewsets
from .models import Users
from .serializers import UserSerializer,ProfilePhotoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
import datetime
from django.conf import settings
class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field='id'

class LoginWithEmailAndPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password') 

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response(
                {"error":"Email ou mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if user.password!=password:
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
            }, settings.SECRET_KEY,algorithm='HS256'
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

class LoginWithPhoneAndPasswordView(APIView):
    def post(self,request):
        phone = request.data.get('telephone')
        password = request.data.get('password') 

        try:
            user = Users.objects.get(telephone=phone)
        except Users.DoesNotExist:
            return Response(
                {"error":"Téléphone ou mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if user.password!=password:
            return Response(
                {"error":"Téléphone ou mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token = jwt.encode(
            {
                'id':str(user.id),
                'email':user.email,
                'role':user.role,
                'exp':datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, settings.SECRET_KEY,algorithm='HS256'
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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None,"Token Manquant,connectez vous!"
    if not auth_header.startswith('Bearer '):
        return None, "Format du token invalide"
    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        request.user = Users.objects.get(id=payload['id'])
        return payload,None
    except Exception as e:
        return None,str(e)
    except jwt.ExpiredSignatureError:
        return None,"Token expiré, reconnectez vous ..."
    except jwt.DecodeError:
        return None,"Token invalide !"
    except Users.DoesNotExist:
        return None, "Utilisateur introuvable"
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
        except Users.DoesNotExist:
            return Response(
                {"error":"Utiliateur introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
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

        if not email:
            return Response(
                {"error":"L'adresse mail est un champ obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {"error":"Le mot de passe est des champ obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not telephone:
            return Response(
                {"error":"Le numéro de télephone est un champ obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not username:
            return Response(
                {"error":"Le nom d'utilisateur est un champ obligatoire."},
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
        
class ProfilePhotoView(APIView):
    def patch(self,request):
        user, error = verifier_token(request)
        if error:
            return Response({"error":error},status=status.HTTP_401_UNAUTHORIZED)
        serializer = ProfilePhotoSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    