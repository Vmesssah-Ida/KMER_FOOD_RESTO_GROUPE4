# 📄 dashboard/urls.py
# Module 7 — Tableau de Bord et Rapports

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard_directeur'),
    path('export/pdf/', views.export_rapport_pdf, name='export_rapport_pdf'),
]