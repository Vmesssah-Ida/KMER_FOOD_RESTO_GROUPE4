from django.urls import path, re_path
from . import views

urlpatterns = [
    path('',                         views.accueil,            name='accueil'),
    path('login/',                   views.login_view,         name='login'),
    path('logout/',                  views.logout_view,        name='logout'),
    path('menu/',                    views.menu,               name='menu'),        # ← ajouté
    path('a-propos/',                views.a_propos,           name='a_propos'),    # ← ajouté
    path('recettes/templates/recettes/',                    views.recettes,               name='recettes'), 
    path('produits/templates/produits/',                    views.produits,               name='produits'), 
    path('inventaire/templates/inventaire/',                    views.inventaire,               name='inventaire'),  
    path('dashboard/templates/dashboard/',          views.dashboard, name='dashboard_directeur'),
    path('dashboard/caissier/',           views.caissier,            name='caissier'),
    path('dashboard/chef-cuisinier/',     views.chef_cuisinier,      name='chef_cuisinier'),
    path('dashboard/livreur/',            views.livreur,             name='livreur'),
    path('dashboard/serveur/',            views.serveur,             name='serveur'),
    path('inventaire/templates/inventaire',  views.responsable_stock,   name='responsable_stock'),
    path('dashboard/client/',             views.client,              name='client'),
    path('mon-espace/menu/',    views.menu_client,      name='menu_client'),
    path('mon-espace/panier/',  views.panier,           name='panier'),
    path('commandes/ajouter/',  views.commande_ajouter, name='commande_ajouter'),
    path('commandes/annuler/<int:cmd_id>/', views.commande_annuler, name='recommander'),
    path('commandes/annuler/<int:cmd_id>/', views.commande_annuler, name='commande_annuler'),
    path('commandes/creer/',                   views.commande_ajouter,          name='commande_creer'),
path('commandes/<int:cmd_id>/servie/',     views.commande_marquer_servie,  name='commande_marquer_servie'),
path('commandes/<int:cmd_id>/annuler/',    views.commande_annuler,         name='commande_annuler'),
path('commandes/<int:cmd_id>/facture/',    views.commande_facture,         name='commande_facture'),
path('reservations/creer/',               views.reservation_creer,        name='reservation_creer'),
    path('reservations/<int:res_id>/annuler/',views.reservation_annuler,      name='reservation_annuler'),
    path('inscription/', views.inscription_client, name='inscription_client'),
    path('admin/utilisateurs/', views.utilisateurs_gestion, name='utilisateurs_gestion'),
    path('dashboard/cuisinier/', views.cuisinier, name='cuisinier'),
    path('404/', views.erreur,      name='page_not_found'),
]

handler404 = 'authentification.views.erreur'
#re_path(r'^.*$', views.erreur, name='catch_all')