from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.utils import timezone

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=128, null=True, blank=True)
    telephone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(max_length=128, null=True, blank=True, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    photo_profil = models.ImageField(null=True, blank=True, upload_to="uploads/profils/")
    nom_boutique = models.CharField(max_length=128, null=True, blank=True)
    description_boutique = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True)

    class Meta:
        db_table = "users"
        ordering = ['-created_at']

class Categorie(models.Model):
    code =  models.CharField(primary_key=True,max_length=10)
    nom = models.CharField(max_length=100,null=False,blank=False)
    def save(self,*args,**kwargs):
        if not self.code:
            codes = Categorie.objects.filter(code__startswith='Cat_').values_list('code', flat=True)
            numbers = [int(c.replace('Cat_', '')) for c in codes if c.replace('Cat_', '').isdigit()]
            number = max(numbers) + 1 if numbers else 1
            self.code = f"Cat_{number}"
        super().save(*args,**kwargs)
    
    class Meta:
        db_table="categories"

class LowCategorie(models.Model):
    code =  models.CharField(primary_key=True,max_length=10)
    nom = models.CharField(max_length=100,null=False,blank=False)
    categorie = models.ForeignKey(Categorie,on_delete=models.CASCADE,related_name="sous_categories")
    def save(self,*args,**kwargs):
        if not self.code:
            codes = LowCategorie.objects.filter(code__startswith='S_C_').values_list('code', flat=True)
            numbers = [int(c.replace('S_C_', '')) for c in codes if c.replace('S_C_', '').isdigit()]
            number = max(numbers) + 1 if numbers else 1
            self.code = f"S_C_{number}"
        super().save(*args,**kwargs)
    
    class Meta:
        db_table="sous_categories"
        constraints=[
            models.UniqueConstraint(
                fields=['nom','categorie'],
                name='unique_sous_categorie_par_categorie'
            )
        ]

class Annonce(models.Model):
    code = models.CharField(primary_key=True,max_length=10)
    sous_categorie = models.ForeignKey(LowCategorie,on_delete=models.CASCADE,related_name='annonces')
    vendeur = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='annonces',null=False)
    titre = models.CharField(max_length=128,null=False,blank=False)
    description = models.TextField()
    prix = models.IntegerField(null=False,blank=False)
    qte = models.IntegerField(null=False,blank=False)
    statut = models.CharField(null=False,blank=False,max_length=64)
    localisation = models.CharField(max_length=256,null=False,blank=False)
    image = models.ImageField(null=False,blank=False,upload_to="uploads/annonces/")
    created_at = models.DateTimeField(auto_now_add=True,editable=False)

    def save(self,*args,**kwargs):
        if not self.code:
            last = Annonce.objects.all().order_by('code').last()
            if last:
                number = int(last.code.replace('A_',''))+1
            else:
                number = 1
            self.code = f"A_{number:0>7d}"
        super().save(*args,**kwargs)

    class Meta:
        db_table = "annonces"
        ordering=['-created_at']    

class ImageAnnonce(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(null=False,blank=False,upload_to="uploads/annonces/")
    produit = models.ForeignKey(Annonce,on_delete=models.CASCADE,related_name="images")

class Vente(models.Model):
    code = models.CharField(primary_key=True, max_length=17)
    acheteur = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='achats')
    prix_total = models.IntegerField(null=True,blank=True,default=0)
    statut = models.CharField(max_length=64,default='En attente')
    mode_paiement = models.CharField(max_length=64,blank=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)

    def save(self, *args, **kwargs):
        if not self.code:
            from datetime import datetime
            annee = datetime.now().year
            last = Vente.objects.filter(code__startswith=f"V-{annee}").order_by('code').last()
    
            if last:
                number = int(last.code.split('-')[2])+1
            else:
                number = 1
            self.code = f"V-{annee}-{number:0>9d}"
        
        super().save(*args,**kwargs)
    
    class Meta:
        db_table = "ventes"

class LigneVente(models.Model):
    id = models.AutoField(primary_key=True)
    vente = models.ForeignKey(Vente,on_delete=models.CASCADE,related_name='lignes')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='lignes_vente')
    quantite = models.IntegerField(null=False,blank=False)
    prix_unitaire = models.IntegerField(null=False,blank=False)

    def save(self,*args,**kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.annonce.prix
        super().save(*args,**kwargs)

        vente = self.vente
        vente.prix_total = sum(
            ligne.prix_unitaire * ligne.quantite
            for ligne in vente.lignes.all()
        )
        vente.save()

    class Meta:
        db_table = "lignes_vente"

class Panier(models.Model):
    user = models.OneToOneField(Users,on_delete=models.CASCADE,related_name="panier")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.sous_total() for item in self.items.all())
    
    def vider(self):
        self.items.all().delete()
    class Meta:
        db_table = "panier"

