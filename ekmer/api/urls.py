from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginWithEmailAndPasswordView,ProfileView,SignInWithEmailAndPassword,LoginWithPhoneAndPasswordView
from .categorie_views import CategorieViewSet,LowCategorieViewSet,SousCategorieParCategorieView
from .annonce_views import AnnonceViewSet,AnnonceParSousCategorie,RechercherAnnonce
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
router = DefaultRouter()
router.register('users',UserViewSet)
router.register('categories',CategorieViewSet)
router.register('sous_categories',LowCategorieViewSet)
router.register('annonces',AnnonceViewSet,basename='annonce')
urlpatterns = [
    path('',include(router.urls)),
    path('auth/login/',LoginWithEmailAndPasswordView.as_view(),name='login'),
    path('auth/login/tel',LoginWithPhoneAndPasswordView.as_view(),name='logintel'),
    path('auth/profile/',ProfileView.as_view(),name='profile'),
    path('auth/register/',SignInWithEmailAndPassword.as_view(),name='register'),
    path('low_categories/<str:categorie_code>/sous_categories/',SousCategorieParCategorieView.as_view()),
    path('all_annonces/<str:low_categorie_code>/annonces/',AnnonceParSousCategorie.as_view()),
    path('annonce/search/',RechercherAnnonce.as_view(),name='recherche-annonce')
] 
