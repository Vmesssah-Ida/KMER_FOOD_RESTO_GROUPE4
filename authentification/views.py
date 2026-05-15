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