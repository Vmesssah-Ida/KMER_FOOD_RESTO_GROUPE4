from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recette, Ingredient, RecetteIngredient
from .forms import RecetteForm, IngredientForm, RecetteIngredientForm


# ─── RECETTES ───

@login_required
def liste_recettes(request):
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


@login_required
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


@login_required
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


@login_required
def supprimer_recette(request, pk):
    recette = get_object_or_404(Recette, pk=pk)
    if request.method == 'POST':
        recette.delete()
        messages.success(request, 'Recette supprimée avec succès !')
        return redirect('liste_recettes')
    return render(request, 'recettes/confirmer_suppression.html', {'recette': recette})


# ─── INGREDIENTS ───

@login_required
def liste_ingredients(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'recettes/liste_ingredients.html', {'ingredients': ingredients})


@login_required
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

@login_required
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

@login_required
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