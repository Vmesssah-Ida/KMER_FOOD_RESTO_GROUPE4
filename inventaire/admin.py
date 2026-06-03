from django.contrib import admin
from .models import Article, MouvementStock, Fournisseur


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'unite', 'quantite_disponible', 'seuil_critique', 'alerte']
    search_fields = ['nom']
    list_filter = ['alerte']


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ['article', 'type', 'quantite', 'date', 'motif']
    list_filter = ['type']
    search_fields = ['article__nom']


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'telephone', 'email', 'actif']
    search_fields = ['nom']