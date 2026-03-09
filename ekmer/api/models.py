from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
class Users(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=128,null=True,blank=True)
    telephone = models.CharField(max_length=13,null=True,blank=True)
    email = models.EmailField(max_length=128,null=True,blank=True,unique=True)
    password = models.CharField(max_length=16,null=True,blank=True)
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

class ImageAnnonce(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(null=False,blank=False,upload_to="uploads/annonces/")
    produit = models.ForeignKey(Annonce,on_delete=models.CASCADE,related_name="images")

