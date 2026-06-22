from django.db import models


class Article(models.Model):
    nom = models.CharField(max_length=100)
    unite = models.CharField(max_length=50)
    quantite_disponible = models.FloatField(default=0)
    seuil_critique = models.FloatField(default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    alerte = models.BooleanField(default=False)

    def verifier_seuil(self):
        if self.quantite_disponible <= self.seuil_critique:
            self.alerte = True
        else:
            self.alerte = False
        self.save()

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"


class MouvementStock(models.Model):
    TYPES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='mouvements'
    )
    type = models.CharField(max_length=10, choices=TYPES)
    quantite = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    motif = models.CharField(max_length=200, blank=True)
    commande = models.ForeignKey(
        'commandes.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements'
    )

    def __str__(self):
        return f"{self.type} - {self.article.nom} - {self.quantite}"

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"