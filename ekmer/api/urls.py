from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginWithEmailAndPasswordView,ProfileView,SignInWithEmailAndPassword,LoginWithPhoneAndPasswordView,ProfilePhotoView
from .categorie_views import CategorieViewSet,LowCategorieViewSet,SousCategorieParCategorieView
from .annonce_views import AnnonceViewSet,AnnonceParSousCategorie,RechercherAnnonce,AnnonceByUser,AllAnnonces,SuspendreAnnonceView
from .vente_views import VenteView,VenteDetailView,VentesVendeurView,AchatUtilisateurView,PanierView,PanierItemAddView,PanierItemDetailView,PanierViderView,OrderListCreateView,OrderConfirmerView
from .favoris_views import FavorisView
from .livreurs_views import (
    LivreurListView, LivreurUpdateView, LivreurValiderView,
    LivreurMeView, TrajetLivreurListCreateView, TrajetLivreurDetailView,
)
from .livraison_views import (
    LivraisonCreateView, MesLivraisonsLivreurView, LivraisonRepondreView,
    LivraisonDemarrerView, LivraisonMarquerLivreeView, LivraisonConfirmerView,
)
from django.urls import path,include
from django.conf import settings
from . import paiement_views
router = DefaultRouter()
router.register('users',UserViewSet)
router.register('categories',CategorieViewSet)
router.register('sous_categories',LowCategorieViewSet)
router.register('annonces',AnnonceViewSet,basename='annonce')
urlpatterns = [
    path('annonces/',AllAnnonces.as_view(),name='annonces'),   # ← déplacé avant le router
    path('',include(router.urls)),
    path('auth/login/',LoginWithEmailAndPasswordView.as_view(),name='login'),
    path('auth/login/tel',LoginWithPhoneAndPasswordView.as_view(),name='logintel'),
    path('auth/profile/',ProfileView.as_view(),name='profile'),
    path('auth/register/',SignInWithEmailAndPassword.as_view(),name='register'),
    path('low_categories/<str:categorie_code>/sous_categories/',SousCategorieParCategorieView.as_view()),
    path('all_annonces/<str:low_categorie_code>/annonces/',AnnonceParSousCategorie.as_view()),
    path('annonce/search/',RechercherAnnonce.as_view(),name='recherche-annonce'),
    path('annonces-user/',AnnonceByUser.as_view(),name='annonces-by-user'),
    path('ventes/',VenteView.as_view(),name='ventes'),
    path('ventes/vendeur/',VentesVendeurView.as_view(),name="ventes-user"),
    path('ventes/<str:code>/',VenteDetailView.as_view(),name='vente-details'),
    path('achats/',AchatUtilisateurView.as_view(),name='achats'),
    path('panier/',PanierView.as_view()),
    path('panier/items/',PanierItemAddView.as_view()),
    path('panier/items/<int:item_id>/',PanierItemDetailView.as_view()),
    path('panier/vider/',PanierViderView.as_view()),
    path('commandes/',OrderListCreateView.as_view()),
    path('commandes/<int:order_id>/confirmer/',OrderConfirmerView.as_view()),
    path('favoris/',FavorisView.as_view(),name='favoris'),
    path('favoris/<str:annonce_code>/',FavorisView.as_view(),name='favoris-delete'),
    path('auth/profil/photo/',ProfilePhotoView.as_view(),name='profil-photo'),
    path('paiements/initier/', paiement_views.initier_paiement, name='initier-paiement'),
    path('paiements/webhook/', paiement_views.webhook_callback, name='webhook-paiement'),
    path('livreurs/', LivreurListView.as_view(), name='livreurs-list'),
    path('annonces/<str:code>/statut/', SuspendreAnnonceView.as_view(), name='annonce-suspendre'),
    path('livreurs/<uuid:id>/valider/', LivreurValiderView.as_view(), name='livreur-valider'),
    path('livreurs/<uuid:id>/', LivreurUpdateView.as_view(), name='livreur-update'),
    path('livreurs/me/', LivreurMeView.as_view(), name='livreur-me'),
    path('livreurs/me/trajets/', TrajetLivreurListCreateView.as_view(), name='livreur-trajets'),
    path('livreurs/me/trajets/<uuid:id>/', TrajetLivreurDetailView.as_view(), name='livreur-trajet-detail'),
    path('livreurs/me/livraisons/', MesLivraisonsLivreurView.as_view(), name='livreur-livraisons'),
    path('livraisons/', LivraisonCreateView.as_view(), name='livraison-create'),
    path('livraisons/<uuid:id>/repondre/', LivraisonRepondreView.as_view(), name='livraison-repondre'),
    path('livraisons/<uuid:id>/demarrer/', LivraisonDemarrerView.as_view(), name='livraison-demarrer'),
    path('livraisons/<uuid:id>/marquer-livree/', LivraisonMarquerLivreeView.as_view(), name='livraison-marquer-livree'),
    path('livraisons/<uuid:id>/confirmer/', LivraisonConfirmerView.as_view(), name='livraison-confirmer'),
]
