from rest_framework import serializers
from .models import Users,Categorie, LowCategorie, ImageAnnonce, Annonce

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
        read_only_fields = ['id','created_at']

class CategorieSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    class Meta:
        model = Categorie
        fields = '__all__'

class LowCategorieSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    class Meta:
        model = LowCategorie
        fields = '__all__'

class ImagesAnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAnnonce
        fields = '__all__'

class AnnonceSerializer(serializers.ModelSerializer):
    images = ImagesAnnonceSerializer(many=True,read_only=True)
    class Meta:
        model = Annonce
        fields = '__all__'


