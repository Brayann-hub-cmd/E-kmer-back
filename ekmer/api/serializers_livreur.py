from rest_framework import serializers
from .models import TrajetLivreur, Livreur, Livraison

# serializers.py
class TrajetLivreurSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrajetLivreur
        fields = ['id', 'ville_depart', 'ville_arrivee', 'tarif', 'actif']
        read_only_fields = ['id']

class LivreurSerializer(serializers.ModelSerializer):
    trajets = TrajetLivreurSerializer(many=True, read_only=True)
    nom_complet = serializers.SerializerMethodField()
    telephone = serializers.CharField(source='user.telephone', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.ImageField(source='user.photo_profil', read_only=True)

    class Meta:
        model = Livreur
        fields = [
            'id', 'nom_complet', 'telephone', 'email', 'avatar', 'disponible',
            'is_validated', 'type_vehicule', 'num_permis', 'num_plaque',
            'trajets',
        ]
        read_only_fields = ['id']

    def get_nom_complet(self, obj):
        return obj.user.username

class LivreurDisponibleSerializer(serializers.ModelSerializer):
    nom_complet = serializers.SerializerMethodField()
    trajets = TrajetLivreurSerializer(many=True, read_only=True)

    class Meta:
        model = Livreur
        fields = ['id', 'nom_complet', 'disponible', 'trajets']

    def get_nom_complet(self, obj):
        return obj.user.username