# import_utilisateurs.py
# Lance avec : python manage.py shell < import_utilisateurs.py

import django
from django.db import connection
from authentification.models import Employe

# ── Correspondance Poste → rôle Django ──
POSTE_VERS_ROLE = {
    'Directeur General':      'directeur',
    'Chef Cuisinier':         'chef_cuisinier',
    'Cuisinier':              'chef_cuisinier',
    'Serveur':                'serveur',
    'Chauffeur':              'livreur',
    'Comptable':              'caissier',
    'Gestionnaire de Stock':  'responsable_stock',
    'Chef du Magasin':        'responsable_stock',
    'Responsable des Achats': 'responsable_stock',
    'Technicien':             'serveur',
    'Agent de Marketing':     'serveur',
    'Agent Téléphonique':     'serveur',
    'Agent de Sécurité':      'serveur',
}

print("\n========== IMPORT EMPLOYÉS ==========")

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT e.id_Employe, e.Nom, e.Prenom, e.Tel, p.Libelle_Poste
        FROM Employe e
        JOIN Affectation a ON e.id_Employe = a.id_Employe
        JOIN Poste p ON a.id_Poste = p.id_Poste
        WHERE a.Date_fin IS NULL
    """)
    employes = cursor.fetchall()

for id_emp, nom, prenom, tel, poste in employes:
    username = f"{prenom.lower().replace(' ', '_')}.{nom.lower().replace(' ', '_')}"
    email    = f"{username}@kmer.cm"
    role     = POSTE_VERS_ROLE.get(poste, 'serveur')
    password = 'kmer2026'

    if Employe.objects.filter(username=username).exists():
        print(f"  ⏭  {username} existe déjà — ignoré")
        continue

    emp = Employe.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=prenom,
        last_name=nom,
        role=role,
        telephone=tel,
    )
    print(f"  ✅ {emp.username} | {poste} → role={role}")

print("\n========== IMPORT CLIENTS ==========")

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT id_Client, Nom, Prenom, Tel, Email
        FROM Client
        WHERE Email IS NOT NULL AND Email != ''
    """)
    clients = cursor.fetchall()

for id_cl, nom, prenom, tel, email in clients:
    username = f"client.{prenom.lower().replace(' ', '_')}.{nom.lower().replace(' ', '_')}"

    if Employe.objects.filter(username=username).exists():
        print(f"  ⏭  {username} existe déjà — ignoré")
        continue

    if Employe.objects.filter(email=email).exists():
        print(f"  ⏭  email {email} déjà utilisé — ignoré")
        continue

    emp = Employe.objects.create_user(
        username=username,
        email=email,
        password='kmer2026',
        first_name=prenom,
        last_name=nom,
        role='client',
        telephone=tel,
    )
    print(f"  ✅ {emp.username} | role=client")

print("\n========== RÉSUMÉ ==========")
print(f"Total comptes Django : {Employe.objects.count()}")
for role_code, role_label in Employe.ROLES:
    count = Employe.objects.filter(role=role_code).count()
    if count:
        print(f"  {role_label:25s} : {count}")

print("\nMot de passe par défaut : kmer2026")
print("Demande à chaque utilisateur de changer son mot de passe à la première connexion.\n")
