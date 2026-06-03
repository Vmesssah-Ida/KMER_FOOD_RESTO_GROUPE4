from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentification.models import Employe


def accueil(request):
    return render(request, 'acceuil.html')


def login_view(request):
    # Si déjà connecté, redirige
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        print(f"[DEBUG] email reçu: {email}")
        print(f"[DEBUG] password reçu: {password}")

        # Cherche l'employé par email
        try:
            employe = Employe.objects.get(email__iexact=email)
            print(f"[DEBUG] utilisateur trouvé: {employe.username} | role: {employe.role}")
        except Employe.DoesNotExist:
            print(f"[DEBUG] aucun compte avec cet email")
            messages.error(request, "Aucun compte trouvé avec cet email.")
            return render(request, 'acceuil.html')

        # Authentifie
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
    logout(request)
    return redirect('accueil')


def _redirect_by_role(user):
    role = getattr(user, 'role', None)
    print(f"[DEBUG] _redirect_by_role appelé avec role: {role}")

    redirections = {
        'directeur':          'dashboard_directeur',
        'caissier':           'caissier',
        'chef_cuisinier':     'chef_cuisinier',
        'livreur':            'livreur',
        'serveur':            'serveur',
        'responsable_stock':  'responsable_stock',
        'client':             'client',
    }
    url_name = redirections.get(role, 'accueil')
    return redirect(url_name)


@login_required
def dashboard_directeur(request):
    return render(request, 'dashboard_directeur.html')

@login_required
def caissier(request):
    return render(request, 'caissier.html')

@login_required
def chef_cuisinier(request):
    return render(request, 'chef_cuisinier.html')

@login_required
def livreur(request):
    return render(request, 'livreur.html')

@login_required
def serveur(request):
    return render(request, 'serveur.html')

@login_required
def responsable_stock(request):
    return render(request, 'responsable_stock.html')

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
    return render(request, 'liste_recettes.html')
@login_required
def inventaire(request):
    return render(request, 'detail_article.html')
@login_required
def produits(request):
    return render(request, 'liste_produits.html')
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')



@login_required
def panier(request):
    from django.db import connection
    commandes, reservations = [], []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id_Commande, c.Date, c.Type, c.Montant_Total,
                   c.Mode_de_Paiement, 'En attente' as statut
            FROM Commande c
            JOIN authentification_employe ae ON ae.email = %s
            JOIN Client cl ON cl.Email = ae.email
            WHERE c.id_Client = cl.id_Client
            ORDER BY c.Date DESC
        """, [request.user.email])
        commandes = [
            {'id_Commande': r[0], 'Date': r[1], 'Type': r[2],
             'Montant_Total': r[3], 'Mode_de_Paiement': r[4], 'statut': r[5]}
            for r in cursor.fetchall()
        ]
        cursor.execute("""
            SELECT r.id_Reservation, r.Date, r.Heure, r.Statut, t.Numero_Table
            FROM Reservation r
            JOIN Client cl ON r.id_Client = cl.id_Client
            JOIN `Table` t ON r.id_Table = t.id_Table
            WHERE cl.Email = %s
            ORDER BY r.Date DESC
        """, [request.user.email])
        reservations = [
            {'id_Reservation': r[0], 'Date': r[1], 'Heure': r[2],
             'Statut': r[3], 'Numero_Table': r[4]}
            for r in cursor.fetchall()
        ]
    return render(request, 'panier.html', {
        'commandes': commandes,
        'reservations': reservations,
        'commandes_actives': sum(1 for c in commandes if c['statut'] in ['En attente','En cours']),
        'total_depense': sum(c['Montant_Total'] or 0 for c in commandes),
    })

@login_required
def commande_ajouter(request):
    if request.method == 'POST':
        messages.success(request, "Commande passée avec succès !")
    return redirect('panier')

@login_required
def commande_annuler(request, cmd_id):
    if request.method == 'POST':
        messages.success(request, f"Commande #{cmd_id} annulée.")
    return redirect('panier')

@login_required
def recommander(request, cmd_id):
    messages.success(request, "Commande re-passée avec succès !")
    return redirect('panier')

@login_required
def commande_creer(request):
    if request.method == 'POST':
        from django.db import connection
        type_cmd  = request.POST.get('type_commande')
        paiement  = request.POST.get('mode_paiement')
        produits  = request.POST.getlist('produit[]')
        quantites = request.POST.getlist('quantite[]')

        # Cherche le client par email ou crée une commande anonyme
        client_email = request.POST.get('client_email', '').strip()
        id_client = None
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_Client FROM Client WHERE Email=%s", [client_email])
            row = cursor.fetchone()
            if row: id_client = row[0]

        if not id_client:
            messages.error(request, "Client introuvable. Vérifiez l'email.")
            return redirect('serveur')

        # Calcul montant total
        total = 0
        lignes = []
        with connection.cursor() as cursor:
            for prod_id, qte in zip(produits, quantites):
                if not prod_id: continue
                cursor.execute("SELECT id_Produit FROM Produit WHERE id_Produit=%s", [prod_id])
                prod = cursor.fetchone()
                # Prix fixe temporaire — à relier à la table Produit quand les prix seront ajoutés
                prix = 5000
                qte = int(qte)
                total += prix * qte
                lignes.append((prod_id, qte, prix))

        with connection.cursor() as cursor:
            from datetime import datetime
            cursor.execute("""
                INSERT INTO Commande (id_Client, Date, Type, Montant_Total, Mode_de_Paiement)
                VALUES (%s, %s, %s, %s, %s)
            """, [id_client, datetime.now(), type_cmd, total, paiement])
            id_commande = cursor.lastrowid

            for prod_id, qte, prix in lignes:
                cursor.execute("""
                    INSERT INTO Ligne_Commande (id_Commande, id_Produit, Quantite, Prix_Unitaire)
                    VALUES (%s, %s, %s, %s)
                """, [id_commande, prod_id, qte, prix])

        messages.success(request, f"Commande #{id_commande} créée — {total} FCFA")
    return redirect('serveur')


@login_required
def commande_marquer_servie(request, cmd_id):
    if request.method == 'POST':
        messages.success(request, f"Commande #{cmd_id} marquée comme servie.")
    return redirect('serveur')


@login_required
def commande_annuler(request, cmd_id):
    if request.method == 'POST':
        messages.success(request, f"Commande #{cmd_id} annulée.")
    return redirect('serveur')


@login_required
def commande_facture(request, cmd_id):
    return render(request, 'serveur.html')  # À remplacer par une vraie page facture


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