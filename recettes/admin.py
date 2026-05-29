from django.contrib import admin
from .models import Recette, Ingredient, RecetteIngredient


class RecetteIngredientInline(admin.TabularInline):
    model = RecetteIngredient
    extra = 1


@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'temps_cuisson', 'chef_responsable', 'date_creation']
    search_fields = ['nom']
    inlines = [RecetteIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'unite', 'prix_unitaire', 'seuil_critique']
    search_fields = ['nom']