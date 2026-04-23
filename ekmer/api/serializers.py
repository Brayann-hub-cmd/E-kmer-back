from rest_framework import serializers
from .models import Livreur, Users,Categorie, LowCategorie, ImageAnnonce, Annonce, Vente, LigneVente

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
    def get_image(self,obj):
        if obj.image:
            return f"/media/annonces/{obj.image.name.split('/')[-1]}"
        return None

class LivreurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livreur
        fields = '__all__'

class LigneVenteSerializer(serializers.ModelSerializer):
    annonce_titre = serializers.CharField(source='annonce.titre',read_only=True)
    prix_unitaire = serializers.IntegerField(read_only=True)
    # vendeur_nom = serializers.CharField(source='annonce.vendeur.username',read_only=True)
    class Meta:
        model = LigneVente
        fields = [
            'id',
            'annonce',
            'annonce_titre',
            'quantite',
            'prix_unitaire',
        ]

class VenteSerializer(serializers.ModelSerializer):
    lignes = LigneVenteSerializer(many=True)
    acheteur_nom = serializers.CharField(source='acheteur.username',read_only=True)

    class Meta:
        model = Vente
        fields = [
            'code',
            'acheteur',
            'acheteur_nom',
            'lignes',
            'statut',
            'prix_total',
            'created_at'
        ]
        read_only_fields = ['code','prix_total','acheteur','created_at']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')
        vente = Vente.objects.create(**validated_data)
        prix_total = 0
        for ligne in lignes_data:
            annonce = ligne['annonce']
            quantite = ligne['quantite']
            prix_unitaire = annonce.prix

            LigneVente.objects.create(
                vente = vente,
                annonce = annonce,
                quantite = quantite,
                prix_unitaire = prix_unitaire
            )

            prix_total += prix_unitaire * quantite
        vente.prix_total = prix_total
        vente.save()
        return vente