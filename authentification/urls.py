from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.accueil,            name='accueil'),
    path('login/',                   views.login_view,         name='login'),
    path('logout/',                  views.logout_view,        name='logout'),
    path('menu/',                    views.menu,               name='menu'),        # ← ajouté
    path('a-propos/',                views.a_propos,           name='a_propos'),    # ← ajouté

    path('dashboard/directeur/',          views.dashboard_directeur, name='dashboard_directeur'),
    path('dashboard/caissier/',           views.caissier,            name='caissier'),
    path('dashboard/chef-cuisinier/',     views.chef_cuisinier,      name='chef_cuisinier'),
    path('dashboard/livreur/',            views.livreur,             name='livreur'),
    path('dashboard/serveur/',            views.serveur,             name='serveur'),
    path('dashboard/responsable-stock/',  views.responsable_stock,   name='responsable_stock'),
    path('dashboard/client/',             views.client,              name='client'),
]