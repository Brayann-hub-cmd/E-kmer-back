# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Annonce, Consultation
from django.utils import timezone

@api_view(['POST'])
@permission_classes([AllowAny])
def enregistrer_consultation(request, code_annonce):
    try:
        annonce = Annonce.objects.get(code=code_annonce)
    except Annonce.DoesNotExist:
        return Response(
            {"error": "Annonce non trouvée"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si l'utilisateur a déjà consulté cette annonce aujourd'hui
    aujourd_hui = timezone.now().date()
    consultation_existante = Consultation.objects.filter(
        annonce=annonce,
        utilisateur=request.user if request.user.is_authenticated else None,
        consulted_at__date=aujourd_hui
    ).exists()
    
    if consultation_existante:
        return Response(
            {"message": "Déjà consulté aujourd'hui"},
            status=status.HTTP_200_OK
        )
    
    consultation = Consultation.objects.create(
        annonce=annonce,
        utilisateur=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response(
        {"message": "Consultation enregistrée", "consultation_id": consultation.id},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def nombre_consultations(request, code_annonce):
    
    try:
        annonce = Annonce.objects.get(code=code_annonce)
    except Annonce.DoesNotExist:
        return Response(
            {"error": "Annonce non trouvée"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    nombre_consultations = Consultation.objects.filter(annonce=annonce).count()
    
    return Response({
        "code_annonce": code_annonce,
        "titre": annonce.titre,
        "nombre_consultations": nombre_consultations
    })
