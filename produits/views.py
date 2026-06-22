# 📄 produits/views.py
# Module 3 — Gestion des produits

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Categorie
from recettes.models import Recette


def chef_cuisinier_required(view_func):
    """Accès réservé au Chef cuisinier ou Administrateur."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['chef_cuisinier', 'administrateur'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Cette action est réservée au Chef cuisinier.")
        return redirect('liste_produits')
    return _wrapped_view


def chef_or_directeur_required(view_func):
    """Modification autorisée pour le Chef cuisinier, le Directeur ou l'Administrateur."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['chef_cuisinier', 'directeur', 'administrateur'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Vous n'avez pas l'autorisation de modifier ce produit.")
        return redirect('liste_produits')
    return _wrapped_view


# ─── PRODUITS ───

@login_required
def liste_produits(request):
    produits = Produit.objects.all()
    categories = Categorie.objects.filter(active=True)
    return render(request, 'produits/liste_produits.html', {
        'produits': produits,
        'categories': categories
    })


@login_required
def detail_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    return render(request, 'produits/detail_produit.html', {
        'produit': produit
    })


@chef_cuisinier_required
def creer_produit(request):
    categories = Categorie.objects.filter(active=True)
    recettes = Recette.objects.all()
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        prix_str = request.POST.get('prix', '0').strip()
        categorie_id = request.POST.get('categorie')
        recette_id = request.POST.get('recette')
        disponible = request.POST.get('disponible') == 'on'
        temps_preparation = request.POST.get('temps_preparation', 30)
        photo = request.FILES.get('photo')

        # Validation : prix strictement positif
        try:
            prix = float(prix_str)
            if prix <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, "Le prix doit être un nombre strictement positif.")
            return render(request, 'produits/form_produit.html', {
                'titre': 'Ajouter un produit', 'categories': categories, 'recettes': recettes, 'post': request.POST
            })

        # Validation : catégorie obligatoire
        if not categorie_id:
            messages.error(request, "La catégorie est obligatoire.")
            return render(request, 'produits/form_produit.html', {
                'titre': 'Ajouter un produit', 'categories': categories, 'recettes': recettes, 'post': request.POST
            })
            
        categorie = get_object_or_404(Categorie, pk=categorie_id)
        
        # Validation : plat en vente doit être lié à une recette valide (au moins un ingrédient)
        recette = None
        if recette_id:
            recette = get_object_or_404(Recette, pk=recette_id)
            
        if disponible:
            if not recette:
                messages.error(request, "Un plat ne peut être mis en vente que s'il est associé à une recette.")
                return render(request, 'produits/form_produit.html', {
                    'titre': 'Ajouter un produit', 'categories': categories, 'recettes': recettes, 'post': request.POST
                })
            elif recette.ingredients.count() == 0:
                messages.error(
                    request, 
                    f"Impossible de mettre en vente : la recette '{recette.nom}' doit contenir au moins un ingrédient."
                )
                return render(request, 'produits/form_produit.html', {
                    'titre': 'Ajouter un produit', 'categories': categories, 'recettes': recettes, 'post': request.POST
                })

        Produit.objects.create(
            nom=nom,
            description=description,
            prix=prix,
            categorie=categorie,
            recette=recette,
            disponible=disponible,
            photo=photo,
            temps_preparation=temps_preparation
        )
        messages.success(request, 'Produit créé avec succès !')
        return redirect('liste_produits')
        
    return render(request, 'produits/form_produit.html', {
        'titre': 'Ajouter un produit',
        'categories': categories,
        'recettes': recettes
    })


@chef_or_directeur_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    categories = Categorie.objects.filter(active=True)
    recettes = Recette.objects.all()
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        prix_str = request.POST.get('prix', '0').strip()
        categorie_id = request.POST.get('categorie')
        recette_id = request.POST.get('recette')
        disponible = request.POST.get('disponible') == 'on'
        temps_preparation = request.POST.get('temps_preparation', 30)
        photo = request.FILES.get('photo')

        # Si l'utilisateur est Directeur, restreindre la modification au prix uniquement
        if request.user.role == 'directeur' and not request.user.is_superuser:
            # Ne modifier que le prix
            try:
                prix = float(prix_str)
                if prix <= 0:
                    raise ValueError()
                produit.prix = prix
                produit.save()
                messages.success(request, 'Prix du produit mis à jour avec succès !')
                return redirect('detail_produit', pk=produit.pk)
            except ValueError:
                messages.error(request, "Le prix doit être un nombre strictement positif.")
                return render(request, 'produits/form_produit.html', {
                    'titre': 'Modifier le produit', 'produit': produit, 'categories': categories, 'recettes': recettes
                })

        # Validation pour Chef cuisinier : prix strictement positif
        try:
            prix = float(prix_str)
            if prix <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, "Le prix doit être un nombre strictement positif.")
            return render(request, 'produits/form_produit.html', {
                'titre': 'Modifier le produit', 'produit': produit, 'categories': categories, 'recettes': recettes
            })

        # Validation : catégorie obligatoire
        if not categorie_id:
            messages.error(request, "La catégorie est obligatoire.")
            return render(request, 'produits/form_produit.html', {
                'titre': 'Modifier le produit', 'produit': produit, 'categories': categories, 'recettes': recettes
            })
            
        categorie = get_object_or_404(Categorie, pk=categorie_id)

        # Validation : plat en vente doit être lié à une recette valide (au moins un ingrédient)
        recette = None
        if recette_id:
            recette = get_object_or_404(Recette, pk=recette_id)

        if disponible:
            if not recette:
                messages.error(request, "Un plat ne peut être mis en vente que s'il est associé à une recette.")
                return render(request, 'produits/form_produit.html', {
                    'titre': 'Modifier le produit', 'produit': produit, 'categories': categories, 'recettes': recettes
                })
            elif recette.ingredients.count() == 0:
                messages.error(
                    request, 
                    f"Impossible de mettre en vente : la recette '{recette.nom}' doit contenir au moins un ingrédient."
                )
                return render(request, 'produits/form_produit.html', {
                    'titre': 'Modifier le produit', 'produit': produit, 'categories': categories, 'recettes': recettes
                })

        produit.nom = nom
        produit.description = description
        produit.prix = prix
        produit.categorie = categorie
        produit.recette = recette
        produit.disponible = disponible
        if photo:
            produit.photo = photo
        produit.temps_preparation = temps_preparation
        produit.save()
        
        messages.success(request, 'Produit modifié avec succès !')
        return redirect('detail_produit', pk=produit.pk)
        
    return render(request, 'produits/form_produit.html', {
        'titre': 'Modifier le produit',
        'produit': produit,
        'categories': categories,
        'recettes': recettes
    })


@chef_cuisinier_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès !')
        return redirect('liste_produits')
    return render(request, 'produits/confirmer_suppression.html', {
        'produit': produit
    })


# ─── CATEGORIES ───

@chef_cuisinier_required
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'produits/liste_categories.html', {
        'categories': categories
    })


@chef_cuisinier_required
def creer_categorie(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        icone = request.POST.get('icone', '🍽️')
        ordre = request.POST.get('ordre', 0)
        Categorie.objects.create(
            nom=nom,
            description=description,
            icone=icone,
            ordre=ordre
        )
        messages.success(request, 'Catégorie créée avec succès !')
        return redirect('liste_categories')
    return render(request, 'produits/form_categorie.html', {
        'titre': 'Ajouter une catégorie'
    })