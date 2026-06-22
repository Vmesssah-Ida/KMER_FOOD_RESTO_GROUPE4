# commandes/views.py
# Module 4 — Gestion des commandes · KMER FOOD RESTO
#
# Règles métier appliquées :
#   1. Une commande doit contenir au moins un produit
#   2. Montant calculé automatiquement
#   3. Annulation uniquement si statut == 'en_attente'
#   4. Toute validation déclenche la mise à jour du stock
#   5. Vérification du stock avant validation (commande rejetée si rupture)
#   6. Accès limité selon le rôle (login_required sur toutes les vues)

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Sum

from .models import Commande, LigneCommande
from produits.models import Produit

try:
    from inventaire.models import Article
    STOCK_DISPONIBLE = True
except ImportError:
    STOCK_DISPONIBLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Vue 1 : Liste des commandes actives
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_liste(request):
    commandes = (
        Commande.objects
        .filter(statut__in=['en_attente', 'en_preparation', 'prete'])
        .prefetch_related('lignes__produit')
        .select_related('serveur')
        .order_by('-date_creation')
    )
    return render(request, 'commandes/liste_commandes.html', {
        'commandes': commandes,
        'titre': 'Commandes en cours',
        'now': timezone.now(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 2 : Créer une commande
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_creer(request):
    produits = Produit.objects.filter(disponible=True).order_by('categorie', 'nom')

    if request.method == 'POST':
        type_commande     = request.POST.get('type_commande', 'sur_place')
        numero_table      = request.POST.get('numero_table', '').strip()
        note_cuisine      = request.POST.get('note_cuisine', '').strip()
        client_nom        = request.POST.get('client_nom', '').strip()
        client_telephone  = request.POST.get('client_telephone', '').strip()
        adresse_livraison = request.POST.get('adresse_livraison', '').strip()

        if type_commande == 'livraison' and not client_nom:
            messages.error(request, "Le nom du client est obligatoire pour une livraison.")
            return render(request, 'commandes/commande_creer.html', {'produits': produits, 'post': request.POST})

        if type_commande == 'livraison' and not adresse_livraison:
            messages.error(request, "L'adresse de livraison est obligatoire.")
            return render(request, 'commandes/commande_creer.html', {'produits': produits, 'post': request.POST})

        produit_ids = request.POST.getlist('produit_id[]') or request.POST.getlist('produit_id')
        quantites   = request.POST.getlist('quantite[]')   or request.POST.getlist('quantite')

        lignes_valides = []
        for pid, qte_str in zip(produit_ids, quantites):
            try:
                qte = int(qte_str)
                if qte <= 0:
                    continue
                produit = Produit.objects.get(pk=pid, disponible=True)
                lignes_valides.append({'produit': produit, 'quantite': qte})
            except (Produit.DoesNotExist, ValueError, TypeError):
                continue

        if not lignes_valides:
            messages.error(request, "La commande doit contenir au moins un produit.")
            return render(request, 'commandes/commande_creer.html', {'produits': produits, 'post': request.POST})

        if STOCK_DISPONIBLE:
            from inventaire.models import Article
            erreurs_stock = []
            ingredients_requis = {}
            for ligne in lignes_valides:
                produit = ligne['produit']
                if hasattr(produit, 'recette') and produit.recette:
                    for ri in produit.recette.recetteingredient_set.all():
                        nom_ing = ri.ingredient.nom
                        qte_necessaire = ri.quantite * ligne['quantite']
                        ingredients_requis[nom_ing] = ingredients_requis.get(nom_ing, 0.0) + qte_necessaire
            for nom_ing, qte_necessaire in ingredients_requis.items():
                try:
                    article = Article.objects.get(nom__iexact=nom_ing)
                    if article.quantite_disponible < qte_necessaire:
                        erreurs_stock.append(
                            f"Stock insuffisant : {nom_ing} "
                            f"(disponible : {article.quantite_disponible}, requis : {qte_necessaire})"
                        )
                except Article.DoesNotExist:
                    erreurs_stock.append(f"Stock introuvable pour : {nom_ing}")
            if erreurs_stock:
                for err in erreurs_stock:
                    messages.error(request, err)
                return render(request, 'commandes/commande_creer.html', {
                    'produits': produits, 'post': request.POST, 'erreurs_stock': erreurs_stock,
                })

        commande = Commande.objects.create(
            serveur=request.user,
            type_commande=type_commande,
            statut='en_attente',
            numero_table=numero_table or None,
            note_cuisine=note_cuisine,
            client_nom=client_nom,
            client_telephone=client_telephone,
            adresse_livraison=adresse_livraison,
        )

        for ligne in lignes_valides:
            LigneCommande.objects.create(
                commande=commande,
                produit=ligne['produit'],
                quantite=ligne['quantite'],
                prix_unitaire=ligne['produit'].prix,
            )

        commande.calculer_montant()

        # Les stocks ne sont décrémentés que lors du passage en préparation (validation)
        pass

        messages.success(request, f"Commande #{commande.pk} créée — {commande.montant_total} FCFA.")

        if hasattr(request.user, 'profil') and getattr(request.user.profil, 'role', '') == 'client':
            return redirect('panier')
        return redirect('commandes:commande_facture', cmd_id=commande.pk)

    return render(request, 'commandes/commande_creer.html', {
        'produits': produits,
        'titre': 'Nouvelle commande',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 3 : Facture
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_facture(request, cmd_id):
    commande = get_object_or_404(Commande, pk=cmd_id)
    lignes   = commande.lignes.select_related('produit').all()
    return render(request, 'commandes/facture.html', {
        'commande': commande,
        'lignes':   lignes,
        'titre':    f'Facture — Commande #{commande.pk}',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 4 : Passer en préparation
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_en_preparation(request, cmd_id):
    if request.method != 'POST':
        return redirect('commandes:commande_liste')
    commande = get_object_or_404(Commande, pk=cmd_id)
    
    # 1. Vérifier les stocks d'ingrédients avant validation
    if STOCK_DISPONIBLE:
        is_ok, erreurs = _verifier_stock_disponible(commande)
        if not is_ok:
            for err in erreurs:
                messages.error(request, err)
            return redirect('commandes:commande_liste')
            
    # 2. Passage du statut de en_attente à en_preparation
    if commande.passer_en_preparation():
        # 3. Décrémenter les stocks et enregistrer le mouvement
        if STOCK_DISPONIBLE:
            _decrementer_stock(commande)
            
        # 4. Générer automatiquement la facture lors de la validation
        from commandes.models import Facture
        Facture.objects.get_or_create(
            commande=commande,
            defaults={
                'montant': commande.montant_total,
                'est_valide': True
            }
        )
        messages.success(request, f"Commande #{commande.pk} passée en préparation et facture générée.")
    else:
        messages.error(request, f"Impossible (statut actuel : {commande.get_statut_display()}).")
    return redirect('commandes:commande_liste')


# ─────────────────────────────────────────────────────────────────────────────
# Vue 5 : Marquer servie
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_marquer_servie(request, cmd_id):
    if request.method != 'POST':
        return redirect('commandes:commande_liste')
    commande = get_object_or_404(Commande, pk=cmd_id)
    if commande.marquer_servie():
        messages.success(request, f"Commande #{commande.pk} marquée comme servie.")
    else:
        messages.error(request, f"Impossible (statut : {commande.get_statut_display()}).")
    return redirect('commandes:commande_liste')


# ─────────────────────────────────────────────────────────────────────────────
# Vue 6 : Annuler
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_annuler(request, cmd_id):
    if request.method != 'POST':
        return redirect('commandes:commande_liste')
    commande = get_object_or_404(Commande, pk=cmd_id)
    if commande.annuler():
        messages.success(request, f"Commande #{commande.pk} annulée.")
    else:
        messages.error(request, f"Impossible d'annuler (statut : {commande.get_statut_display()}).")
    if hasattr(request.user, 'profil') and getattr(request.user.profil, 'role', '') == 'client':
        return redirect('panier')
    return redirect('commandes:commande_liste')


# ─────────────────────────────────────────────────────────────────────────────
# Vue 7 : Historique complet
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def commande_historique(request):
    commandes = (
        Commande.objects.all()
        .prefetch_related('lignes__produit')
        .select_related('serveur')
        .order_by('-date_creation')
    )
    statut     = request.GET.get('statut', '')
    type_c     = request.GET.get('type_commande', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin   = request.GET.get('date_fin', '')

    if statut:
        commandes = commandes.filter(statut=statut)
    if type_c:
        commandes = commandes.filter(type_commande=type_c)
    if date_debut:
        commandes = commandes.filter(date_creation__date__gte=date_debut)
    if date_fin:
        commandes = commandes.filter(date_creation__date__lte=date_fin)

    total_ca = sum(c.montant_total for c in commandes if c.statut == 'servie')

    return render(request, 'commandes/historique.html', {
        'commandes': commandes,
        'titre': 'Historique des commandes',
        'total_ca': total_ca,
        'statut_choices': Commande.STATUT_CHOICES,
        'type_choices':   Commande.TYPE_CHOICES,
        'filtres': {
            'statut': statut, 'type_commande': type_c,
            'date_debut': date_debut, 'date_fin': date_fin,
        },
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 8 : Accueil client (landing page)
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def client_accueil(request):
    specialites = Produit.objects.filter(disponible=True).order_by('?')[:4]
    nb_produits = Produit.objects.filter(disponible=True).count()
    return render(request, 'client/client.html', {
        'specialites': specialites,
        'nb_produits': nb_produits,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 9 : Menu client (liste des produits avec catégories)
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def menu_client(request):
    produits = (
        Produit.objects
        .filter(disponible=True)
        .order_by('categorie', 'nom')
    )
    return render(request, 'client/menu_client.html', {
        'produits': produits,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Vue 10 : Panier / suivi des commandes client
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def panier_client(request):
    commandes = (
        Commande.objects
        .filter(serveur=request.user)
        .prefetch_related('lignes__produit')
        .order_by('-date_creation')
    )

    reservations = []
    try:
        from reservations.models import Reservation
        reservations = Reservation.objects.filter(client=request.user).order_by('-date_reservation')
    except Exception:
        pass

    commandes_actives = commandes.filter(statut__in=['en_attente', 'en_preparation', 'prete']).count()
    total_depense = (
        commandes
        .filter(statut='servie')
        .aggregate(total=Sum('montant_total'))['total'] or 0
    )

    return render(request, 'client/panier.html', {
        'commandes': commandes,
        'reservations': reservations,
        'commandes_actives': commandes_actives,
        'total_depense': total_depense,
    })


# ═════════════════════════════════════════════════════════════════════════════
# API JSON — Communication temps réel entre modules
# ═════════════════════════════════════════════════════════════════════════════

@login_required
def api_cuisine(request):
    """
    GET /commandes/api/cuisine/
    Retourne les commandes actives au format JSON pour le chef cuisinier.
    Interrogé toutes les 5 secondes par le template chef_cuisinier.html.
    """
    commandes = (
        Commande.objects
        .filter(statut__in=['en_attente', 'en_preparation'])
        .prefetch_related('lignes__produit')
        .order_by('date_creation')
    )
    data = []
    for cmd in commandes:
        lignes = [
            {'nom': l.produit.nom, 'quantite': l.quantite}
            for l in cmd.lignes.all()
        ]
        minutes = int((timezone.now() - cmd.date_creation).total_seconds() / 60)
        label_table = cmd.numero_table if cmd.numero_table else (
            f"Livraison — {cmd.client_nom}" if cmd.type_commande == 'livraison' else 'À emporter'
        )
        data.append({
            'id': cmd.pk,
            'statut': cmd.statut,
            'statut_display': cmd.get_statut_display(),
            'type_commande': cmd.type_commande,
            'label_table': label_table,
            'note_cuisine': cmd.note_cuisine or '',
            'lignes': lignes,
            'heure': cmd.date_creation.strftime('%H:%M'),
            'minutes': minutes,
            'urgent': minutes >= 20,
        })
    return JsonResponse({'commandes': data, 'total': len(data)})


@login_required
def api_preparer(request, cmd_id):
    """
    POST /commandes/api/<id>/preparer/
    Transition en_attente → en_preparation (chef accepte le ticket).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    commande = get_object_or_404(Commande, pk=cmd_id)
    success = commande.passer_en_preparation()
    return JsonResponse({'success': success, 'statut': commande.statut, 'id': cmd_id})


@login_required
def api_servir(request, cmd_id):
    """
    POST /commandes/api/<id>/servir/
    Transition en_preparation → prete (ticket prêt, visible serveur et livreur).
    Utilisée par le chef cuisinier via le bouton "Ticket prêt".
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    commande = get_object_or_404(Commande, pk=cmd_id)
    success = commande.marquer_prete()
    return JsonResponse({'success': success, 'statut': commande.statut, 'id': cmd_id})


@login_required
def api_serveur(request):
    """
    GET /commandes/api/serveur/
    Retourne les commandes 'prete' de type sur_place ou a_emporter pour le serveur.
    Interrogé toutes les 5 secondes par le template serveur.html.
    """
    commandes = (
        Commande.objects
        .filter(statut='prete', type_commande__in=['sur_place', 'a_emporter'])
        .prefetch_related('lignes__produit')
        .order_by('date_creation')
    )
    data = []
    for cmd in commandes:
        lignes = [
            {'nom': l.produit.nom, 'quantite': l.quantite}
            for l in cmd.lignes.all()
        ]
        data.append({
            'id': cmd.pk,
            'statut': cmd.statut,
            'statut_display': cmd.get_statut_display(),
            'type_commande': cmd.type_commande,
            'label_table': cmd.numero_table or 'À emporter',
            'note_cuisine': cmd.note_cuisine or '',
            'lignes': lignes,
            'heure': cmd.date_creation.strftime('%H:%M'),
            'montant_total': float(cmd.montant_total),
        })
    return JsonResponse({'commandes': data, 'total': len(data)})


@login_required
def api_serveur_servir(request, cmd_id):
    """
    POST /commandes/api/<id>/serveur-servir/
    Transition prete → servie (serveur remet la commande au client en salle).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    commande = get_object_or_404(Commande, pk=cmd_id, type_commande__in=['sur_place', 'a_emporter'])
    success = commande.marquer_servie()
    return JsonResponse({'success': success, 'statut': commande.statut, 'id': cmd_id})


@login_required
def api_caisse(request):
    """
    GET /commandes/api/caisse/
    Retourne les commandes servies non encore clôturées pour le caissier.
    Interrogé toutes les 5 secondes par le template caissier.html.
    """
    commandes = (
        Commande.objects
        .filter(statut='servie')
        .prefetch_related('lignes__produit')
        .order_by('-date_creation')[:60]
    )
    data = []
    for cmd in commandes:
        lignes = [
            {
                'nom': l.produit.nom,
                'quantite': l.quantite,
                'prix_unitaire': float(l.prix_unitaire),
                'sous_total': float(l.sous_total()),
            }
            for l in cmd.lignes.all()
        ]
        label = (
            f"Table {cmd.numero_table}" if cmd.numero_table
            else (f"Livraison — {cmd.client_nom}" if cmd.type_commande == 'livraison'
                  else 'À emporter')
        )
        data.append({
            'id': cmd.pk,
            'label': label,
            'type_commande': cmd.type_commande,
            'montant_total': float(cmd.montant_total),
            'lignes': lignes,
            'heure': cmd.date_creation.strftime('%H:%M'),
        })
    return JsonResponse({'commandes': data, 'total': len(data)})


@login_required
def api_livraisons(request):
    """
    GET /commandes/api/livraisons/
    Retourne les commandes de type livraison pour le livreur.
    Affiche les livraisons en cours de préparation ET prêtes à livrer.
    Interrogé toutes les 5 secondes par le template livreur.html.
    """
    commandes = (
        Commande.objects
        .filter(type_commande='livraison', statut__in=['en_attente', 'en_preparation', 'prete'])
        .prefetch_related('lignes__produit')
        .order_by('date_creation')
    )
    data = []
    for cmd in commandes:
        lignes = [
            {'nom': l.produit.nom, 'quantite': l.quantite}
            for l in cmd.lignes.all()
        ]
        minutes = int((timezone.now() - cmd.date_creation).total_seconds() / 60)
        data.append({
            'id': cmd.pk,
            'statut': cmd.statut,
            'statut_display': cmd.get_statut_display(),
            'client_nom': cmd.client_nom,
            'client_telephone': cmd.client_telephone,
            'adresse_livraison': cmd.adresse_livraison,
            'montant_total': float(cmd.montant_total),
            'lignes': lignes,
            'heure': cmd.date_creation.strftime('%H:%M'),
            'minutes': minutes,
            'en_retard': minutes >= 45,
        })
    return JsonResponse({'livraisons': data, 'total': len(data)})


@login_required
def api_livrer(request, cmd_id):
    """
    POST /commandes/api/<id>/livrer/
    Marquer une livraison comme effectuée : prete → servie (appelée par le livreur).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    commande = get_object_or_404(Commande, pk=cmd_id, type_commande='livraison')
    success = commande.marquer_servie()
    return JsonResponse({'success': success, 'statut': commande.statut, 'id': cmd_id})


@login_required
def api_mes_commandes(request):
    """
    GET /commandes/api/mes-commandes/
    Retourne le statut actuel des commandes actives du client connecté.
    Interrogé toutes les 8 secondes par le template panier.html.
    """
    commandes = (
        Commande.objects
        .filter(
            serveur=request.user,
            statut__in=['en_attente', 'en_preparation', 'prete', 'servie'],
        )
        .values('pk', 'statut')
        .order_by('-date_creation')[:20]
    )
    data = [{'id': c['pk'], 'statut': c['statut']} for c in commandes]
    return JsonResponse({'commandes': data})


# ─────────────────────────────────────────────────────────────────────────────
# Helpers privés (logique de stock)
# ─────────────────────────────────────────────────────────────────────────────
def _verifier_stock_disponible(commande):
    from inventaire.models import Article
    erreurs = []
    ingredients_requis = {}
    for ligne in commande.lignes.select_related('produit').all():
        produit = ligne.produit
        if not (hasattr(produit, 'recette') and produit.recette):
            continue
        for ri in produit.recette.recetteingredient_set.select_related('ingredient').all():
            nom_ing = ri.ingredient.nom
            qte_necessaire = ri.quantite * ligne.quantite
            ingredients_requis[nom_ing] = ingredients_requis.get(nom_ing, 0.0) + qte_necessaire

    for nom_ing, qte_necessaire in ingredients_requis.items():
        try:
            article = Article.objects.get(nom__iexact=nom_ing)
            if article.quantite_disponible < qte_necessaire:
                erreurs.append(
                    f"Stock insuffisant : {nom_ing} "
                    f"(disponible : {article.quantite_disponible} {article.unite}, requis : {qte_necessaire} {article.unite})"
                )
        except Article.DoesNotExist:
            erreurs.append(f"Article '{nom_ing}' introuvable dans l'inventaire.")

    return len(erreurs) == 0, erreurs


def _decrementer_stock(commande):
    from inventaire.models import Article, MouvementStock
    for ligne in commande.lignes.select_related('produit').all():
        produit = ligne.produit
        if not (hasattr(produit, 'recette') and produit.recette):
            continue
        for ri in produit.recette.recetteingredient_set.select_related('ingredient').all():
            qte_a_retirer = ri.quantite * ligne.quantite
            try:
                article = Article.objects.get(nom__iexact=ri.ingredient.nom)
                article.quantite_disponible = max(0.0, article.quantite_disponible - qte_a_retirer)
                article.save(update_fields=['quantite_disponible'])
                article.verifier_seuil()
                
                # Créer le mouvement de stock lié à la commande
                MouvementStock.objects.create(
                    article=article,
                    type='sortie',
                    quantite=qte_a_retirer,
                    motif=f"Validation commande #{commande.pk}",
                    commande=commande
                )
            except Article.DoesNotExist:
                pass
