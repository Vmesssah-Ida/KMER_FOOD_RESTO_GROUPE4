from django.urls import path
from . import views

urlpatterns = [
    # Articles
    path('', views.liste_articles, name='liste_articles'),
    path('<int:pk>/', views.detail_article, name='detail_article'),
    path('creer/', views.creer_article, name='creer_article'),
    path('<int:pk>/modifier/', views.modifier_article, name='modifier_article'),
    path('<int:pk>/supprimer/', views.supprimer_article, name='supprimer_article'),
    path('<int:pk>/mouvement/', views.ajouter_mouvement, name='ajouter_mouvement'),

    # Fournisseurs
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/creer/', views.creer_fournisseur, name='creer_fournisseur'),
]