from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from authentification.models import Employe
import datetime


def accueil(request):
    return render(request, 'acceuil.html')

def erreur(request, exception=None):
    return render(request, '404.html')

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        print(f"[DEBUG] email reçu: {email}")
        print(f"[DEBUG] password reçu: {password}")

        try:
            employe = Employe.objects.get(email__iexact=email)
            print(f"[DEBUG] utilisateur trouvé: {employe.username} | role: {employe.role}")
        except Employe.DoesNotExist:
            print(f"[DEBUG] aucun compte avec cet email")
            messages.error(request, "Aucun compte trouvé avec cet email.")
            return render(request, 'acceuil.html')

        user = authenticate(request, username=employe.username, password=password)
        print(f"[DEBUG] authenticate retourne: {user}")

        if user is not None and user.is_active:
            login(request, user)
            print(f"[DEBUG] connecté en tant que: {user.username} | role: {user.role}")
            return _redirect_by_role(user)
        else:
            messages.error(request, "Mot de passe incorrect.")

    return render(request, 'acceuil.html')


def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('accueil')


def _redirect_by_role(user):
    # L'administrateur système ou superutilisateur est redirigé vers la gestion des comptes
    if user.is_superuser or user.role == 'administrateur':
        return redirect('utilisateurs_gestion')

    role = getattr(user, 'role', None)
    print(f"[DEBUG] _redirect_by_role appelé avec role: {role}")

    redirections = {
        'administrateur':     'utilisateurs_gestion',
        'directeur':          'dashboard_directeur',
        'caissier':           'caissier',
        'chef_cuisinier':     'chef_cuisinier',
        'cuisinier':          'cuisinier',
        'livreur':            'livreur',
        'serveur':            'serveur',
        'responsable_stock':  'responsable_stock',
        'client':             'client',
    }
    url_name = redirections.get(role, 'accueil')
    return redirect(url_name)


@login_required
def caissier(request):
    return render(request, 'caissier.html')


@login_required
def chef_cuisinier(request):
    return render(request, 'chef_cuisinier.html')


@login_required
def livreur(request):
    return render(request, 'livreur.html')

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from commandes.models import Commande
from produits.models import Produit

@login_required
def serveur(request):
    # 1. Récupération des plats actifs
    produits_queryset = Produit.objects.filter(disponible=True).order_by('nom')
    produits_liste = list(produits_queryset.values('id', 'nom', 'prix'))
    
    # 2. Sérialisation en texte JSON pour le script JavaScript
    produits_json = json.dumps(produits_liste)

    # 3. Récupération des commandes récentes
    commandes_recentes = (
        Commande.objects
        .filter(serveur=request.user)
        .prefetch_related('lignes__produit')
        .order_by('-date_creation')[:20]
    )
    
    # 4. Compte des commandes actives
    nb_actives = (
        Commande.objects
        .filter(serveur=request.user, statut__in=['en_attente', 'en_preparation', 'prete'])
        .count()
    )

    # CORRECTION ICI : Assurez-vous qu'il n'y a aucun symbole '@' dans ce bloc de retour
    return render(request, 'serveur.html', {
        'produits': produits_json,           # Chaîne JSON lue par le bloc <script>
        'produits_boucle': produits_liste,   # Liste lue par la boucle {% for %} Django
        'commandes_recentes': commandes_recentes,
        'nb_actives': nb_actives,
    })
    
    
    
@login_required
def responsable_stock(request):
    return render(request, 'inventaire/detail_article.html')


@login_required
def client(request):
    return render(request, 'client.html')


def menu(request):
    return render(request, 'menu.html')


def a_propos(request):
    return render(request, 'apropos.html')


@login_required
def menu_client(request):
    return render(request, 'menu_client.html')


@login_required
def recettes(request):
    return render(request, 'recettes/liste_recettes.html')


@login_required
def inventaire(request):
    return render(request, 'inventaire/detail_article.html')


