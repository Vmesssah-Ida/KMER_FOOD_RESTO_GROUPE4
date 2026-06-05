from django.contrib import admin
from .models import Produit, Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone', 'ordre', 'active']
    search_fields = ['nom']
    list_filter = ['active']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom','categorie', 'prix', 'disponible', 'temps_preparation']
    search_fields = ['nom']
    list_filter = ['categorie', 'disponible']