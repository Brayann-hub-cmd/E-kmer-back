from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginWithEmailAndPasswordView,ProfileView,SignInWithEmailAndPassword,LoginWithPhoneAndPasswordView
from .categorie_views import CategorieViewSet,LowCategorieViewSet,SousCategorieParCategorieView
from .annonce_views import AnnonceViewSet,AnnonceParSousCategorie,RechercherAnnonce
from .vente_views import VenteView,VenteDetailView,VentesVendeurView,AchatUtilisateurView,PanierView,PanierItemAddView,PanierItemDetailView,PanierViderView,OrderListCreateView,OrderConfirmerView
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
    path('annonce/search/',RechercherAnnonce.as_view(),name='recherche-annonce'),
    path('ventes/',VenteView.as_view(),name='ventes'),
    path('ventes/vendeur/',VentesVendeurView.as_view(),name="ventes-user"),
    path('ventes/<str:code>/',VenteDetailView.as_view(),name='vente-details'),
    path('achats/',AchatUtilisateurView.as_view(),name='achats'),
    path('panier/',PanierView.as_view()),
    path('panier/items/',PanierItemAddView.as_view()),
    path('panier/items/<int:item_id>/',PanierItemDetailView.as_view()),
    path('panier/vider/',PanierViderView.as_view()),
    path('commandes/',OrderListCreateView.as_view()),
    path('commandes/<int:order_id>/confirmer/',OrderConfirmerView.as_view())
] 
