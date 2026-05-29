from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Categorie


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


@login_required
def creer_produit(request):
    categories = Categorie.objects.filter(active=True)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        prix = request.POST.get('prix')
        categorie_id = request.POST.get('categorie')
        disponible = request.POST.get('disponible') == 'on'
        image_url = request.POST.get('image_url', '')
        temps_preparation = request.POST.get('temps_preparation', 30)
        categorie = get_object_or_404(Categorie, pk=categorie_id)
        Produit.objects.create(
            nom=nom,
            description=description,
            prix=prix,
            categorie=categorie,
            disponible=disponible,
            image_url=image_url,
            temps_preparation=temps_preparation
        )
        messages.success(request, 'Produit créé avec succès !')
        return redirect('liste_produits')
    return render(request, 'produits/form_produit.html', {
        'titre': 'Ajouter un produit',
        'categories': categories
    })


@login_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    categories = Categorie.objects.filter(active=True)
    if request.method == 'POST':
        produit.nom = request.POST.get('nom')
        produit.description = request.POST.get('description', '')
        produit.prix = request.POST.get('prix')
        categorie_id = request.POST.get('categorie')
        produit.disponible = request.POST.get('disponible') == 'on'
        produit.image_url = request.POST.get('image_url', '')
        produit.temps_preparation = request.POST.get('temps_preparation', 30)
        produit.categorie = get_object_or_404(Categorie, pk=categorie_id)
        produit.save()
        messages.success(request, 'Produit modifié avec succès !')
        return redirect('detail_produit', pk=produit.pk)
    return render(request, 'produits/form_produit.html', {
        'titre': 'Modifier le produit',
        'produit': produit,
        'categories': categories
    })


@login_required
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

@login_required
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'produits/liste_categories.html', {
        'categories': categories
    })


@login_required
def creer_categorie(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
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