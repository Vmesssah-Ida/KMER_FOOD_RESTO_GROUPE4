# KMER FOOD — Système de Gestion de Restaurant

> **KMER FOOD** est une application web complète de gestion de restaurant camerounais, développée avec Django. Elle couvre l'ensemble du cycle opérationnel : de la prise de commande à la gestion de la caisse, en passant par le suivi des stocks et l'analyse des ventes.

---

## Table des matières

- [Aperçu du projet](#-aperçu-du-projet)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture du projet](#-architecture-du-projet)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Lancement](#-lancement)
- [Structure des modules](#-structure-des-modules)
- [Base de données](#-base-de-données)
- [Équipe](#-équipe)
- [Encadrement](#-encadrement)
- [Licence](#-licence)

---

##  Aperçu du projet

KMER FOOD est né du besoin de digitaliser la gestion des restaurants au Cameroun. L'application offre une interface intuitive pour les gérants, les serveurs et les caissiers, avec une gestion centralisée de toutes les opérations quotidiennes.

**Contexte académique :**
- Établissement : École Nationale Supérieure Polytechnique (ENSP) de Yaoundé
- Filière : Génie des Télécommunications (3GTEL)
- Année académique : 2025–2026

---

##  Fonctionnalités

| # | Module | Description | Statut |
|---|--------|-------------|--------|
| 1 | **Authentification & Rôles** | Connexion sécurisée, gestion des utilisateurs et permissions par rôle (gérant, serveur, caissier, cuisinier) | Prévu |
| 2 | **Recettes** | Création et gestion des recettes avec ingrédients, quantités et coût de revient |  Prévu |
| 3 | **Produits** | Catalogue des produits et plats proposés, avec catégories, prix et disponibilité |  Prévu |
| 4 | **Commandes & Facturation** | Prise de commande, suivi en temps réel, génération de factures et reçus |  Prévu |
| 5 | **Inventaire & Alertes Stock** | Suivi des stocks d'ingrédients, alertes de seuil critique et historique des mouvements | Prévu |
| 6 | **Ressources Humaines & Paie** | Gestion du personnel, présences, congés et calcul de la paie | Prévu |
| 7 | **Dashboard & Rapports** | Tableaux de bord interactifs, statistiques de ventes et exports PDF/Excel |  Prévu |

---

## Architecture du projet

```
KMER_FOOD/
│
├── KMER_FOOD_RESTO/
│   ├── KMER_FOOD_RESTO/              # Configuration principale Django
│   │   ├── settings.py               # Paramètres globaux
│   │   ├── urls.py                   # Routage principal
│   │   ├── wsgi.py                   # Interface WSGI
│   │   └── asgi.py                   # Interface ASGI
│   │
│   ├── authentification/             # Module 1 — Auth & Rôles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templates/authentification/
│   │
│   ├── recettes/                     # Module 2 — Recettes
│   ├── produits/                     # Module 3 — Produits
│   ├── commandes/                    # Module 4 — Commandes & Facturation
│   ├── inventaire/                   # Module 5 — Inventaire & Alertes Stock
│   ├── rh/                           # Module 6 — Ressources Humaines & Paie
│   ├── dashboard/                    # Module 7 — Dashboard & Rapports
│   ├── Base_Restaurant.sql           # Base de données du restaurant
│   ├── static/                       # Fichiers statiques (CSS, JS, images), prevu
│   ├── templates/                    # Templates HTML globaux 
│   └── manage.py
│
├── env/                              # Environnement virtuel (non versionné)
├── .env.example                      # Exemple de configuration
├── requirements.txt                  # Dépendances Python
└── README.md
```

---

##  Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python** 3.11 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **MySQL Server** 8.0 ou supérieur
- **Git**

Vérifier les versions en utilisant les commandes :

```bash
python3 --version
mysql --version
git --version
```

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/KMER_FOOD.git
cd KMER_FOOD/KMER_FOOD_RESTO
```

### 2. Créer et activer un environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv env

# Activer (Linux / macOS)
source env/bin/activate

# Activer (Windows)
env\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer les dépendances individuellement (si nécessaire)

```bash
pip install django
pip install mysqlclient
pip install python-decouple
pip install Pillow
```

---

##  Configuration

### 1. Créer le fichier `.env`

Copiez le fichier d'exemple et remplissez vos valeurs :

```bash
cp .env.example .env
```

### 2. Contenu du fichier `.env`

```env
# Django
SECRET_KEY=votre_clé_secrète_django_ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données MySQL
DB_NAME=kmer_food_db
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306
```

### 3. Créer la base de données MySQL

```sql
-- Se connecter à MySQL
mysql -u root -p

-- Créer la base de données
CREATE DATABASE kmer_food_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Vérifier
SHOW DATABASES;
EXIT;
```

---

##  Lancement

### 1. Appliquer les migrations

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 2. Créer un superutilisateur

```bash
python3 manage.py createsuperuser
```

### 3. Lancer le serveur de développement

```bash
python3 manage.py runserver
```

L'application est accessible à l'adresse : **http://127.0.0.1:8000/**  
L'interface d'administration : **http://127.0.0.1:8000/admin/**

---

##  Structure des modules

###  Module 1 — Authentification & Rôles

Point d'entrée sécurisé de toute l'application.

- Connexion / déconnexion avec session sécurisée
- Gestion des utilisateurs (création, modification, désactivation)
- Définition des rôles : Gérant, Serveur, Caissier, Cuisinier
- Contrôle d'accès par rôle (permissions granulaires sur chaque module)
- Journal des connexions et activités utilisateurs

###  Module 2 — Recettes

Référentiel des recettes utilisées pour la préparation des plats.

- Création de recettes avec liste d'ingrédients et quantités
- Calcul automatique du coût de revient par recette
- Association recette ↔ produit du menu
- Versioning des recettes (historique des modifications)

###  Module 3 — Produits

Catalogue complet des plats et boissons proposés.

- Gestion des produits avec photos, prix de vente et catégories
- Activation/désactivation de la disponibilité en temps réel
- Association produit ↔ recette pour le calcul de marge
- Gestion des menus et formules spéciales

###  Module 4 — Commandes & Facturation

Cœur opérationnel du restaurant.

- Prise de commande par table, comptoir ou à emporter
- Suivi du statut : En attente → En préparation → Servie → Clôturée
- Génération automatique de factures et reçus
- Support des paiements : espèces, Mobile Money (MTN/Orange)
- Historique complet et recherche avancée

###  Module 5 — Inventaire & Alertes Stock

Maîtrise des consommables et approvisionnements.

- Inventaire en temps réel des ingrédients et matières premières
- Décrément automatique du stock à chaque commande validée
- Alertes automatiques quand un seuil critique est atteint
- Historique des entrées, sorties et ajustements de stock
- Gestion des fournisseurs et bons de commande

###  Module 6 — Ressources Humaines & Paie

Administration du personnel du restaurant.

- Fiche employé (informations personnelles, poste, contrat)
- Suivi des présences, absences et congés
- Calcul automatique de la paie mensuelle (salaire de base + heures sup)
- Génération des fiches de paie en PDF (optionnel)
- Historique des mouvements RH

###  Module 7 — Dashboard & Rapports

Vision globale et aide à la décision.

- Tableau de bord interactif avec indicateurs clés
- Chiffre d'affaires : journalier, hebdomadaire, mensuel
- Classement des produits les plus vendus
- Analyse des coûts et marges bénéficiaires
- Export des rapports en PDF et Excel *(fonctionnalité optionnelle)*

---

##  Base de données

**SGBD :** MySQL 8.0  
**Encodage :** UTF-8 MB4 (support des caractères spéciaux et emojis)

### Schéma simplifié

```
Utilisateur(Rôle) ──< Commande >── Produit ──< Recette >── Ingrédient
                          |                                      |
                      Facturation                           Inventaire
                          |                                (AlerteStock)
                     PaiementMobile

Employé ──< Présence
    |
  Paie
```

### Commandes utiles

```bash
# Voir les migrations disponibles
python3 manage.py showmigrations

# Réinitialiser une migration spécifique
python3 manage.py migrate nom_app zero

# Sauvegarder la base de données
mysqldump -u root -p kmer_food_db > backup_$(date +%Y%m%d).sql
```



##  Équipe

| Nom | Matricule | Rôle |
|-----|-----------|------|
| VMESSAH IDA | 23P343 | Développeuse principale |
| ENGAMBA ARMAND | 25P882 | Développeur |
| JOHN KOLLE EPIE | 23P473 | Développeur |
| NGOMANDJOLIE LARISSA | 22P500 | Développeuse |
| CHINTOUO ARAFAT | — | Développeur |

---

##  Encadrement

**Superviseur :** Mr. Mbietieu Amos Mb.  
**Institution :** École Nationale Supérieure Polytechnique (ENSP) de Yaoundé  
**Département :** Génie des Télécommunications — Promotion 2028

---

##  Licence

Ce projet est développé dans un cadre académique à l'ENSP Yaoundé.  
Tous droits réservés © 2026 — Équipe KMER FOOD.

---
<p align="center">
  Fait à Yaoundé, Cameroun 
</p>
