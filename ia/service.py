import re
from django.conf import settings


def _reponse_locale(message):
    """Réponses intelligentes sans API — basées sur mots-clés."""
    msg = message.lower()

    # Salutations
    if any(w in msg for w in ['bonjour', 'bonsoir', 'salut', 'hello', 'bonne journée']):
        return "Bonjour ! Je suis KEMI 🌿 Votre conseillère nutrition chez KMER FOOD. Comment puis-je vous aider à bien manger aujourd'hui ?"

    # Recommandations générales
    if any(w in msg for w in ['recommande', 'conseille', 'propose', 'suggère', 'quoi manger', 'que manger']):
        return "Je vous recommande notre Ndolé 🍲 — le plat national camerounais, riche en protéines et en saveurs. Accompagné d'un Jus de Gingembre, c'est un repas complet et équilibré !"

    # Plats spécifiques
    if 'ndolé' in msg or 'ndole' in msg:
        return "Le Ndolé est notre fierté ! 🌿 Feuilles mijotées avec arachides, bœuf et crevettes séchées. Riche en fer et en protéines. Idéal pour un repas complet — 8 000 FCFA."

    if 'poulet' in msg or 'dg' in msg:
        return "Le Poulet DG est un incontournable ! 🍗 Poulet sauté aux plantains mûrs et poivrons. Excellent apport en protéines maigres — 5 000 FCFA."

    if 'eru' in msg:
        return "L'Eru et Waterleaf est un trésor du Sud-Ouest Cameroun 🌱 Riche en vitamines et minéraux, préparé avec de l'huile de palme et des protéines — 6 500 FCFA."

    if 'koki' in msg:
        return "Le Koki est une spécialité à base de haricots et huile de palme 🟡 Excellente source de protéines végétales, idéal pour les végétariens !"

    if 'beignet' in msg:
        return "Nos Beignets Sucre-Cannelle sont parfaits pour finir le repas 🍩 Moelleux et dorés — 2 000 FCFA. À déguster avec modération !"

    if any(w in msg for w in ['jus', 'boisson', 'boire', 'gingembre', 'bissap']):
        return "Nos jus maison sont préparés chaque matin 🥤 Le Jus de Gingembre est tonique et digestif, le Bissap est riche en antioxydants. Les deux à 1 500 FCFA."

    # Régimes / allergies
    if any(w in msg for w in ['végétar', 'vegetar', 'vegan', 'sans viande']):
        return "Pour un régime végétarien, je recommande le Koki (haricots) ou l'Eru sans viande 🌱 Riches en protéines végétales et en minéraux. Signalez-le au serveur lors de votre commande !"

    if any(w in msg for w in ['allergi', 'intoléran', 'sans gluten', 'arachide', 'noix']):
        return "Nous prenons les allergies très au sérieux 🙏 Signalez votre allergie au serveur. Attention : plusieurs de nos plats contiennent des arachides (Ndolé, Koki). Le Poulet DG et l'Eru en sont exempts."

    if any(w in msg for w in ['diabète', 'diabete', 'sucre', 'glycémie']):
        return "Pour un régime diabétique, privilégiez l'Eru ou le Poulet DG 🥗 Évitez les beignets et les jus sucrés. Le Jus de Gingembre sans sucre ajouté reste une bonne option !"

    if any(w in msg for w in ['poids', 'maigrir', 'régime', 'calorie', 'mince']):
        return "Pour surveiller votre ligne, optez pour le Poulet DG ou l'Eru 💪 Riches en protéines et pauvres en glucides. Accompagnez d'eau ou de Jus de Gingembre sans sucre."

    if any(w in msg for w in ['enfant', 'bébé', 'petit']):
        return "Pour les enfants, le Riz Sauté est parfait 🍚 Doux et nourrissant. Le Poulet DG est aussi apprécié des petits. Nos portions peuvent être adaptées — demandez au serveur !"

    # Prix / commande
    if any(w in msg for w in ['prix', 'coût', 'combien', 'tarif', 'cher']):
        return "Nos prix vont de 1 500 FCFA (jus) à 8 000 FCFA (Ndolé) 💰 Le Poulet DG est à 5 000 FCFA, l'Eru à 6 500 FCFA. Excellent rapport qualité-prix pour une cuisine authentique !"

    if any(w in msg for w in ['commander', 'commande', 'acheter', 'passer']):
        return "Pour commander, cliquez sur le bouton 'Commander' sur la carte du plat de votre choix 🛒 Choisissez la quantité, le type (sur place ou livraison) et confirmez. C'est simple et rapide !"

    # Horaires / infos restaurant
    if any(w in msg for w in ['heure', 'horaire', 'ouvert', 'ferme', 'quand']):
        return "KMER FOOD est ouvert tous les jours de 7h à 22h 🕐 Le service de livraison est disponible de 11h à 21h. Nous acceptons Orange Money et MTN MoMo."

    if any(w in msg for w in ['livraison', 'livrer', 'domicile']):
        return "Nous livrons à domicile dans un rayon de 10 km autour de Yaoundé 🚴 Délai moyen : 30 à 45 minutes. Choisissez 'À livrer' lors de votre commande et renseignez votre adresse."

    if any(w in msg for w in ['merci', 'super', 'parfait', 'excellent', 'génial', 'bonne']):
        return "Avec plaisir ! 😊 Bon appétit et à très bientôt chez KMER FOOD. N'hésitez pas si vous avez d'autres questions !"

    # Réponse par défaut
    return "Je suis KEMI, votre conseillère nutrition chez KMER FOOD 🌿 Je peux vous aider à choisir un plat selon vos goûts, votre régime ou vos allergies. Dites-moi ce que vous recherchez !"


def _api_disponible():
    """Vérifie si la clé API est configurée et non vide."""
    key = getattr(settings, 'ANTHROPIC_API_KEY', '') or ''
    return bool(key.strip())


def ask_client_assistant(user_message, client_profile=None):
    if not _api_disponible():
        return _reponse_locale(user_message)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        context = ""
        if client_profile:
            context = f"""
Profil du client :
- Régime alimentaire : {client_profile.get('regime', 'standard')}
- Allergies : {client_profile.get('allergies', 'aucune')}
- Préférences : {client_profile.get('preferences', 'non renseignées')}
"""
        system_prompt = f"""Tu es KEMI, l'assistante culinaire du restaurant KMER FOOD.
Tu aides les clients à choisir leurs plats et à gérer leur alimentation.
Tu es chaleureuse, tu parles de cuisine camerounaise avec passion.
Si on te demande ce que tu es, dis que tu es la conseillère nutrition du restaurant.
{context}
Plats disponibles : Ndolé, Poulet DG, Eru, Koki, Mbongo Tchobi, Okok, Beignets haricots.
Conseille des plats adaptés au profil si fourni. Sois concise (max 3 phrases). Réponds en français."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return message.content[0].text

    except Exception:
        # API indisponible → fallback local
        return _reponse_locale(user_message)


def ask_employee_assistant(user_message, context_data=None):
    if not _api_disponible():
        return "Assistant IA non disponible — rechargez des crédits sur console.anthropic.com pour activer cette fonctionnalité."

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        db_context = f"\nDonnées actuelles du restaurant :\n{context_data}" if context_data else ""
        system_prompt = f"""Tu es un assistant de gestion interne pour le restaurant KMER FOOD.
Tu aides les employés et managers à gérer le restaurant efficacement.
Sois précis, professionnel et concis. Réponds en français.{db_context}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return message.content[0].text

    except Exception:
        return "Assistant IA temporairement indisponible."
