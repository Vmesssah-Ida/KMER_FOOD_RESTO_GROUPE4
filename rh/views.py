from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Personnel, Presence, Paie
import datetime

@login_required
def personnel_liste(request):
    employes = Personnel.objects.select_related('utilisateur').all()
    return render(request, 'rh/personnel_liste.html', {'employes': employes})

@login_required
def personnel_detail(request, pk):
    employe   = get_object_or_404(Personnel, pk=pk)
    presences = employe.presences.all()[:30]
    paies     = employe.paies.all()
    return render(request, 'rh/personnel_detail.html', {'employe': employe, 'presences': presences, 'paies': paies})

@login_required
def presence_enregistrer(request):
    employes = Personnel.objects.select_related('utilisateur').all()
    if request.method == 'POST':
        date = datetime.date.fromisoformat(request.POST.get('date'))
        for employe in employes:
            present       = request.POST.get(f'present_{employe.pk}') == 'on'
            heure_arrivee = request.POST.get(f'arrivee_{employe.pk}') or None
            heure_depart  = request.POST.get(f'depart_{employe.pk}')  or None
            Presence.objects.update_or_create(
                personnel=employe, date=date,
                defaults={'present': present, 'heure_arrivee': heure_arrivee, 'heure_depart': heure_depart}
            )
        messages.success(request, f"Présences du {date} enregistrées.")
        return redirect('presence_enregistrer')
    return render(request, 'rh/presence_enregistrer.html', {'employes': employes, 'today': datetime.date.today()})

@login_required
def paie_calculer(request, pk):
    employe = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        mois  = int(request.POST.get('mois'))
        annee = int(request.POST.get('annee'))
        jours = Presence.objects.filter(personnel=employe, date__month=mois, date__year=annee, present=True).count()
        paie, _ = Paie.objects.update_or_create(
            personnel=employe, mois=mois, annee=annee,
            defaults={'jours_travailles': jours}
        )
        paie.calculer()
        messages.success(request, f"Paie calculée : {paie.montant} FCFA pour {jours} jours travaillés.")
        return redirect('personnel_detail', pk=employe.pk)
    return render(request, 'rh/paie_calculer.html', {'employe': employe, 'today': datetime.date.today()})

@login_required
def paie_marquer_versee(request, pk):
    paie = get_object_or_404(Paie, pk=pk)
    paie.statut        = 'versee'
    paie.date_versement = datetime.date.today()
    paie.save()
    messages.success(request, "Paie marquée comme versée.")
    return redirect('personnel_detail', pk=paie.personnel.pk)
