# 📄 produits/models.py
# Module 3 — Gestion des produits

from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=10, blank=True, default='🍽️')
    ordre = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre']


class Produit(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name='produits'
    )
    disponible = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='produits/', blank=True, null=True)
    recette = models.ForeignKey(
        'recettes.Recette',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits'
    )
    temps_preparation = models.IntegerField(
        default=30,
        help_text="Temps en minutes"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['categorie', 'nom']