# 📄 rh/models.py
# Module 6 — Ressources Humaines et Paie

from django.db import models
from django.conf import settings


class Personnel(models.Model):
    POSTES = [
        ('directeur',         'Directeur'),
        ('administrateur',    'Administrateur'),
        ('chef_cuisinier',    'Chef cuisinier'),
        ('cuisinier',         'Cuisinier'),
        ('serveur',           'Serveur'),
        ('responsable_stock', 'Gestionnaire de stock'),
        ('caissier',          'Caissier'),
        ('livreur',           'Livreur'),
    ]

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personnel'
    )
    poste = models.CharField(max_length=30, choices=POSTES)
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2)
    date_embauche = models.DateField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnels"
        ordering = ['poste']

    def __str__(self):
        return f"{self.utilisateur.get_full_name() or self.utilisateur.username} — {self.get_poste_display()}"


class Presence(models.Model):
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name='presences'
    )
    date = models.DateField()
    present = models.BooleanField(default=True)
    heure_arrivee = models.TimeField(blank=True, null=True)
    heure_depart = models.TimeField(blank=True, null=True)
    remarque = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ['-date']
        unique_together = ('personnel', 'date')

    def __str__(self):
        statut = "Présent" if self.present else "Absent"
        return f"{self.personnel.utilisateur.username} — {self.date} : {statut}"


class Paie(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('versee',     'Versée'),
    ]

    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name='paies'
    )
    mois = models.PositiveIntegerField()
    annee = models.PositiveIntegerField()
    jours_travailles = models.PositiveIntegerField(default=0)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    date_versement = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Paie"
        verbose_name_plural = "Paies"
        ordering = ['-annee', '-mois']
        unique_together = ('personnel', 'mois', 'annee')

    def calculer(self):
        """Calcule automatiquement le montant basé sur salaire_base (journalier) et jours travaillés."""
        self.montant = self.jours_travailles * self.personnel.salaire_base
        self.save()

    def __str__(self):
        return f"Paie {self.mois}/{self.annee} — {self.personnel.utilisateur.username}"


class Affectation(models.Model):
    SERVICES = [
        ('salle',   'Service en salle'),
        ('cuisine', 'Cuisine'),
        ('accueil', 'Accueil'),
        ('stock',   'Stock et approvisionnement'),
    ]

    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name='affectations'
    )
    service = models.CharField(max_length=50, choices=SERVICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Affectation de {self.personnel} au service {self.get_service_display()}"