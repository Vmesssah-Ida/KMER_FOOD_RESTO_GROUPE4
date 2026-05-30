from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.personnel_liste,      name='personnel_liste'),
    path('<int:pk>/',              views.personnel_detail,     name='personnel_detail'),
    path('presences/',             views.presence_enregistrer, name='presence_enregistrer'),
    path('<int:pk>/paie/',         views.paie_calculer,        name='paie_calculer'),
    path('paie/<int:pk>/versee/',  views.paie_marquer_versee,  name='paie_marquer_versee'),
]
