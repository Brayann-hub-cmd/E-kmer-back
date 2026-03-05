from django.db import models
import uuid
class Users(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=128,null=True,blank=True)
    telephone = models.CharField(max_length=13,null=True,blank=True)
    email = models.EmailField(max_length=128,null=True,blank=True)
    password = models.CharField(max_length=16,null=True,blank=True)
    role = models.CharField(max_length=64,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,editable=False,null=True)

    class Meta:
        db_table="users"
        ordering=['-created_at']