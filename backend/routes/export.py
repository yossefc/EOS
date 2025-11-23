# backend/routes/export.py

from flask import Blueprint, request, jsonify, send_file
import os
import datetime
import logging
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.enqueteur import Enqueteur
from extensions import db

# Configuration du logging
logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export-enquetes', methods=['POST'])
def export_enquetes():
    """
    Génère un fichier Word (.docx) avec les résultats d'enquête
    Format: Un document Word avec une page par enquête
    """
    try:
        data = request.json
        enquetes_ids = [e.get('id') for e in data.get('enquetes', [])]
        
        if not enquetes_ids:
            return jsonify({"error": "Aucune enquête à exporter"}), 400
            
        # Récupérer les données complètes des enquêtes
        donnees = Donnee.query.filter(Donnee.id.in_(enquetes_ids)).all()
        
        if not donnees:
            return jsonify({"error": "Aucune donnée trouvée pour les enquêtes spécifiées"}), 404
            
        # Générer le document Word
        doc = generate_word_document(donnees)
        
        # Sauvegarder le document dans un BytesIO
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        # Nom du fichier
        filename = f"Export_Enquetes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        logger.info(f"{len(donnees)} enquêtes exportées avec succès en Word")
        
        # Envoyer le fichier au client
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des enquêtes: {str(e)}")
        return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500


def generate_word_document(donnees):
    """
    Génère un document Word avec toutes les enquêtes
    Une page par enquête avec mise en forme professionnelle
    """
    doc = Document()
    
    # Style du document
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    for idx, donnee in enumerate(donnees):
        # Récupérer les données enquêteur associées
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
        
        # Récupérer l'enquêteur
        enqueteur = None
        if donnee.enqueteurId:
            enqueteur = Enqueteur.query.get(donnee.enqueteurId)
        
        # Ajouter le contenu de l'enquête
        add_enquete_to_document(doc, donnee, donnee_enqueteur, enqueteur)
        
        # Ajouter un saut de page sauf pour la dernière enquête
        if idx < len(donnees) - 1:
            doc.add_page_break()
    
    return doc


def add_enquete_to_document(doc, donnee, donnee_enqueteur, enqueteur):
    """
    Ajoute une enquête au document Word avec mise en forme
    """
    # ========== TITRE PRINCIPAL ==========
    title = doc.add_heading(f"Enquête n°{donnee.id} – {donnee.nom or 'Sans nom'} {donnee.prenom or ''}", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0, 51, 102)  # Bleu foncé
    
    # Espacement après le titre
    title.paragraph_format.space_after = Pt(12)
    
    # ========== SOUS-TITRE ==========
    date_str = donnee.created_at.strftime('%d/%m/%Y') if hasattr(donnee, 'created_at') and donnee.created_at else 'N/A'
    enqueteur_nom = f"{enqueteur.prenom} {enqueteur.nom}" if enqueteur else "Non assigné"
    statut = get_statut_label(donnee_enqueteur.code_resultat if donnee_enqueteur else None)
    
    subtitle = doc.add_paragraph()
    subtitle_text = f"Date : {date_str} | Enquêteur : {enqueteur_nom} | Statut : {statut}"
    subtitle_run = subtitle.add_run(subtitle_text)
    subtitle_run.font.size = Pt(12)
    subtitle_run.font.color.rgb = RGBColor(64, 64, 64)  # Gris foncé
    subtitle.alignment = WD_ALIGN_PARAGRAPH.LEFT
    subtitle.paragraph_format.space_after = Pt(18)
    
    # ========== TABLEAU DES DONNÉES ==========
    # Créer le tableau (2 colonnes)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    
    # En-tête du tableau
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Champ'
    header_cells[1].text = 'Valeur'
    
    # Style de l'en-tête
    for cell in header_cells:
        cell_paragraph = cell.paragraphs[0]
        cell_run = cell_paragraph.runs[0]
        cell_run.font.bold = True
        cell_run.font.size = Pt(11)
        cell_run.font.color.rgb = RGBColor(255, 255, 255)  # Blanc
        # Fond bleu clair pour l'en-tête
        shading_elm = cell._element.get_or_add_tcPr()
        shading = parse_xml(r'<w:shd {} w:fill="4472C4"/>'.format(nsdecls('w')))
        shading_elm.append(shading)
    
    # Ajouter les données
    fields_data = get_enquete_fields_data(donnee, donnee_enqueteur)
    
    for field_name, field_value in fields_data:
        row_cells = table.add_row().cells
        row_cells[0].text = field_name
        row_cells[1].text = str(field_value) if field_value else ''
        
        # Style des cellules
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
    
    # Espacement après le tableau
    doc.add_paragraph()
    
    # ========== NOTES / COMMENTAIRES ==========
    notes_heading = doc.add_heading('Notes / Commentaires', level=2)
    notes_heading.paragraph_format.space_before = Pt(12)
    notes_heading_run = notes_heading.runs[0]
    notes_heading_run.font.size = Pt(14)
    notes_heading_run.font.color.rgb = RGBColor(0, 51, 102)
    
    notes_content = ""
    if donnee_enqueteur:
        notes_parts = []
        if hasattr(donnee_enqueteur, 'notes_personnelles') and donnee_enqueteur.notes_personnelles:
            notes_parts.append(donnee_enqueteur.notes_personnelles)
        if hasattr(donnee_enqueteur, 'commentaires_revenus') and donnee_enqueteur.commentaires_revenus:
            notes_parts.append(f"Revenus: {donnee_enqueteur.commentaires_revenus}")
        
        notes_content = "\n".join(notes_parts) if notes_parts else "Aucune note"
    else:
        notes_content = "Aucune note"
    
    notes_para = doc.add_paragraph(notes_content)
    notes_para.paragraph_format.space_after = Pt(12)