class PanierItem(models.Model):
    panier = models.ForeignKey(Panier,on_delete=models.CASCADE,related_name="items")
    annonce = models.ForeignKey(Annonce,on_delete=models.CASCADE,related_name="panier_items")
    quantite = models.PositiveIntegerField(default=1)
    add_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("panier","annonce")

    def sous_total(self):
        return self.annonce.prix * self.quantite
    
    class Meta:
        db_table = "panier_item"
    
class Order(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        CONFIRMEE = "confirmee", "Confirmé"
        ANNULEE = "annulee", "Annulée"
    class StatutPaiement(models.TextChoices):
        NON_PAYE = 'non_paye','Non payé'
        PAYE = 'paye','Payé'
        REMBOURSE = 'rembourse','Rembourse'
    user = models.ForeignKey(Users,on_delete=models.CASCADE,related_name="orders")
    statut = models.CharField(max_length=20,choices=Statut.choices, default=Statut.EN_ATTENTE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    confirme_le = models.DateTimeField(null=True,blank=True)
    statut_paiement = models.CharField(max_length=20,choices=StatutPaiement.choices, default=StatutPaiement.NON_PAYE)
    def confirmer(self):
        if self.statut == self.Statut.CONFIRMEE:
            return  # évite de re-décrémenter si le webhook est appelé 2x

        for item in self.items.select_related("annonce").all():
            annonce = item.annonce
            if annonce.qte < item.quantite:
                # stock insuffisant, on ne peut pas confirmer
                raise ValueError(f"Stock insuffisant pour {annonce.titre}")
            annonce.qte -= item.quantite
            annonce.save()

        self.statut = self.Statut.CONFIRMEE
        self.save()

    class Meta:
        db_table = "order"

class OrderItems(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    annonce = models.ForeignKey(Annonce,on_delete=models.SET_NULL,null=True,related_name="order_items")
    titre = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=12,decimal_places=2)
    quantite = models.PositiveIntegerField()

    def sous_total(self):
        return self.prix * self.quantite
    
    class Meta:
        db_table = "order_item"

class Favoris(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="favoris")
    annonce = models.ForeignKey(Annonce,on_delete=models.CASCADE,related_name='favoris')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "favoris"
        constraints = [
            models.UniqueConstraint(fields=['user','annonce'],name='unique_favoris')
        ]

class Livreur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Users,on_delete=models.CASCADE,related_name='profil_livreur')
    disponible = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=False)
    type_vehicule = models.CharField(max_length=32, null=True, blank=True)
    num_permis = models.CharField(max_length=64, null=True, blank=True)
    num_plaque = models.CharField(max_length=32, null=True, blank=True)

class TrajetLivreur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE, related_name='trajets')
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    tarif = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)

STATUS_LIVRAISON = [
    ('en_attente_selection', 'En attente sélection livreur'),
    ('en_attente_acceptation','EN attente acceptation livreur'),
    ('acceptee','Acceptée'),
    ('refusee','Refusée'),
    ('en_cours','En cours de livraison'),
    ('livree_attente_confirmation','Livrée - attente confirmation client'),
    ('confirmee','Confirmée'),
    ('annulee','Annulée')
]

class Livraison:
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order,on_delete=models.CASCADE,related_name='livraison')
    livreur = models.ForeignKey(Livreur,on_delete=models.SET_NULL,null=True,blank=True)
    ville_depart = models.CharField(max_length=100)
    ville_livraison = models.CharField(max_length=100)
    statut = models.CharField(max_length=30, choices=STATUS_LIVRAISON, default='en_attente_selection')
    date_acceptation = models.DateTimeField(null=True,blank=True)
    date_livraison = models.DateTimeField(null=True,blank=True)
    date_confirmation = models.DateTimeField(null=True,blank=True)
    created_at =models.DateTimeField(auto_now_add=True)

TYPE_TRANSACTION = [('paiement', 'Paiement'), ('remboursement', 'Remboursement')]
STATUT_TRANSACTION = [('en_attente', 'En attente'), ('reussi', 'Réussi'), ('echoue', 'Échoué')]

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=20, choices=TYPE_TRANSACTION)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    operateur = models.CharField(max_length=20, blank=True)  # 'OM', 'MOMO'...
    numero_telephone = models.CharField(max_length=20, blank=True)
    cinetpay_transaction_id = models.CharField(max_length=100, unique=True)  # notre ID envoyé à CinetPay
    payment_token = models.CharField(max_length=255, blank=True)  # retourné par CinetPay (paiement uniquement)
    statut = models.CharField(max_length=20, choices=STATUT_TRANSACTION, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"{self.type_transaction} - {self.cinetpay_transaction_id} - {self.statut}"

