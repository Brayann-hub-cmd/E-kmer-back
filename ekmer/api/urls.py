from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginWithEmailAndPasswordView,ProfileView,SignInWithEmailAndPassword,LoginWithPhoneAndPasswordView
from .categorie_views import CategorieViewSet,LowCategorieViewSet
from .annonce_views import AnnonceViewSet
from django.urls import path,include

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
    path('auth/register/',SignInWithEmailAndPassword.as_view(),name='register')
]