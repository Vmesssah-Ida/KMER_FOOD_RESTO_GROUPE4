"""
URL configuration for KMER_FOOD_RESTO project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# 📄 KMER_FOOD_RESTO/KMER_FOOD_RESTO/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages principales
    path('',        include('authentification.urls')),  # accueil + login
   
    # Modules
    path('recettes/',    include('recettes.urls')),
    path('commandes/',   include('commandes.urls')),
    path('dashboard/',   include('dashboard.urls')),
    path('inventaire/',  include('inventaire.urls')),
    path('produits/',    include('produits.urls')),
    path('rh/',          include('rh.urls')),
    

] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])