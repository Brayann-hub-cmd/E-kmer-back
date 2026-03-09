import jwt
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from .models import Users

SECRET_KEY = "SECRET_KEY"

class IsAdminRole(BasePermission):

    def has_permission(self, request, view):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise AuthenticationFailed("Token manquant")
        
        try:
            parts = auth_header.split(" ")

            if len(parts) == 2:
                token = parts[1]
            else:
                token = parts[0]

        except IndexError:
            raise AuthenticationFailed("Format du token invalide")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expiré")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token invalide")

        user_id = payload.get("id")

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            raise AuthenticationFailed("Utilisateur introuvable")

        # on attache l'utilisateur à la requête
        request.user = user

        if user.role == "admin":
            return True

        return False