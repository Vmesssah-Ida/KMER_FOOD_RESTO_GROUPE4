from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article, MouvementStock, Fournisseur

def responsable_stock_required(view_func):
    """Accès réservé au Gestionnaire de stock ou à l'Administrateur."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['responsable_stock', 'administrateur'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Cette action est réservée au Gestionnaire de stock.")
        return redirect('liste_articles')
    return _wrapped_view



# ─── ARTICLES ───

@login_required
def liste_articles(request):
    articles = Article.objects.all()
    alertes = Article.objects.filter(alerte=True)
    return render(request, 'inventaire/liste_articles.html', {
        'articles': articles,
        'alertes': alertes
    })


@login_required
def detail_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    mouvements = MouvementStock.objects.filter(article=article).order_by('-date')
    return render(request, 'inventaire/detail_article.html', {
        'article': article,
        'mouvements': mouvements
    })


@responsable_stock_required
def creer_article(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        unite = request.POST.get('unite')
        quantite = request.POST.get('quantite_disponible')
        seuil = request.POST.get('seuil_critique')
        prix = request.POST.get('prix_unitaire')
        article = Article.objects.create(
            nom=nom,
            unite=unite,
            quantite_disponible=quantite,
            seuil_critique=seuil,
            prix_unitaire=prix
        )
        article.verifier_seuil()
        messages.success(request, 'Article créé avec succès !')
        return redirect('liste_articles')
    return render(request, 'inventaire/form_article.html', {'titre': 'Ajouter un article'})


@responsable_stock_required
def modifier_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.nom = request.POST.get('nom')
        article.unite = request.POST.get('unite')
        article.quantite_disponible = request.POST.get('quantite_disponible')
        article.seuil_critique = request.POST.get('seuil_critique')
        article.prix_unitaire = request.POST.get('prix_unitaire')
        article.save()
        article.verifier_seuil()
        messages.success(request, 'Article modifié avec succès !')
        return redirect('detail_article', pk=article.pk)
    return render(request, 'inventaire/form_article.html', {
        'titre': 'Modifier un article',
        'article': article
    })


@responsable_stock_required
def supprimer_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article supprimé avec succès !')
        return redirect('liste_articles')
    return render(request, 'inventaire/confirmer_suppression.html', {'article': article})


# ─── MOUVEMENTS DE STOCK ───

@responsable_stock_required
def ajouter_mouvement(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        type_mouvement = request.POST.get('type')
        quantite = float(request.POST.get('quantite'))
        motif = request.POST.get('motif', '')
        MouvementStock.objects.create(
            article=article,
            type=type_mouvement,
            quantite=quantite,
            motif=motif
        )
        if type_mouvement == 'entree':
            article.quantite_disponible += quantite
        else:
            article.quantite_disponible -= quantite
        article.save()
        article.verifier_seuil()
        messages.success(request, 'Mouvement enregistré !')
        return redirect('detail_article', pk=article.pk)
    return render(request, 'inventaire/form_mouvement.html', {'article': article})


# ─── FOURNISSEURS ───

@login_required
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'inventaire/liste_fournisseurs.html', {'fournisseurs': fournisseurs})


@login_required
def creer_fournisseur(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email', '')
        adresse = request.POST.get('adresse', '')
        Fournisseur.objects.create(
            nom=nom,
            telephone=telephone,
            email=email,
            adresse=adresse
        )
        messages.success(request, 'Fournisseur ajouté avec succès !')
        return redirect('liste_fournisseurs')
    return render(request, 'inventaire/form_fournisseur.html', {'titre': 'Ajouter un fournisseur'})