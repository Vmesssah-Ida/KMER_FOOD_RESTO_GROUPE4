from django.urls import path
from . import views

urlpatterns = [
    # Recettes
    path('', views.liste_recettes, name='liste_recettes'),
    path('<int:pk>/', views.detail_recette, name='detail_recette'),
    path('creer/', views.creer_recette, name='creer_recette'),
    path('<int:pk>/modifier/', views.modifier_recette, name='modifier_recette'),
    path('<int:pk>/supprimer/', views.supprimer_recette, name='supprimer_recette'),
    path('<int:pk>/ajouter-ingredient/', views.ajouter_ingredient_recette, name='ajouter_ingredient_recette'),

    # Ingrédients
    path('ingredients/', views.liste_ingredients, name='liste_ingredients'),
    path('ingredients/creer/', views.creer_ingredient, name='creer_ingredient'),
    path('ingredients/<int:pk>/modifier/', views.modifier_ingredient, name='modifier_ingredient'),
]
