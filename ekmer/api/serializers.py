from rest_framework import serializers
from .models import Users,Categorie

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
