from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
class Users(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=128,null=True,blank=True)
    telephone = models.CharField(max_length=13,null=True,blank=True)
    email = models.EmailField(max_length=128,null=True,blank=True,unique=True)
    password = models.CharField(max_length=128,null=True,blank=True)
    role = models.CharField(max_length=64,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,editable=False,null=True)

    class Meta:
        db_table="users"
        ordering=['-created_at']

class Categorie(models.Model):
    code =  models.CharField(primary_key=True,max_length=10)
    nom = models.CharField(max_length=100,null=False,blank=False)
    def save(self,*args,**kwargs):
        if not self.code:
            last = Categorie.objects.all().order_by('code').last()
            if last:
                number = int(last.code.replace('Cat_','')) + 1
            else:
                number = 1
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
            last = LowCategorie.objects.all().order_by('code').last()
            if last:
                number = int(last.code.replace('S_C_','')) + 1
            else:
                number = 1
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

class Livreur(models.Model):
    idLivreur = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)

    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('occupe', 'Occupé'),
        ('offline', 'Hors ligne'),
    ]

    VEHICULE_CHOICES = [
        ('moto', 'Moto'),
        ('voiture', 'Voiture'),
        ('velo', 'Vélo'),
        ('camion', 'Camion'),
    ]

    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='livreur'
    )

    telephone = models.CharField(max_length=20, unique=True)
    numero_permis = models.CharField(max_length=50, blank=True, null=True)
    type_vehicule = models.CharField(max_length=20, choices=VEHICULE_CHOICES)
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='offline')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "livreurs"    
    
    def __str__(self):
        return f"{self.user.username} - {self.type_vehicule}"

class Vente(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    acheteur = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='achats')
    prix_total = models.IntegerField(null=False,blank=False)
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
            self.code = f"V-{annee}-{number:0>10d}"
        if not self.prix_total:
            self.prix_total = self.quantite * self.annonce.prix
        super().save(*args,**kwargs)
    
    class Meta:
        db_table = "ventes"

class LigneVente(models.Model):
    id = models.AutoField(primary_key=True)
    vente = models.ForeignKey(Vente,on_delete=models.CASCADE,related_name='lignes')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='lignes_vente')
    quantite = models.IntegerField(null=False,blank=False)
    prix_unitaire = models.IntegerField(null=False,blank=False)

    class Meta:
        db_table = "lignes_vente"


class Consultation(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    date_consultation = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "consultations"
        ordering = ['-date_consultation']
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'annonce'],
                name='unique_consultation_par_client_annonce'
            )
        ]

    def __str__(self):
        return f"{self.client.username} → {self.annonce.titre}"