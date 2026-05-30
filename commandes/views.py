from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Commande, LigneCommande
from produits.models import Produit

@login_required
def commande_creer(request):
    produits = Produit.objects.filter(disponible=True)
    if request.method == 'POST':
        type_commande = request.POST.get('type_commande', 'sur_place')
        commande = Commande.objects.create(serveur=request.user, type_commande=type_commande)
        produit_ids = request.POST.getlist('produit_id')
        quantites   = request.POST.getlist('quantite')
        for pid, qte in zip(produit_ids, quantites):
            try:
                produit = Produit.objects.get(pk=pid)
                qte = int(qte)
                if qte > 0:
                    LigneCommande.objects.create(commande=commande, produit=produit, quantite=qte, prix_unitaire=produit.prix)
            except (Produit.DoesNotExist, ValueError):
                continue
        commande.calculer_montant()
        messages.success(request, "Commande créée avec succès.")
        return redirect('commande_facture', cmd_id=commande.pk)
    return render(request, 'commandes/commande_creer.html', {'produits': produits})

@login_required
def commande_annuler(request, cmd_id):
    commande = get_object_or_404(Commande, pk=cmd_id)
    if commande.peut_etre_annulee():
        commande.statut = 'annulee'
        commande.save()
        messages.success(request, "Commande annulée.")
    else:
        messages.error(request, "Cette commande ne peut plus être annulée.")
    return redirect('commande_ajouter')

@login_required
def commande_marquer_servie(request, cmd_id):
    commande = get_object_or_404(Commande, pk=cmd_id)
    commande.statut = 'servie'
    commande.save()
    messages.success(request, "Commande marquée comme servie.")
    return redirect('commande_ajouter')

@login_required
def commande_facture(request, cmd_id):
    commande = get_object_or_404(Commande, pk=cmd_id)
    lignes   = commande.lignes.select_related('produit').all()
    return render(request, 'commandes/facture.html', {'commande': commande, 'lignes': lignes})

@login_required
def commande_ajouter(request):
    commandes = Commande.objects.filter(statut__in=['en_attente', 'en_preparation']).prefetch_related('lignes__produit')
    return render(request, 'commandes/liste_commandes.html', {'commandes': commandes})
