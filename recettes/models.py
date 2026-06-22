from django.db import models
from django.conf import settings


class Ingredient(models.Model):
    nom = models.CharField(max_length=100)
    unite = models.CharField(max_length=50)
    seuil_critique = models.FloatField(default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Ingrédient"
        verbose_name_plural = "Ingrédients"


class Recette(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, default='')
    temps_cuisson = models.IntegerField(help_text="Temps en minutes") 
    chef_responsable = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    related_name='recettes'
)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecetteIngredient'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"


class RecetteIngredient(models.Model):
    recette = models.ForeignKey(
        Recette,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantite = models.FloatField()

    def __str__(self):
        return f"{self.recette.nom} - {self.ingredient.nom}"

    class Meta:
        verbose_name = "Ingrédient de recette"
        verbose_name_plural = "Ingrédients de recette"