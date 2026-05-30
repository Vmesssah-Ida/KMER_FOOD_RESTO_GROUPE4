from django.db import models
from django.conf import settings
from produits.models import Produit

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente',     'En attente'),
        ('en_preparation', 'En préparation'),
        ('servie',         'Servie'),
        ('annulee',        'Annulée'),
    ]
    TYPE_CHOICES = [
        ('sur_place', 'Sur place'),
        ('livraison', 'Livraison'),
    ]
    serveur       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='commandes')
    statut        = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    type_commande = models.CharField(max_length=20, choices=TYPE_CHOICES, default='sur_place')
    date_creation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculer_montant(self):
        total = sum(ligne.sous_total() for ligne in self.lignes.all())
        self.montant_total = total
        self.save()
        return total

    def peut_etre_annulee(self):
        return self.statut == 'en_attente'

    def __str__(self):
        return f"Commande #{self.pk} — {self.statut}"

    class Meta:
        verbose_name = "Commande"
        ordering = ['-date_creation']


class LigneCommande(models.Model):
    commande      = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit       = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite      = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=8, decimal_places=2)

    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite}× {self.produit.nom}"
