from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_produits, name='liste_produits'),
    path('<int:pk>/', views.detail_produit, name='detail_produit'),
    path('creer/', views.creer_produit, name='creer_produit'),
    path('<int:pk>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('<int:pk>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categories/creer/', views.creer_categorie, name='creer_categorie'),
]