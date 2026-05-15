# 📄 authentification/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employe


@admin.register(Employe)
class EmployeAdmin(UserAdmin):

    # Colonnes visibles dans la liste
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('role', 'username')

    # Ajouter le champ "role" dans le formulaire d'édition
    fieldsets = UserAdmin.fieldsets + (
        ('Informations KMER FOOD', {
            'fields': ('role', 'telephone', 'adresse', 'date_naissance')
        }),
    )

    # Ajouter le champ "role" dans le formulaire de création
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations KMER FOOD', {
            'fields': ('email', 'role', 'telephone', 'adresse', 'date_naissance')
        }),
    )