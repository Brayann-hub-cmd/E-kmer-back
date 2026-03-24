from rest_framework import serializers
from .models import Livreur, Users,Categorie, LowCategorie, ImageAnnonce, Annonce

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
    code = serializers.CharField(read_only=True)
    images = ImagesAnnonceSerializer(many=True,read_only=True)
    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    vendeur = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Annonce
        fields = '__all__'
        read_only_fields = ['code','created_at']
    def create(self, validated_data):
        image_data = validated_data.pop('images_upload', [])
        annonce = Annonce.objects.create(**validated_data)

        for image in image_data:
            ImageAnnonce.objects.create(produit=annonce,image=image)

        return annonce


class LivreurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livreur
        fields = '__all__'