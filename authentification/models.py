# 📄 authentification/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class Employe(AbstractUser):

    ROLES = [
        ('directeur',         'Directeur'),
        ('caissier',          'Caissier'),
        ('chef_cuisinier',    'Chef Cuisinier'),
        ('livreur',           'Livreur'),
        ('serveur',           'Serveur'),
        ('responsable_stock', 'Responsable Stock'),
        ('client',            'Client'),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLES,
        default='client',
        verbose_name='Rôle'
    )
    telephone      = models.CharField(max_length=20, blank=True, null=True)
    adresse        = models.CharField(max_length=255, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)

    # ← Ces deux lignes corrigent l'erreur
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='employe_set',
        blank=True,
        verbose_name='Groupes'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='employe_set',
        blank=True,
        verbose_name='Permissions'
    )

    def __str__(self):
        return f"{self.username} — {self.get_role_display()}"