from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recette, Ingredient, RecetteIngredient
from .forms import RecetteForm, IngredientForm, RecetteIngredientForm


def chef_cuisinier_required(view_func):
    """Décorateur pour restreindre l'accès en écriture au Chef cuisinier ou Administrateur."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['chef_cuisinier', 'administrateur'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Cette action est réservée au Chef cuisinier.")
        return redirect('liste_recettes')
    return _wrapped_view


# ─── RECETTES ───

@login_required
def liste_recettes(request):
    # Les Cuisiniers et autres ont un accès en lecture seule
    recettes = Recette.objects.all()
    return render(request, 'recettes/liste_recettes.html', {'recettes': recettes})


@login_required
def detail_recette(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    ingredients = RecetteIngredient.objects.filter(recette=recette)
    return render(request, 'recettes/detail_recette.html', {
        'recette': recette,
        'ingredients': ingredients
    })


@chef_cuisinier_required
def creer_recette(request):
    if request.method == 'POST':
        form = RecetteForm(request.POST)
        if form.is_valid():
            recette = form.save()
            messages.success(request, 'Recette créée avec succès !')
            return redirect('detail_recette', pk=recette.pk)
    else:
        form = RecetteForm()
    return render(request, 'recettes/form_recette.html', {'form': form, 'titre': 'Créer une recette'})


@chef_cuisinier_required
def modifier_recette(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    if request.method == 'POST':
        form = RecetteForm(request.POST, instance=recette)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recette modifiée avec succès !')
            return redirect('detail_recette', pk=recette.pk)
    else:
        form = RecetteForm(instance=recette)
    return render(request, 'recettes/form_recette.html', {'form': form, 'titre': 'Modifier la recette'})


@chef_cuisinier_required
def supprimer_recette(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    
    # Bloquer la suppression si associée à un produit actif (disponible=True)
    if hasattr(recette, 'produits'):
        produits_actifs = recette.produits.filter(disponible=True)
        if produits_actifs.exists():
            noms_plats = ", ".join([p.nom for p in produits_actifs])
            messages.error(
                request, 
                f"Impossible de supprimer cette recette car elle est liée à des plats actifs en vente : {noms_plats}."
            )
            return redirect('detail_recette', pk=recette.pk)
            
    if request.method == 'POST':
        recette.delete()
        messages.success(request, 'Recette supprimée avec succès !')
        return redirect('liste_recettes')
    return render(request, 'recettes/confirmer_suppression.html', {'recette': recette})


# ─── INGREDIENTS ───

@login_required
def list_ingredients_access(request):
    """Lecture des ingrédients."""
    ingredients = Ingredient.objects.all()
    return render(request, 'recettes/liste_ingredients.html', {'ingredients': ingredients})


# Rediriger l'ancienne vue liste_ingredients
liste_ingredients = login_required(list_ingredients_access)


@chef_cuisinier_required
def creer_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrédient créé avec succès !')
            return redirect('liste_ingredients')
    else:
        form = IngredientForm()
    return render(request, 'recettes/form_ingredient.html', {'form': form, 'titre': 'Ajouter un ingrédient'})


@chef_cuisinier_required
def ajouter_ingredient_recette(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    if request.method == 'POST':
        form = RecetteIngredientForm(request.POST)
        if form.is_valid():
            ri = form.save(commit=False)
            ri.recette = recette
            ri.save()
            messages.success(request, 'Ingrédient ajouté à la recette !')
            return redirect('detail_recette', pk=recette.pk)
    else:
        form = RecetteIngredientForm()
    return render(request, 'recettes/ajouter_ingredient.html', {
        'form': form,
        'recette': recette
    })


@chef_cuisinier_required
def modifier_ingredient(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrédient modifié avec succès !')
            return redirect('liste_ingredients')
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, 'recettes/form_ingredient.html', {
        'form': form,
        'titre': 'Modifier un ingrédient'
    })