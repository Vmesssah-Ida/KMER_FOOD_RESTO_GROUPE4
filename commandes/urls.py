from django.urls import path
from . import views

urlpatterns = [
    path('creer/',                        views.commande_creer,          name='commande_creer'),
    path('liste/',                        views.commande_ajouter,        name='commande_ajouter'),
    path('<int:cmd_id>/facture/',         views.commande_facture,        name='commande_facture'),
    path('<int:cmd_id>/servie/',          views.commande_marquer_servie, name='commande_marquer_servie'),
    path('<int:cmd_id>/annuler/',         views.commande_annuler,        name='commande_annuler'),
]