@login_required
def produits(request):
    return render(request, 'produits/liste_produits.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


@login_required
def panier(request):
    from commandes.models import Commande

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

    commandes_actives = (
        Commande.objects
        .filter(serveur=request.user, statut__in=['en_attente', 'en_preparation', 'prete'])
        .count()
    )
    total_depense = (
        Commande.objects
        .filter(serveur=request.user, statut='servie')
        .aggregate(total=Sum('montant_total'))['total'] or 0
    )

    return render(request, 'panier.html', {
        'commandes': commandes,
        'reservations': reservations,
        'commandes_actives': commandes_actives,
        'total_depense': total_depense,
    })


@login_required
def commande_ajouter(request):
    if request.method == 'POST':
        from commandes.models import Commande, LigneCommande
        from produits.models import Produit

        type_cmd      = request.POST.get('type_commande', 'sur_place')
        produit_ids   = request.POST.getlist('produit[]')
        quantites     = request.POST.getlist('quantite[]')

        commande = Commande.objects.create(
            serveur=request.user,
            type_commande=type_cmd,
            statut='en_attente',
            client_nom=request.user.get_full_name() or request.user.username,
            client_telephone=getattr(request.user, 'telephone', ''),
        )

        for prod_id, qte_str in zip(produit_ids, quantites):
            try:
                qte = int(qte_str)
                if qte <= 0:
                    continue
                produit = Produit.objects.get(pk=prod_id, disponible=True)
                LigneCommande.objects.create(
                    commande=commande,
                    produit=produit,
                    quantite=qte,
                    prix_unitaire=produit.prix,
                )
            except (Produit.DoesNotExist, ValueError, TypeError):
                continue

        commande.calculer_montant()
        messages.success(request, f"Commande #{commande.pk} passée avec succès — {commande.montant_total} FCFA.")

    return redirect('panier')


@login_required
def commande_annuler(request, cmd_id):
    if request.method == 'POST':
        from commandes.models import Commande
        try:
            commande = Commande.objects.get(pk=cmd_id, serveur=request.user)
            if commande.annuler():
                messages.success(request, f"Commande #{cmd_id} annulée.")
            else:
                messages.error(request, "Impossible d'annuler cette commande.")
        except Commande.DoesNotExist:
            messages.error(request, "Commande introuvable.")
    return redirect('panier')


@login_required
def recommander(request, cmd_id):
    messages.success(request, "Commande re-passée avec succès !")
    return redirect('panier')


@login_required
def commande_marquer_servie(request, cmd_id):
    if request.method == 'POST':
        messages.success(request, f"Commande #{cmd_id} marquée comme servie.")
    return redirect('serveur')


@login_required
def commande_facture(request, cmd_id):
    return render(request, 'serveur.html')


@login_required
def reservation_creer(request):
    if request.method == 'POST':
        messages.success(request, "Réservation confirmée.")
    return redirect('serveur')


@login_required
def reservation_annuler(request, res_id):
    if request.method == 'POST':
        messages.success(request, f"Réservation #{res_id} annulée.")
    return redirect('panier')


def inscription_client(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        if not email or not password or not first_name or not last_name:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'inscription.html')

        if Employe.objects.filter(email__iexact=email).exists():
            messages.error(request, "Cet e-mail est déjà utilisé.")
            return render(request, 'inscription.html')

        username = f"client.{first_name.lower().replace(' ', '_')}.{last_name.lower().replace(' ', '_')}"
        base_username = username
        counter = 1
        while Employe.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = Employe.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='client',
            telephone=telephone
        )
        login(request, user)
        messages.success(request, f"Bienvenue chez KMER FOOD, {user.first_name} ! Votre compte a été créé avec succès.")
        return redirect('client')

    return render(request, 'inscription.html')


@login_required
def utilisateurs_gestion(request):
    if not (request.user.is_superuser or request.user.role == 'administrateur'):
        return redirect('accueil')

    action = request.GET.get('action')
    user_id = request.GET.get('id')

    if request.method == 'POST':
        if action == 'creer':
            email = request.POST.get('email', '').strip().lower()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            role = request.POST.get('role', 'serveur')
            telephone = request.POST.get('telephone', '').strip()
            adresse = request.POST.get('adresse', '').strip()

            if not email or not username or not password or not first_name or not last_name:
                messages.error(request, "Veuillez remplir tous les champs requis.")
            elif Employe.objects.filter(email__iexact=email).exists():
                messages.error(request, "Cet e-mail est déjà associé à un compte.")
            elif Employe.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            else:
                user = Employe.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    telephone=telephone,
                    adresse=adresse
                )
                if role != 'client':
                    from rh.models import Personnel
                    Personnel.objects.create(
                        utilisateur=user,
                        poste=role,
                        salaire_base=1000,
                        date_embauche=datetime.date.today(),
                        telephone=telephone,
                        adresse=adresse
                    )
                messages.success(request, f"Utilisateur {username} créé avec succès.")
                return redirect('utilisateurs_gestion')

        elif action == 'modifier' and user_id:
            user = get_object_or_404(Employe, pk=user_id)
            user.email = request.POST.get('email', '').strip().lower()
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.role = request.POST.get('role', user.role)
            user.telephone = request.POST.get('telephone', '').strip()
            user.adresse = request.POST.get('adresse', '').strip()
            user.is_active = request.POST.get('is_active') == 'on'

            new_password = request.POST.get('password', '').strip()
            if new_password:
                user.set_password(new_password)

            user.save()
            messages.success(request, f"Compte {user.username} mis à jour.")
            return redirect('utilisateurs_gestion')

    if action == 'supprimer' and user_id:
        user = get_object_or_404(Employe, pk=user_id)
        if user.id != request.user.id:
            user.delete()
            messages.success(request, f"Compte {user.username} définitivement supprimé.")
        else:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('utilisateurs_gestion')

    if action == 'deactiver' and user_id:
        user = get_object_or_404(Employe, pk=user_id)
        user.is_active = False
        user.save()
        messages.success(request, f"Compte {user.username} désactivé.")
        return redirect('utilisateurs_gestion')

    if action == 'activer' and user_id:
        user = get_object_or_404(Employe, pk=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f"Compte {user.username} activé.")
        return redirect('utilisateurs_gestion')

    utilisateurs = Employe.objects.all().order_by('-date_joined')
    roles_list = Employe.ROLES
    return render(request, 'admin_utilisateurs.html', {
        'utilisateurs': utilisateurs,
        'roles_list': roles_list
    })


@login_required
def cuisinier(request):
    if request.user.role not in ['chef_cuisinier', 'cuisinier'] and not request.user.is_superuser:
        return redirect('accueil')
        
    from commandes.models import Commande
    from recettes.models import Recette
    commandes_actives = Commande.objects.filter(statut__in=['en_attente', 'en_preparation']).order_by('date_creation')
    recettes_liste = Recette.objects.all()

    return render(request, 'cuisinier.html', {
        'commandes_actives': commandes_actives,
        'recettes_liste': recettes_liste
    })
