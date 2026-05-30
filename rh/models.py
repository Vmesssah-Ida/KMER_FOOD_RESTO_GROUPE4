from django.db import models
from django.conf import settings

class Personnel(models.Model):
    POSTE_CHOICES = [
        ('directeur',         'Directeur'),
        ('administrateur',    'Administrateur'),
        ('chef_cuisinier',    'Chef cuisinier'),
        ('cuisinier',         'Cuisinier'),
        ('serveur',           'Serveur'),
        ('responsable_stock', 'Responsable stock'),
        ('caissier',          'Caissier'),
        ('livreur',           'Livreur'),
    ]
    utilisateur   = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personnel')
    poste         = models.CharField(max_length=30, choices=POSTE_CHOICES)
    salaire_base  = models.DecimalField(max_digits=10, decimal_places=2)
    date_embauche = models.DateField()
    telephone     = models.CharField(max_length=20, blank=True, null=True)
    adresse       = models.TextField(blank=True, null=True)

    def calculer_paie(self, jours_travailles, jours_ouvrables=26):
        return round((self.salaire_base / jours_ouvrables) * jours_travailles, 2)

    def __str__(self):
        return f"{self.utilisateur.get_full_name()} — {self.get_poste_display()}"

    class Meta:
        verbose_name = "Personnel"
        ordering = ['poste']


class Presence(models.Model):
    personnel     = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='presences')
    date          = models.DateField()
    present       = models.BooleanField(default=True)
    heure_arrivee = models.TimeField(blank=True, null=True)
    heure_depart  = models.TimeField(blank=True, null=True)
    remarque      = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        statut = "Présent" if self.present else "Absent"
        return f"{self.personnel} — {self.date} — {statut}"

    class Meta:
        verbose_name = "Présence"
        unique_together = ('personnel', 'date')
        ordering = ['-date']


class Paie(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('versee',     'Versée'),
    ]
    personnel        = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='paies')
    mois             = models.PositiveIntegerField()
    annee            = models.PositiveIntegerField()
    jours_travailles = models.PositiveIntegerField(default=0)
    montant          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut           = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    date_versement   = models.DateField(blank=True, null=True)

    def calculer(self):
        self.montant = self.personnel.calculer_paie(self.jours_travailles)
        self.save()
        return self.montant

    def __str__(self):
        return f"Paie {self.personnel} — {self.mois}/{self.annee} — {self.montant} FCFA"

    class Meta:
        verbose_name = "Paie"
        unique_together = ('personnel', 'mois', 'annee')
        ordering = ['-annee', '-mois']
