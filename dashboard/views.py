from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from commandes.models import Commande
from produits.models import Produit
from inventaire.models import Article


@login_required
def dashboard(request):
    # Statistiques
    total_commandes = Commande.objects.count()
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    total_produits = Produit.objects.count()
    alertes_stock = Article.objects.filter(alerte=True).count()
    
    # Top produits
    top_produits = Produit.objects.annotate(
        nb_commandes=Count('lignecommande')
    ).order_by('-nb_commandes')[:5]
    
    # Articles en alerte
    articles_alerte = Article.objects.filter(alerte=True)

    return render(request, 'dashboard/dashboard.html', {
        'total_commandes': total_commandes,
        'commandes_en_attente': commandes_en_attente,
        'total_produits': total_produits,
        'alertes_stock': alertes_stock,
        'top_produits': top_produits,
        'articles_alerte': articles_alerte,
    })
@login_required
def commande_facture(request, cmd_id):
    commande = get_object_or_404(Commande, pk=cmd_id)
    lignes   = commande.lignes.select_related('produit').all()
    return render(request, 'commandes/facture.html', {
        'commande': commande,
        'lignes':   lignes,
        'titre':    f'Facture — Commande #{commande.pk}',
    })

