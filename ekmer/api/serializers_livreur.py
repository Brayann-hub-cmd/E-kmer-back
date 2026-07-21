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

    class Meta:
        model = Livreur
        fields = ['id', 'nom_complet', 'telephone', 'disponible', 'trajets']
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