# commandes/models.py
# Module 4 — Gestion des commandes
# KMER FOOD RESTO · Groupe 04 · ENSP Yaoundé I

from django.db import models
from django.conf import settings
from produits.models import Produit


class Commande(models.Model):
    """
    Classe centrale du flux de vente.
    Liée au Serveur (FK → AUTH_USER_MODEL), composition avec LigneCommande.
    Règles métier :
      - Doit contenir au moins un produit (vérifié dans la vue)
      - Annulable uniquement si statut == 'en_attente'
      - Toute validation déclenche la mise à jour du stock (signal dans inventaire)
    """

    STATUT_CHOICES = [
        ('en_attente',     'En attente'),
        ('en_preparation', 'En préparation'),
        ('prete',          'Prête'),
        ('servie',         'Servie'),
        ('annulee',        'Annulée'),
    ]

    TYPE_CHOICES = [
        ('sur_place',  'Sur place'),
        ('livraison',  'Livraison'),
        ('a_emporter', 'A emporter'),
    ]

    # ── Champs principaux ──────────────────────────────────────────────────────
    serveur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commandes',
        verbose_name='Serveur',
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name='Statut',
    )
    type_commande = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='sur_place',
        verbose_name='Type de commande',
    )

    # ── Informations complémentaires ──────────────────────────────────────────
    numero_table = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Numéro de table',
        help_text='Ex: 03, VIP-1. Laisser vide pour une livraison.',
    )
    note_cuisine = models.TextField(
        blank=True,
        default='',
        verbose_name='Note pour la cuisine',
        help_text='Instructions spéciales : cuisson, allergies, modifications...',
    )
    client_nom = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Nom du client',
        help_text='Requis pour une livraison.',
    )
    client_telephone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Téléphone client',
    )
    adresse_livraison = models.TextField(
        blank=True,
        default='',
        verbose_name='Adresse de livraison',
        help_text='Obligatoire si type_commande = livraison.',
    )

    # ── Montant ───────────────────────────────────────────────────────────────
    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Montant total (FCFA)',
    )

    # ── Horodatage ────────────────────────────────────────────────────────────
    date_creation    = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_mise_a_jour = models.DateTimeField(auto_now=True,     verbose_name='Dernière mise à jour')

    # ── Méthodes métier ───────────────────────────────────────────────────────
    def calculer_montant(self):
        """
        Calcule et enregistre le montant total à partir des lignes.
        Appelée après chaque ajout/suppression de ligne.
        """
        total = sum(ligne.sous_total() for ligne in self.lignes.all())
        self.montant_total = total
        self.save(update_fields=['montant_total', 'date_mise_a_jour'])
        return total

    def peut_etre_annulee(self):
        """
        Règle métier : une commande n'est annulable que si elle est encore
        'en_attente'. Appelée comme méthode (avec parenthèses) dans les vues
        et dans les templates via {% if commande.peut_etre_annulee %}.
        """
        return self.statut == 'en_attente'

    def est_active(self):
        """Vrai si la commande n'est ni servie ni annulée."""
        return self.statut in ('en_attente', 'en_preparation', 'prete')

    def passer_en_preparation(self):
        """Transition : en_attente → en_preparation."""
        if self.statut == 'en_attente':
            self.statut = 'en_preparation'
            self.save(update_fields=['statut', 'date_mise_a_jour'])
            return True
        return False

    def marquer_prete(self):
        """Transition : en_preparation → prete (chef a terminé)."""
        if self.statut == 'en_preparation':
            self.statut = 'prete'
            self.save(update_fields=['statut', 'date_mise_a_jour'])
            return True
        return False

    def marquer_servie(self):
        """Transition : prete → servie (serveur ou livreur a remis la commande)."""
        if self.statut in ('en_attente', 'en_preparation', 'prete'):
            self.statut = 'servie'
            self.save(update_fields=['statut', 'date_mise_a_jour'])
            return True
        return False

    def annuler(self):
        """Transition : en_attente → annulee."""
        if self.peut_etre_annulee():
            self.statut = 'annulee'
            self.save(update_fields=['statut', 'date_mise_a_jour'])
            return True
        return False

    # ── Représentation ────────────────────────────────────────────────────────
    def __str__(self):
        table = f" · Table {self.numero_table}" if self.numero_table else ""
        return f"Commande #{self.pk}{table} — {self.get_statut_display()}"

    class Meta:
        verbose_name        = "Commande"
        verbose_name_plural = "Commandes"
        ordering            = ['-date_creation']


class LigneCommande(models.Model):
    """
    Ligne de commande (composition avec Commande).
    Une LigneCommande ne peut pas exister sans sa commande parente
    → on_delete=CASCADE.
    """

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name='Commande',
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        verbose_name='Produit',
    )
    quantite = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantité',
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire (FCFA)',
    )

    # ── Méthodes ──────────────────────────────────────────────────────────────
    def sous_total(self):
        """Retourne quantite × prix_unitaire."""
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        """
        Snapshot du prix au moment de la création.
        Correction du bug original : tester `None` explicitement,
        pas `not self.prix_unitaire` qui est faux pour Decimal(0).
        """
        if self.prix_unitaire is None:
            self.prix_unitaire = self.produit.prix
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite}× {self.produit.nom} ({self.prix_unitaire} FCFA)"

    class Meta:
        verbose_name        = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"


class Facture(models.Model):
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='facture',
        verbose_name='Commande'
    )
    date_emission = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'émission'
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Montant (FCFA)'
    )
    est_valide = models.BooleanField(
        default=True,
        verbose_name='Est valide'
    )

    def __str__(self):
        return f"Facture #{self.pk} — Commande #{self.commande.pk} ({self.montant} FCFA)"

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
