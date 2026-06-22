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

    except ValueError as e:
        # Clé API manquante
        return JsonResponse({
            'response': "Je suis KEMI 🌿 Je ne suis pas encore activée — la clé API n'est pas configurée. Mais n'hésitez pas à consulter notre menu pour choisir vos plats !"
        })
    except Exception as e:
        return JsonResponse({
            'response': f"Erreur : {str(e)}" 
        })


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

    except ValueError as e:
        return JsonResponse({'response': "Assistant IA non activé — clé API manquante."})
    except Exception as e:
        return JsonResponse({'response': f"Erreur : {str(e)}"})


def _get_restaurant_context():
    try:
        from produits.models import Produit
        from commandes.models import Commande
        from inventaire.models import Article
        from django.db.models import Sum
        
        produits = Produit.objects.all()[:15]
        produits_info = "\n".join([f"- {p.nom}: prix={p.prix} FCFA, disponible={'Oui' if p.disponible else 'Non'}" for p in produits])
        
        nb_commandes = Commande.objects.count()
        commandes_actives = Commande.objects.filter(statut__in=['en_attente', 'en_preparation', 'prete']).count()
        
        ca_mensuel = Commande.objects.filter(statut='servie').aggregate(total=Sum('montant_total'))['total'] or 0.0
        
        alertes = Article.objects.filter(alerte=True)
        alertes_info = "\n".join([f"- {a.nom}: stock={a.quantite_disponible} {a.unite}" for a in alertes]) or "Aucune alerte"
        
        return f"""
PRODUITS:
{produits_info}

COMMANDES:
- Nombre total: {nb_commandes}
- En cours: {commandes_actives}
- Chiffre d'affaires total (commandes servies): {ca_mensuel} FCFA

ALERTES STOCK:
{alertes_info}
"""
    except Exception:
        return "Données non disponibles"
