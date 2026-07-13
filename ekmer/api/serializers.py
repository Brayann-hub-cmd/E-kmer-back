from rest_framework import serializers
from .models import Livreur, Users,Categorie, LowCategorie, ImageAnnonce, Annonce, Vente, LigneVente,PanierItem,Panier,OrderItems,Order,Favoris,Livraison,Transaction
from .utils import verifier_token
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

class VendeurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','username','created_at']

class AnnonceSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    images = ImagesAnnonceSerializer(many=True,read_only=True)
    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    vendeur = VendeurSerializer(read_only=True)
    est_favori = serializers.SerializerMethodField()
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
    
    def get_est_favori(self,obj):
        request = self.context.get('request')
        if not request:
            return False
        user, error = verifier_token(request)
        if error or not user:
            return False
        return Favoris.objects.filter(user=user,annonce=obj).exists()

class LivreurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livreur
        fields = '__all__'

class LigneVenteSerializer(serializers.ModelSerializer):
    annonce_titre = serializers.CharField(source='annonce.titre',read_only=True)
    prix_unitaire = serializers.IntegerField(read_only=True)
    class Meta:
        model = LigneVente
        fields = [
            'id',
            'annonce',
            'annonce_titre',
            'quantite',
            'prix_unitaire',
        ]

class LigneDetailVenteSerializer(serializers.ModelSerializer):
    annonce_titre = serializers.CharField(source='annonce.titre',read_only=True)
    annonce_image = serializers.ImageField(source='annonce.image',read_only=True)
    annonce_qte = serializers.IntegerField(source='annonce.qte',read_only=True)
    prix_unitaire = serializers.IntegerField(read_only=True)
    class Meta:
        model = LigneVente
        fields = [
            'id',
            'annonce',
            'annonce_titre',
            'annonce_image',
            'annonce_qte',
            'quantite',
            'prix_unitaire',
        ]