def get_statut_label(code):
    """Retourne le label du statut en fonction du code"""
    statuts = {
        'P': 'Positif',
        'N': 'Négatif',
        'H': 'Confirmé',
        'Z': 'Annulé (agence)',
        'I': 'Intraitable',
        'Y': 'Annulé (EOS)'
    }
    return statuts.get(code, 'En attente')


def get_enquete_fields_data(donnee, donnee_enqueteur):
    """
    Retourne la liste des champs et valeurs pour une enquête
    Format: [(nom_champ, valeur), ...]
    """
    fields = []
    
    # Informations de base
    fields.append(("N° Dossier", donnee.numeroDossier))
    fields.append(("Référence", donnee.referenceDossier))
    fields.append(("Type de demande", "Enquête" if donnee.typeDemande == "ENQ" else "Contestation"))
    
    # État civil
    fields.append(("Nom", donnee.nom))
    fields.append(("Prénom", donnee.prenom))
    fields.append(("Date de naissance", donnee.dateNaissance.strftime('%d/%m/%Y') if donnee.dateNaissance else ''))
    fields.append(("Lieu de naissance", donnee.lieuNaissance))
    
    # Adresse d'origine
    fields.append(("Adresse (origine)", donnee.adresse1))
    fields.append(("Code postal (origine)", donnee.codePostal))
    fields.append(("Ville (origine)", donnee.ville))
    fields.append(("Téléphone (origine)", donnee.telephonePersonnel))
    
    if donnee_enqueteur:
        # Résultat de l'enquête
        fields.append(("Code résultat", get_statut_label(donnee_enqueteur.code_resultat)))
        fields.append(("Éléments retrouvés", donnee_enqueteur.elements_retrouves))
        
        # Adresse trouvée
        if donnee_enqueteur.adresse1:
            fields.append(("--- ADRESSE TROUVÉE ---", ""))
            fields.append(("Adresse 1", donnee_enqueteur.adresse1))
            if donnee_enqueteur.adresse2:
                fields.append(("Adresse 2", donnee_enqueteur.adresse2))
            if donnee_enqueteur.adresse3:
                fields.append(("Adresse 3", donnee_enqueteur.adresse3))
            fields.append(("Code postal", donnee_enqueteur.code_postal))
            fields.append(("Ville", donnee_enqueteur.ville))
            fields.append(("Pays", donnee_enqueteur.pays_residence))
        
        # Contact
        if donnee_enqueteur.telephone_personnel:
            fields.append(("Téléphone personnel", donnee_enqueteur.telephone_personnel))
        if donnee_enqueteur.telephone_chez_employeur:
            fields.append(("Téléphone chez employeur", donnee_enqueteur.telephone_chez_employeur))
        
        # Employeur
        if donnee_enqueteur.nom_employeur:
            fields.append(("--- EMPLOYEUR ---", ""))
            fields.append(("Nom employeur", donnee_enqueteur.nom_employeur))
            fields.append(("Téléphone employeur", donnee_enqueteur.telephone_employeur))
            fields.append(("Adresse employeur", donnee_enqueteur.adresse1_employeur))
            fields.append(("Ville employeur", donnee_enqueteur.ville_employeur))
        
        # Banque
        if donnee_enqueteur.banque_domiciliation:
            fields.append(("--- BANQUE ---", ""))
            fields.append(("Banque", donnee_enqueteur.banque_domiciliation))
            fields.append(("Guichet", donnee_enqueteur.libelle_guichet))
            fields.append(("Titulaire", donnee_enqueteur.titulaire_compte))
            fields.append(("Code banque", donnee_enqueteur.code_banque))
            fields.append(("Code guichet", donnee_enqueteur.code_guichet))
        
        # Décès
        if donnee_enqueteur.date_deces:
            fields.append(("--- DÉCÈS ---", ""))
            fields.append(("Date de décès", donnee_enqueteur.date_deces.strftime('%d/%m/%Y')))
            fields.append(("N° acte de décès", donnee_enqueteur.numero_acte_deces))
            fields.append(("Lieu de décès", donnee_enqueteur.localite_deces))
    
    return fields


def register_export_routes(app):
    """
    Enregistre les routes d'export dans l'application
    """
    app.register_blueprint(export_bp)
