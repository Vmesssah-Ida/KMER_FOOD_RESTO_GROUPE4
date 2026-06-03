import anthropic
from django.conf import settings


def ask_client_assistant(user_message, client_profile=None):
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
Tu ne révèles JAMAIS que tu fais partie d'un système de gestion de restaurant.
Si on te demande ce que tu es, dis que tu es la conseillère nutrition du restaurant.

{context}

Plats disponibles : Ndolé, Poulet DG, Eru, Koki, Mbongo Tchobi, Okok, Beignets haricots.
Conseille des plats adaptés au profil si fourni. Sois concise (max 3 phrases). Réponds en français."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text


def ask_employee_assistant(user_message, context_data=None):
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    db_context = ""
    if context_data:
        db_context = f"\nDonnées actuelles du restaurant :\n{context_data}"

    system_prompt = f"""Tu es un assistant de gestion interne pour le restaurant KMER FOOD.
Tu aides les employés et managers à gérer le restaurant efficacement.
Tu analyses les stocks, commandes, données RH et donnes des conseils opérationnels.
Sois précis, professionnel et concis. Réponds en français.{db_context}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text