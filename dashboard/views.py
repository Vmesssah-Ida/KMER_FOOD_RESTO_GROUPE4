# 📄 dashboard/views.py
# Module 7 — Tableau de Bord et Rapports

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
import datetime
import io

from commandes.models import Commande
from produits.models import Produit
from inventaire.models import Article, MouvementStock

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def directeur_or_admin_required(view_func):
    """Accès réservé aux Directeurs ou Administrateurs."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['directeur', 'administrateur'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Cet espace est réservé à la Direction.")
        return redirect('accueil')
    return _wrapped_view


@directeur_or_admin_required
def dashboard(request):
    now = timezone.now()
    mois = now.month
    annee = now.year

    # Statistiques de base
    total_commandes = Commande.objects.count()
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    total_produits = Produit.objects.count()
    alertes_stock = Article.objects.filter(alerte=True).count()
    
    # Agrégations requises
    ca_mensuel = Commande.objects.filter(
        statut='servie',
        date_creation__month=mois,
        date_creation__year=annee
    ).aggregate(total=Sum('montant_total'))['total'] or 0.0

    depenses_stock = MouvementStock.objects.filter(
        type='entree',
        date__month=mois,
        date__year=annee
    ).annotate(
        cout=F('quantite') * F('article__prix_unitaire')
    ).aggregate(total=Sum('cout'))['total'] or 0.0
    
    # Top produits (triés par quantité cumulée vendue)
    top_produits = Produit.objects.annotate(
        total_quantite=Sum('lignecommande_set__quantite')
    ).filter(total_quantite__gt=0).order_by('-total_quantite')[:5]
    
    # Articles en alerte
    articles_alerte = Article.objects.filter(alerte=True)

    return render(request, 'dashboard/dashboard.html', {
        'total_commandes': total_commandes,
        'commandes_en_attente': commandes_en_attente,
        'total_produits': total_produits,
        'alertes_stock': alertes_stock,
        'top_produits': top_produits,
        'articles_alerte': articles_alerte,
        'ca_mensuel': ca_mensuel,
        'depenses_approvisionnement': depenses_stock,
    })


@directeur_or_admin_required
def export_rapport_pdf(request):
    now = timezone.now()
    mois = now.month
    annee = now.year
    
    ca = Commande.objects.filter(
        statut='servie',
        date_creation__month=mois,
        date_creation__year=annee
    ).aggregate(total=Sum('montant_total'))['total'] or 0.0
    
    nb_cmd_jour = Commande.objects.filter(date_creation__date=now.date()).count()
    nb_cmd_semaine = Commande.objects.filter(date_creation__gte=now - datetime.timedelta(days=7)).count()
    nb_cmd_mois = Commande.objects.filter(date_creation__month=mois, date_creation__year=annee).count()
    
    depenses = MouvementStock.objects.filter(
        type='entree',
        date__month=mois,
        date__year=annee
    ).annotate(
        cout=F('quantite') * F('article__prix_unitaire')
    ).aggregate(total=Sum('cout'))['total'] or 0.0
    
    top_prods = Produit.objects.annotate(
        total_quantite=Sum('lignecommande_set__quantite')
    ).filter(total_quantite__gt=0).order_by('-total_quantite')[:5]

    # Create the PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_financier_{mois}_{annee}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2E4057'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3E2009'),
        spaceBefore=15,
        spaceAfter=8
    )
    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

    # Title
    story.append(Paragraph(f"KMER FOOD RESTO — Rapport Mensuel ({mois}/{annee})", title_style))
    story.append(Paragraph(f"Généré le {now.strftime('%d/%m/%Y à %H:%M')}", text_style))
    story.append(Spacer(1, 10))
    
    # Section 1: KPI Financiers
    story.append(Paragraph("Statistiques Financières", section_style))
    data_kpi = [
        [Paragraph("<b>Indicateur</b>", text_style), Paragraph("<b>Valeur</b>", text_style)],
        [Paragraph("Chiffre d'Affaires Mensuel (Commandes Servies)", text_style), Paragraph(f"{ca} FCFA", text_style)],
        [Paragraph("Dépenses d'Approvisionnement", text_style), Paragraph(f"{depenses} FCFA", text_style)],
        [Paragraph("Bénéfice Brut Estimé", text_style), Paragraph(f"{float(ca) - float(depenses)} FCFA", text_style)],
    ]
    t1 = Table(data_kpi, colWidths=[4.0*inch, 2.5*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F4F6')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D3D3D3')),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Section 2: Commandes
    story.append(Paragraph("Volume de Commandes", section_style))
    data_cmd = [
        [Paragraph("<b>Période</b>", text_style), Paragraph("<b>Nombre de commandes</b>", text_style)],
        [Paragraph("Aujourd'hui", text_style), Paragraph(str(nb_cmd_jour), text_style)],
        [Paragraph("7 derniers jours", text_style), Paragraph(str(nb_cmd_semaine), text_style)],
        [Paragraph("Ce mois-ci", text_style), Paragraph(str(nb_cmd_mois), text_style)],
    ]
    t2 = Table(data_cmd, colWidths=[4.0*inch, 2.5*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F4F6')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D3D3D3')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Section 3: Top produits
    story.append(Paragraph("Top 5 des Produits les plus Vendus", section_style))
    data_prod = [[Paragraph("<b>Produit</b>", text_style), Paragraph("<b>Quantité vendue</b>", text_style)]]
    for p in top_prods:
        data_prod.append([Paragraph(p.nom, text_style), Paragraph(str(p.total_quantite), text_style)])
    
    if len(data_prod) == 1:
        data_prod.append([Paragraph("Aucune vente enregistrée ce mois-ci.", text_style), Paragraph("0", text_style)])
        
    t3 = Table(data_prod, colWidths=[4.0*inch, 2.5*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F4F6')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D3D3D3')),
    ]))
    story.append(t3)
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