class VenteDetailSerializer(serializers.ModelSerializer):
    lignes = LigneVenteSerializer(many=True,read_only=True)

    class Meta:
        model=Vente
        fields = [
            'code','acheteur','prix_total','statut','mode_paiement','created_at','lignes'
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
            'created_at',
            'mode_paiement'
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
    
class PanierItemSerializer(serializers.ModelSerializer):
    annonce_titre = serializers.CharField(source="annonce.titre", read_only=True)
    annonce_prix = serializers.DecimalField(source="annonce.prix", max_digits=12, decimal_places=2,read_only=True)
    sous_total = serializers.SerializerMethodField()
    annonce_image= serializers.ImageField(source="annonce.image",read_only=True)
    annonce_vendeur = serializers.CharField(source="annonce.vendeur.username",read_only=True)
    class Meta:
        model = PanierItem
        fields = ["id","annonce","annonce_titre","annonce_prix","annonce_image","annonce_vendeur","sous_total","quantite","add_at"]
        read_only_fields = ["id","add_at"]

    def get_sous_total(self,obj):
        return obj.annonce.prix * obj.quantite
        
    def validate_quantite(self,value):
        if value < 1:
            raise serializers.ValidationError("La quantité doit être 1 au moins !")
        return value
        
class PanierSerializer(serializers.ModelSerializer):
    items = PanierItemSerializer(many=True,read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ["id","user","items","total","created_at","update_at"]
        read_only_fields = fields
    
    def get_total(self,obj):
        return obj.total()

class OrderItemSerializer(serializers.ModelSerializer):
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = ["id","annonce","titre","prix","quantite","sous_total"]
        read_only_fields = fields

    def get_sous_total(self,obj):
        return obj.sous_total()

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)

    class Meta:
        model = Order
        fields =["id","user","statut","total","items","created_at","confirme_le"]
        read_only_fields = ["id","user","total","items","created_at","confirme_le"]

class FavorisSerializer(serializers.ModelSerializer):
    annonce_titre = serializers.CharField(source='annonce.titre', read_only=True)
    annonce_prix = serializers.IntegerField(source='annonce.prix', read_only=True)
    annonce_image = serializers.ImageField(source='annonce.image', read_only=True)
    class Meta:
        model = Favoris
        fields = ['id','user','annonce','annonce_titre','annonce_prix','annonce_image','created_at']
        read_only_fields = ['user','created_at']

class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['photo_profil']

from .serializers_livreur import LivreurSerializer

class LivraisonSerializer(serializers.ModelSerializer):
    livreur = LivreurSerializer(read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    montant_commande = serializers.DecimalField(
        source='order.montant_total', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Livraison
        fields = [
            'id', 'order_id', 'montant_commande', 'livreur',
            'ville_depart', 'ville_livraison',
            'statut', 'statut_display',
            'date_acceptation', 'date_livraison', 'date_confirmation',
            'created_at',
        ]
        read_only_fields = fields

class LivraisonCreateSerializer(serializers.ModelSerializer):
    livreur_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Livraison
        fields = ['order', 'livreur_id', 'ville_livraison']

    def validate_order(self, order):
        if hasattr(order, 'livraison'):
            raise serializers.ValidationError("Une livraison existe déjà pour cette commande.")
        if order.statut_paiement != 'paye':
            raise serializers.ValidationError("La commande doit être payée avant de choisir un livreur.")
        return order

    def validate(self, data):
        from .models import Livreur, TrajetLivreur
        livreur_id = data.get('livreur_id')
        ville_livraison = data.get('ville_livraison')
        try:
            livreur = Livreur.objects.get(id=livreur_id, disponible=True)
        except Livreur.DoesNotExist:
            raise serializers.ValidationError({"livreur_id": "Livreur introuvable ou indisponible."})

        # ville_depart calculée dans la vue et injectée dans validated_data avant save()
        ville_depart = data.get('ville_depart')
        trajet_existe = TrajetLivreur.objects.filter(
            livreur=livreur, ville_depart=ville_depart,
            ville_arrivee=ville_livraison, actif=True
        ).exists()
        if not trajet_existe:
            raise serializers.ValidationError(
                "Ce livreur ne dessert pas ce trajet."
            )
        data['livreur'] = livreur
        data.pop('livreur_id')
        return data

    def create(self, validated_data):
        validated_data['statut'] = 'en_attente_acceptation'
        return Livraison.objects.create(**validated_data)

class LivraisonReponseLivreurSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accepter', 'refuser'])

    def validate(self, data):
        livraison = self.instance
        if livraison.statut != 'en_attente_acceptation':
            raise serializers.ValidationError(
                "Cette livraison n'est plus en attente d'acceptation."
            )
        return data

    def save(self, **kwargs):
        from django.utils import timezone
        livraison = self.instance
        if self.validated_data['action'] == 'accepter':
            livraison.statut = 'acceptee'
            livraison.date_acceptation = timezone.now()
        else:
            livraison.statut = 'refusee'
            livraison.order.statut = 'annulee'
            livraison.order.save()
        livraison.save()
        return livraison

class LivraisonMarquerLivreeSerializer(serializers.Serializer):
    def validate(self, data):
        if self.instance.statut != 'acceptee':
            raise serializers.ValidationError("La livraison doit être acceptée avant d'être marquée livrée.")
        return data

    def save(self, **kwargs):
        from django.utils import timezone
        livraison = self.instance
        livraison.statut = 'livree_attente_confirmation'
        livraison.date_livraison = timezone.now()
        livraison.save()
        return livraison

class LivraisonConfirmationClientSerializer(serializers.Serializer):
    def validate(self, data):
        if self.instance.statut != 'livree_attente_confirmation':
            raise serializers.ValidationError("Aucune livraison en attente de confirmation.")
        return data

    def save(self, **kwargs):
        from django.utils import timezone
        livraison = self.instance
        livraison.statut = 'confirmee'
        livraison.date_confirmation = timezone.now()
        livraison.save()
        livraison.order.statut = 'confirmee'
        livraison.order.save()
        return livraison
    
class TransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_transaction_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
 
    class Meta:
        model = Transaction
        fields = [
            'id', 'order', 'type_transaction', 'type_display',
            'montant', 'operateur', 'numero_telephone',
            'statut', 'statut_display', 'created_at',
        ]
        read_only_fields = fields