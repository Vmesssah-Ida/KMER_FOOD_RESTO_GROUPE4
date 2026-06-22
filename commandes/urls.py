# commandes/urls.py
# Module 4 — Gestion des commandes · KMER FOOD RESTO

from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    # ── Vues principales (personnel interne) ─────────────────────────────────
    path('liste/',                      views.commande_liste,          name='commande_liste'),
    path('creer/',                      views.commande_creer,          name='commande_creer'),
    path('<int:cmd_id>/facture/',       views.commande_facture,        name='commande_facture'),
    path('<int:cmd_id>/preparation/',   views.commande_en_preparation, name='commande_en_preparation'),
    path('<int:cmd_id>/servie/',        views.commande_marquer_servie, name='commande_marquer_servie'),
    path('<int:cmd_id>/annuler/',       views.commande_annuler,        name='commande_annuler'),
    path('historique/',                 views.commande_historique,     name='commande_historique'),

    # ── API JSON — Communication temps réel entre modules ────────────────────
    # Chef cuisinier : polling des commandes actives en cuisine
    path('api/cuisine/',                views.api_cuisine,          name='api_cuisine'),
    # Chef : accepter un ticket (en_attente → en_preparation)
    path('api/<int:cmd_id>/preparer/', views.api_preparer,          name='api_preparer'),
    # Chef : marquer une commande comme prête (en_preparation → prete)
    path('api/<int:cmd_id>/servir/',   views.api_servir,            name='api_servir'),
    # Serveur : commandes prêtes en salle / à emporter
    path('api/serveur/',               views.api_serveur,           name='api_serveur'),
    # Serveur : confirmer qu'une commande en salle a été remise (prete → servie)
    path('api/<int:cmd_id>/serveur-servir/', views.api_serveur_servir, name='api_serveur_servir'),
    # Caissier : commandes servies en attente d'encaissement
    path('api/caisse/',                views.api_caisse,            name='api_caisse'),
    # Livreur : commandes de type livraison prêtes à prendre en charge
    path('api/livraisons/',            views.api_livraisons,        name='api_livraisons'),
    # Livreur : confirmer une livraison effectuée (prete → servie)
    path('api/<int:cmd_id>/livrer/',   views.api_livrer,            name='api_livrer'),
    # Client : suivi en temps réel de ses propres commandes (polling panier.html)
    path('api/mes-commandes/',         views.api_mes_commandes,     name='api_mes_commandes'),
]


# ─────────────────────────────────────────────────────────────────────────────
# NOTE : Les vues client (accueil, menu, panier) doivent être déclarées dans
#        le urls.py PRINCIPAL du projet (ex: kmer_food/urls.py) car elles
#        n'appartiennent pas au namespace 'commandes'.
#
#        Ajoutez ces lignes dans votre urls.py racine :
#
#   from commandes.views import client_accueil, menu_client, panier_client
#
#   urlpatterns += [
#       path('client/',       client_accueil, name='client'),
#       path('menu/',         menu_client,    name='menu_client'),
#       path('panier/',       panier_client,  name='panier'),
#   ]
#
# ─────────────────────────────────────────────────────────────────────────────
