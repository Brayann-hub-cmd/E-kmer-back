from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginWithEmailAndPasswordView,ProfileView,SignInWithEmailAndPassword
from .categorie_views import CategorieViewSet,LowCategorieViewSet
from django.urls import path,include

router = DefaultRouter()
router.register('users',UserViewSet)
router.register('categories',CategorieViewSet)
router.register('sous_categories',LowCategorieViewSet)
urlpatterns = [
    path('',include(router.urls)),
    path('auth/login/',LoginWithEmailAndPasswordView.as_view(),name='login'),
    path('auth/profile/',ProfileView.as_view(),name='profile'),
    path('auth/register/',SignInWithEmailAndPassword.as_view(),name='register')
]