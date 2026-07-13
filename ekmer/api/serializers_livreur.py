from rest_framework import serializers
from .models import TrajetLivreur, Livreur, Livraison


class TrajetLivreurSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrajetLivreur
        fields = ['id', 'ville_depart', 'ville_arrivee', 'actif']
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
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class LivreurDisponibleSerializer(serializers.ModelSerializer):
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Livreur
        fields = ['id', 'nom_complet', 'disponible']

    def get_nom_complet(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()