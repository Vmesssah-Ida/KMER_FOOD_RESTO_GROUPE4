import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .service import ask_client_assistant, ask_employee_assistant


@csrf_exempt
@require_POST
def client_chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Message vide'}, status=400)

        client_profile = request.session.get('client_profile', {})
        response = ask_client_assistant(message, client_profile)
        return JsonResponse({'response': response})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def employee_chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Message vide'}, status=400)

        context_data = _get_restaurant_context()
        response = ask_employee_assistant(message, context_data)
        return JsonResponse({'response': response})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _get_restaurant_context():
    try:
        from produits.models import Produit
        from commandes.models import Commande

        produits = Produit.objects.all()[:15]
        produits_info = "\n".join([
            f"- {p.nom}: prix={p.prix}"
            for p in produits
        ])

        nb_commandes = Commande.objects.count()
        return f"PRODUITS:\n{produits_info}\n\nNB COMMANDES TOTAL: {nb_commandes}"
    except Exception:
        return "Données non disponibles"