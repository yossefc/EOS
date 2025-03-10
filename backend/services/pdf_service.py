"""
Service de génération de documents PDF pour les factures et relevés de paiement
Utilise la bibliothèque ReportLab pour générer des PDF
"""

import logging
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak

logger = logging.getLogger(__name__)

def generate_paiement_pdf(enqueteur, facturations, montant_total, reference_paiement, date_paiement, non_payees=False):
    """
    Génère un PDF de relevé de paiement pour un enquêteur
    
    Args:
        enqueteur: Instance de Enqueteur
        facturations: Liste des facturations (avec détails)
        montant_total: Montant total des facturations
        reference_paiement: Référence du paiement
        date_paiement: Date du paiement
        non_payees: Indique s'il s'agit d'un relevé pour des facturations non encore payées
        
    Returns:
        str: Chemin vers le fichier PDF généré
    """
    try:
        # Créer un fichier temporaire pour le PDF
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)  # Fermer le descripteur de fichier
        
        # Créer le document
        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            alignment=1,
            fontSize=16,
            spaceAfter=16,
        )
        # Éléments du document
        elements = []
        
        # Titre
        if non_payees:
            elements.append(Paragraph("RELEVÉ DES FACTURATIONS À PAYER", title_style))
        else:
            elements.append(Paragraph("RELEVÉ DE PAIEMENT", title_style))
        
        # Informations du document
        elements.append(Paragraph(f"<b>Date:</b> {date_paiement.strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Référence:</b> {reference_paiement}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Informations de l'enquêteur
        elements.append(Paragraph("<b>Enquêteur:</b>", styles['Normal']))
        elements.append(Paragraph(f"{enqueteur.nom} {enqueteur.prenom}", styles['Normal']))
        elements.append(Paragraph(f"Email: {enqueteur.email}", styles['Normal']))
        if enqueteur.telephone:
            elements.append(Paragraph(f"Téléphone: {enqueteur.telephone}", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Résumé
        elements.append(Paragraph(f"<b>Nombre d'enquêtes:</b> {len(facturations)}", styles['Normal']))
        elements.append(Paragraph(f"<b>Montant total:</b> {montant_total:.2f} €", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Tableau des facturations
        data = [
            ["N° Dossier", "Éléments", "Résultat", "Date", "Montant"]
        ]
        
        for f in facturations:
            # Interprétation des codes résultat
            if f['code_resultat'] == 'P':
                resultat = "Positif"
            elif f['code_resultat'] == 'N':
                resultat = "Négatif"
            elif f['code_resultat'] == 'H':
                resultat = "Confirmé"
            else:
                resultat = f['code_resultat'] if f['code_resultat'] else "-"
            
            data.append([
                f['numeroDossier'],
                f['elements_retrouves'] or "-",
                resultat,
                f['date_creation'],
                f"{f['montant']:.2f} €"
            ])
        
        # Ajouter une ligne de total
        data.append(["", "", "", "TOTAL", f"{montant_total:.2f} €"])
        
        # Créer le tableau
        table = Table(data, colWidths=[doc.width/5.0]*5)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Signature
        if non_payees:
            elements.append(Paragraph("Ce document est un relevé des facturations en attente de paiement.", styles['Normal']))
        else:
            elements.append(Paragraph("Ce document atteste du paiement des enquêtes listées ci-dessus.", styles['Normal']))
        
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Signature:", styles['Normal']))
        
        # Construire le document
        doc.build(elements)
        
        return path
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du PDF: {str(e)}")
        raise

def generate_facture_pdf(client, facturations, montant_total, reference_facture, date_facture):
    """
    Génère une facture PDF pour un client
    
    Args:
        client: Informations du client
        facturations: Liste des facturations (avec détails)
        montant_total: Montant total de la facture
        reference_facture: Référence de la facture
        date_facture: Date de la facture
        
    Returns:
        str: Chemin vers le fichier PDF généré
    """
    try:
        # Créer un fichier temporaire pour le PDF
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)  # Fermer le descripteur de fichier
        
        # Créer le document
        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            alignment=2,  # 2 = right alignment
        ))
        styles.add(ParagraphStyle(
            name='Center',
            parent=styles['Normal'],
            alignment=1,  # 1 = center alignment
        ))
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            alignment=1,
            fontSize=16,
            spaceAfter=16,
        ))
        
        # Éléments du document
        elements = []
        
        # En-tête avec logo et informations de l'entreprise
        # Remplacer par le logo et les informations réelles de l'entreprise
        header_data = [
            ["EOS FRANCE", ""],
            ["123 Avenue de Paris", "FACTURE"],
            ["75000 Paris", f"N° {reference_facture}"],
            ["SIRET: 123 456 789 00012", f"Date: {date_facture.strftime('%d/%m/%Y')}"]
        ]
        
        header = Table(header_data, colWidths=[doc.width/2.0, doc.width/2.0])
        header.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('FONTSIZE', (1, 1), (1, 1), 14),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(header)
        elements.append(Spacer(1, 20))
        
        # Informations du client
        elements.append(Paragraph("<b>Client:</b>", styles['Normal']))
        elements.append(Paragraph(f"{client['nom']}", styles['Normal']))
        elements.append(Paragraph(f"{client['adresse']}", styles['Normal']))
        elements.append(Paragraph(f"{client['code_postal']} {client['ville']}", styles['Normal']))
        if client.get('email'):
            elements.append(Paragraph(f"Email: {client['email']}", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Tableau des facturations
        data = [
            ["Description", "Quantité", "Prix unitaire HT", "Total HT"]
        ]
        
        # Regrouper les facturations par type d'élément
        facturations_par_type = {}
        for f in facturations:
            elements_retrouves = f['elements_retrouves'] or "Autre"
            if elements_retrouves not in facturations_par_type:
                facturations_par_type[elements_retrouves] = {
                    'count': 0,
                    'montant': 0
                }
            facturations_par_type[elements_retrouves]['count'] += 1
            facturations_par_type[elements_retrouves]['montant'] += f['montant']
        
        # Ajouter une ligne par type d'élément
        for elements, info in facturations_par_type.items():
            # Description basée sur le type d'élément
            if elements == "A":
                desc = "Recherche d'adresse"
            elif elements == "AT":
                desc = "Recherche d'adresse et téléphone"
            elif elements == "D":
                desc = "Vérification de décès"
            elif elements == "AB":
                desc = "Recherche d'adresse et banque"
            elif elements == "ATB":
                desc = "Recherche complète (adresse, téléphone, banque)"
            else:
                desc = f"Recherche de type {elements}"
            
            data.append([
                desc,
                info['count'],
                f"{info['montant'] / info['count']:.2f} €",
                f"{info['montant']:.2f} €"
            ])
        
        # Ajouter les lignes de total
        data.append(["", "", "Total HT", f"{montant_total:.2f} €"])
        data.append(["", "", "TVA (20%)", f"{montant_total * 0.2:.2f} €"])
        data.append(["", "", "Total TTC", f"{montant_total * 1.2:.2f} €"])
        
        # Créer le tableau
        table = Table(data, colWidths=[doc.width*0.4, doc.width*0.15, doc.width*0.2, doc.width*0.25])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('ALIGN', (1, 1), (1, -4), 'CENTER'),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Conditions de paiement
        elements.append(Paragraph("<b>Conditions de paiement:</b>", styles['Normal']))
        elements.append(Paragraph("Paiement à 30 jours à compter de la date de facturation.", styles['Normal']))
        elements.append(Paragraph("Règlement par virement bancaire sur le compte suivant:", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Coordonnées bancaires
        bank_data = [
            ["Titulaire", "EOS FRANCE"],
            ["Banque", "Banque Exemple"],
            ["IBAN", "FR76 XXXX XXXX XXXX XXXX XXXX XXX"],
            ["BIC", "EXAMPLEXXXXX"]
        ]
        
        bank_table = Table(bank_data, colWidths=[doc.width*0.2, doc.width*0.8])
        bank_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(bank_table)
        elements.append(Spacer(1, 15))
        
        # Mentions légales
        elements.append(Paragraph("En cas de retard de paiement, des pénalités de retard au taux annuel de 12% seront appliquées.", styles['Normal']))
        elements.append(Paragraph("Une indemnité forfaitaire de 40€ pour frais de recouvrement sera due.", styles['Normal']))
        
        # Construire le document
        doc.build(elements)
        
        return path
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la facture PDF: {str(e)}")
        raise