# backend/routes/export.py

from flask import Blueprint, request, jsonify, send_file
import os
import datetime
import logging
from io import StringIO, BytesIO
import tempfile
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur
from models.enqueteur import Enqueteur
from extensions import db

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx n'est pas installé. L'export Word ne sera pas disponible.")

# Configuration du logging
logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export-enquetes', methods=['POST'])
def export_enquetes():
    """
    Génère un fichier texte avec les résultats d'enquête au format EOS
    Format: fichier texte à longueur fixe selon le cahier des charges
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
            
        # Générer le contenu du fichier texte
        content = generate_export_content(donnees)
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        
        # Envoyer le fichier au client
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"EOSExp_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des enquêtes: {str(e)}")
        return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500

def generate_export_content(donnees):
    """
    Génère le contenu du fichier d'export au format texte à longueur fixe
    selon les spécifications du cahier des charges EOS
    """
    output = StringIO()
    
    for donnee in donnees:
        # Récupérer les données enquêteur associées
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
        
        # Si pas de données enquêteur, on utilise des valeurs par défaut
        if not donnee_enqueteur:
            donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee.id)
        
        # Récupérer l'enquêteur
        enqueteur = None
        if donnee.enqueteurId:
            enqueteur = Enqueteur.query.get(donnee.enqueteurId)
        
        # Construire la ligne selon le format du cahier des charges
        line = format_export_line(donnee, donnee_enqueteur, enqueteur)
        output.write(line + '\n')
    
    return output.getvalue()

def format_export_line(donnee, donnee_enqueteur, enqueteur=None):
    """
    Formatte une ligne de données selon le format spécifié dans le cahier des charges
    Prend en compte les corrections d'état civil lorsque le flag est activé
    """
    # Initialisation de la ligne avec des espaces
    line = " " * 1854  # Longueur totale de la ligne selon le cahier des charges
    
    # Liste des positions et longueurs de chaque champ selon le cahier des charges
    fields = [
        # Champ, début, longueur
        ("numeroDossier", 0, 10),
        ("referenceDossier", 10, 15),
        ("numeroInterlocuteur", 25, 12),
        ("guidInterlocuteur", 37, 36),
        ("typeDemande", 73, 3),
        ("numeroDemande", 76, 11),
        ("numeroDemandeContestee", 87, 11),
        ("numeroDemandeInitiale", 98, 11),
        ("forfaitDemande", 109, 16),
        ("dateRetourEspere", 125, 10),
        ("qualite", 135, 10),
        ("nom", 145, 30),
        ("prenom", 175, 20),
        ("dateNaissance", 195, 10),
        ("lieuNaissance", 205, 50),
        ("codePostalNaissance", 255, 10),
        ("paysNaissance", 265, 32),
        ("nomPatronymique", 297, 30),
        ("dateRetour", 327, 10),
        ("codeResultat", 337, 1),
        ("elementsRetrouves", 338, 10),
        ("flagEtatCivilErrone", 348, 1),
        ("numeroFacture", 349, 9),
        ("dateFacture", 358, 10),
        ("montantFacture", 368, 8),
        ("tarifApplique", 376, 8),
        ("cumulMontantsPrecedents", 384, 8),
        ("repriseFacturation", 392, 8),
        ("remiseEventuelle", 400, 8),
        ("dateDeces", 408, 10),
        ("numeroActeDeces", 418, 10),
        ("codeInseeDeces", 428, 5),
        ("codePostalDeces", 433, 10),
        ("localiteDeces", 443, 32),
        ("adresse1", 475, 32),
        ("adresse2", 507, 32),
        ("adresse3", 539, 32),
        ("adresse4", 571, 32),
        ("codePostal", 603, 10),
        ("ville", 613, 32),
        ("paysResidence", 645, 32),
        ("telephonePersonnel", 677, 15),
        ("telephoneEmployeur", 692, 15),
        ("nomEmployeur", 707, 32),
        ("telephoneEmployeur2", 739, 15),
        ("telecopieEmployeur", 754, 15),
        ("adresse1Employeur", 769, 32),
        ("adresse2Employeur", 801, 32),
        ("adresse3Employeur", 833, 32),
        ("adresse4Employeur", 865, 32),
        ("codePostalEmployeur", 897, 10),
        ("villeEmployeur", 907, 32),
        ("paysEmployeur", 939, 32),
        ("banqueDomiciliation", 971, 32),
        ("libelleGuichet", 1003, 30),
        ("titulaireCompte", 1033, 32),
        ("codeBanque", 1065, 5),
        ("codeGuichet", 1070, 5),
        ("numeroCompte", 1075, 11),
        ("ribCompte", 1086, 2),
    ]
    
    # Déterminer si on doit utiliser les données d'état civil corrigées
    use_corrected_data = donnee_enqueteur and hasattr(donnee_enqueteur, 'flag_etat_civil_errone') and donnee_enqueteur.flag_etat_civil_errone == 'E'
    
    # Déterminer les valeurs d'état civil à utiliser (originales ou corrigées)
    qualite = donnee.qualite
    nom = donnee.nom
    prenom = donnee.prenom
    nom_patronymique = donnee.nomPatronymique
    date_naissance = donnee.dateNaissance.strftime('%d/%m/%Y') if donnee.dateNaissance else ""
    lieu_naissance = donnee.lieuNaissance
    code_postal_naissance = donnee.codePostalNaissance
    pays_naissance = donnee.paysNaissance
    
    # Si on doit utiliser les données corrigées, on les récupère
    if use_corrected_data:
        if hasattr(donnee_enqueteur, 'qualite_corrigee') and donnee_enqueteur.qualite_corrigee:
            qualite = donnee_enqueteur.qualite_corrigee
        if hasattr(donnee_enqueteur, 'nom_corrige') and donnee_enqueteur.nom_corrige:
            nom = donnee_enqueteur.nom_corrige
        if hasattr(donnee_enqueteur, 'prenom_corrige') and donnee_enqueteur.prenom_corrige:
            prenom = donnee_enqueteur.prenom_corrige
        if hasattr(donnee_enqueteur, 'nom_patronymique_corrige') and donnee_enqueteur.nom_patronymique_corrige:
            nom_patronymique = donnee_enqueteur.nom_patronymique_corrige
        if hasattr(donnee_enqueteur, 'date_naissance_corrigee') and donnee_enqueteur.date_naissance_corrigee:
            date_naissance = donnee_enqueteur.date_naissance_corrigee.strftime('%d/%m/%Y')
        if hasattr(donnee_enqueteur, 'lieu_naissance_corrige') and donnee_enqueteur.lieu_naissance_corrige:
            lieu_naissance = donnee_enqueteur.lieu_naissance_corrige
        if hasattr(donnee_enqueteur, 'code_postal_naissance_corrige') and donnee_enqueteur.code_postal_naissance_corrige:
            code_postal_naissance = donnee_enqueteur.code_postal_naissance_corrige
        if hasattr(donnee_enqueteur, 'pays_naissance_corrige') and donnee_enqueteur.pays_naissance_corrige:
            pays_naissance = donnee_enqueteur.pays_naissance_corrige
    
    # Formater la date de retour avec la date actuelle
    date_retour = datetime.datetime.now().strftime('%d/%m/%Y')
    
    # Préparer toutes les valeurs à insérer
    values = {
        "numeroDossier": donnee.numeroDossier or "",
        "referenceDossier": donnee.referenceDossier or "",
        "numeroInterlocuteur": donnee.numeroInterlocuteur or "",
        "guidInterlocuteur": donnee.guidInterlocuteur or "",
        "typeDemande": donnee.typeDemande or "",
        "numeroDemande": donnee.numeroDemande or "",
        "numeroDemandeContestee": donnee.numeroDemandeContestee or "",
        "numeroDemandeInitiale": donnee.numeroDemandeInitiale or "",
        "forfaitDemande": donnee.forfaitDemande or "",
        "dateRetourEspere": donnee.dateRetourEspere.strftime('%d/%m/%Y') if donnee.dateRetourEspere else "",
        
        # État civil (original ou corrigé)
        "qualite": qualite or "",
        "nom": nom or "",
        "prenom": prenom or "",
        "dateNaissance": date_naissance or "",
        "lieuNaissance": lieu_naissance or "",
        "codePostalNaissance": code_postal_naissance or "",
        "paysNaissance": pays_naissance or "",
        "nomPatronymique": nom_patronymique or "",
        
        "dateRetour": date_retour,
        "codeResultat": donnee_enqueteur.code_resultat or "",
        "elementsRetrouves": donnee_enqueteur.elements_retrouves or "",
        "flagEtatCivilErrone": donnee_enqueteur.flag_etat_civil_errone if hasattr(donnee_enqueteur, 'flag_etat_civil_errone') else "",
        "numeroFacture": "",  # Laisser vide selon le cahier des charges
        "dateFacture": "",    # Laisser vide selon le cahier des charges
        "montantFacture": "0",
        "tarifApplique": "0",
        "cumulMontantsPrecedents": "0",
        "repriseFacturation": "0",
        "remiseEventuelle": "0",
        "dateDeces": donnee_enqueteur.date_deces.strftime('%d/%m/%Y') if hasattr(donnee_enqueteur, 'date_deces') and donnee_enqueteur.date_deces else "",
        "numeroActeDeces": donnee_enqueteur.numero_acte_deces or "",
        "codeInseeDeces": donnee_enqueteur.code_insee_deces or "",
        "codePostalDeces": donnee_enqueteur.code_postal_deces or "",
        "localiteDeces": donnee_enqueteur.localite_deces or "",
        "adresse1": donnee_enqueteur.adresse1 or "",
        "adresse2": donnee_enqueteur.adresse2 or "",
        "adresse3": donnee_enqueteur.adresse3 or "",
        "adresse4": donnee_enqueteur.adresse4 or "",
        "codePostal": donnee_enqueteur.code_postal or "",
        "ville": donnee_enqueteur.ville or "",
        "paysResidence": donnee_enqueteur.pays_residence or "",
        "telephonePersonnel": donnee_enqueteur.telephone_personnel or "",
        "telephoneEmployeur": donnee_enqueteur.telephone_chez_employeur or "",
        "nomEmployeur": donnee_enqueteur.nom_employeur or "",
        "telephoneEmployeur2": donnee_enqueteur.telephone_employeur or "",
        "telecopieEmployeur": donnee_enqueteur.telecopie_employeur or "",
        "adresse1Employeur": donnee_enqueteur.adresse1_employeur or "",
        "adresse2Employeur": donnee_enqueteur.adresse2_employeur or "",
        "adresse3Employeur": donnee_enqueteur.adresse3_employeur or "",
        "adresse4Employeur": donnee_enqueteur.adresse4_employeur or "",
        "codePostalEmployeur": donnee_enqueteur.code_postal_employeur or "",
        "villeEmployeur": donnee_enqueteur.ville_employeur or "",
        "paysEmployeur": donnee_enqueteur.pays_employeur or "",
        "banqueDomiciliation": donnee_enqueteur.banque_domiciliation or "",
        "libelleGuichet": donnee_enqueteur.libelle_guichet or "",
        "titulaireCompte": donnee_enqueteur.titulaire_compte or "",
        "codeBanque": donnee_enqueteur.code_banque or "",
        "codeGuichet": donnee_enqueteur.code_guichet or "",
        "numeroCompte": "",  # Laisser vide selon le cahier des charges
        "ribCompte": "",     # Laisser vide selon le cahier des charges
    }
    
    # Construire la ligne en insérant chaque valeur à la position correcte
    line_list = list(line)
    for field, start, length in fields:
        value = values.get(field, "")
        # Tronquer si la valeur est trop longue
        if len(value) > length:
            value = value[:length]
        # Insérer la valeur dans la ligne à la position correcte
        for i, char in enumerate(value):
            if i < length and start + i < len(line_list):
                line_list[start + i] = char
    
    # Reconvertir la liste en chaîne
    return "".join(line_list)

def generate_word_document(donnees):
    """
    Génère un document Word (.docx) contenant les enquêtes.
    Chaque enquête est sur une nouvelle page avec un design professionnel.
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx n'est pas installé")
    
    doc = Document()
    
    for i, donnee in enumerate(donnees):
        # Ajouter un saut de page entre les enquêtes (sauf pour la première)
        if i > 0:
            doc.add_page_break()
        
        # Récupérer les données enquêteur
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
        
        # Récupérer l'enquêteur
        enqueteur = None
        if donnee.enqueteurId:
            enqueteur = Enqueteur.query.get(donnee.enqueteurId)
        
        # Titre principal (Heading 1)
        titre = doc.add_heading(f"Enquête n°{donnee.id} – {donnee.nom or ''} {donnee.prenom or ''}", level=1)
        titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in titre.runs:
            run.font.size = Pt(18)
            run.font.bold = True
        
        # Sous-titre (Heading 2)
        date_str = donnee.updated_at.strftime('%d/%m/%Y') if donnee.updated_at else 'N/A'
        enqueteur_str = f"{enqueteur.nom} {enqueteur.prenom}" if enqueteur else "Non assigné"
        statut_str = donnee.statut_validation or "En attente"
        
        sous_titre = doc.add_paragraph(f"Date : {date_str} | Enquêteur : {enqueteur_str} | Statut : {statut_str}")
        sous_titre.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in sous_titre.runs:
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(64, 64, 64)
        
        doc.add_paragraph()  # Espacement
        
        # Tableau des données
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Light Grid Accent 1'
        
        # En-tête du tableau
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Champ'
        hdr_cells[1].text = 'Valeur'
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(11)
        
        # Données de base
        fields_data = [
            ('N° Dossier', donnee.numeroDossier),
            ('Référence Dossier', donnee.referenceDossier),
            ('Type de Demande', donnee.typeDemande),
            ('Qualité', donnee.qualite),
            ('Nom', donnee.nom),
            ('Prénom', donnee.prenom),
            ('Date de Naissance', donnee.dateNaissance),
            ('Lieu de Naissance', donnee.lieuNaissance),
            ('Nom Patronymique', donnee.nomPatronymique),
            ('Adresse 1', donnee.adresse1),
            ('Adresse 2', donnee.adresse2),
            ('Ville', donnee.ville),
            ('Code Postal', donnee.codePostal),
            ('Pays de Résidence', donnee.paysResidence),
            ('Téléphone Personnel', donnee.telephonePersonnel),
            ('Nom Employeur', donnee.nomEmployeur),
        ]
        
        # Ajouter les données enquêteur si disponibles
        if donnee_enqueteur:
            fields_data.extend([
                ('Code Résultat', donnee_enqueteur.code_resultat),
                ('Éléments Retrouvés', donnee_enqueteur.elements_retrouves),
                ('Date de Retour', donnee_enqueteur.date_retour.strftime('%d/%m/%Y') if donnee_enqueteur.date_retour else None),
            ])
        
        # Remplir le tableau
        for field_name, field_value in fields_data:
            if field_value:  # N'afficher que les champs non vides
                row_cells = table.add_row().cells
                row_cells[0].text = str(field_name)
                row_cells[1].text = str(field_value)
                
                # Style pour la colonne "Champ"
                for paragraph in row_cells[0].paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.size = Pt(10)
                
                # Style pour la colonne "Valeur"
                for paragraph in row_cells[1].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(10)
        
        doc.add_paragraph()  # Espacement
        
        # Section Notes / Commentaires
        doc.add_heading('Notes / Commentaires', level=2)
        notes = donnee.commentaire or "Aucune note"
        if donnee_enqueteur and donnee_enqueteur.notes_personnelles:
            notes += f"\n\nNotes de l'enquêteur:\n{donnee_enqueteur.notes_personnelles}"
        
        notes_para = doc.add_paragraph(notes)
        for run in notes_para.runs:
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(64, 64, 64)
    
    return doc

@export_bp.route('/api/enquetes/validees', methods=['GET'])
def get_enquetes_validees():
    """Récupère toutes les enquêtes validées (confirmées) prêtes pour l'export"""
    try:
        from models.enquete_archive import EnqueteArchive
        
        # Sous-requête pour les enquêtes déjà archivées
        archived_ids = db.session.query(EnqueteArchive.enquete_id).distinct()
        
        enquetes_validees = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.statut_validation == 'confirmee',
            ~Donnee.id.in_(archived_ids),
            DonneeEnqueteur.code_resultat.in_(['P', 'H', 'N', 'Z', 'I', 'Y'])
        ).order_by(
            Donnee.updated_at.desc()
        ).all()
        
        result = []
        for donnee, donnee_enqueteur in enquetes_validees:
            enqueteur = Enqueteur.query.get(donnee.enqueteurId) if donnee.enqueteurId else None
            enqueteur_nom = f"{enqueteur.nom} {enqueteur.prenom}" if enqueteur else "Non assigné"
            
            result.append({
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'referenceDossier': donnee.referenceDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'typeDemande': donnee.typeDemande,
                'enqueteurId': donnee.enqueteurId,
                'enqueteurNom': enqueteur_nom,
                'code_resultat': donnee_enqueteur.code_resultat,
                'elements_retrouves': donnee_enqueteur.elements_retrouves,
                'updated_at': donnee.updated_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.updated_at else None,
                'statut_validation': donnee.statut_validation
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes validées: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_word_document(donnees):
    """
    Génère un document Word (.docx) contenant les enquêtes.
    Chaque enquête est sur une nouvelle page avec un design professionnel.
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx n'est pas installé")
    
    doc = Document()
    
    for i, donnee in enumerate(donnees):
        # Ajouter un saut de page entre les enquêtes (sauf pour la première)
        if i > 0:
            doc.add_page_break()
        
        # Récupérer les données enquêteur
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
        
        # Récupérer l'enquêteur
        enqueteur = None
        if donnee.enqueteurId:
            enqueteur = Enqueteur.query.get(donnee.enqueteurId)
        
        # Titre principal (Heading 1)
        titre = doc.add_heading(f"Enquête n°{donnee.id} – {donnee.nom or ''} {donnee.prenom or ''}", level=1)
        titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in titre.runs:
            run.font.size = Pt(18)
            run.font.bold = True
        
        # Sous-titre (Heading 2)
        date_str = donnee.updated_at.strftime('%d/%m/%Y') if donnee.updated_at else 'N/A'
        enqueteur_str = f"{enqueteur.nom} {enqueteur.prenom}" if enqueteur else "Non assigné"
        statut_str = donnee.statut_validation or "En attente"
        
        sous_titre = doc.add_paragraph(f"Date : {date_str} | Enquêteur : {enqueteur_str} | Statut : {statut_str}")
        sous_titre.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in sous_titre.runs:
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(64, 64, 64)
        
        doc.add_paragraph()  # Espacement
        
        # Tableau des données
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Light Grid Accent 1'
        
        # En-tête du tableau
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Champ'
        hdr_cells[1].text = 'Valeur'
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(11)
        
        # Données de base
        fields_data = [
            ('N° Dossier', donnee.numeroDossier),
            ('Référence Dossier', donnee.referenceDossier),
            ('Type de Demande', donnee.typeDemande),
            ('Qualité', donnee.qualite),
            ('Nom', donnee.nom),
            ('Prénom', donnee.prenom),
            ('Date de Naissance', donnee.dateNaissance),
            ('Lieu de Naissance', donnee.lieuNaissance),
            ('Nom Patronymique', donnee.nomPatronymique),
            ('Adresse 1', donnee.adresse1),
            ('Adresse 2', donnee.adresse2),
            ('Ville', donnee.ville),
            ('Code Postal', donnee.codePostal),
            ('Pays de Résidence', donnee.paysResidence),
            ('Téléphone Personnel', donnee.telephonePersonnel),
            ('Nom Employeur', donnee.nomEmployeur),
        ]
        
        # Ajouter les données enquêteur si disponibles
        if donnee_enqueteur:
            fields_data.extend([
                ('Code Résultat', donnee_enqueteur.code_resultat),
                ('Éléments Retrouvés', donnee_enqueteur.elements_retrouves),
                ('Date de Retour', donnee_enqueteur.date_retour.strftime('%d/%m/%Y') if donnee_enqueteur.date_retour else None),
            ])
        
        # Remplir le tableau
        for field_name, field_value in fields_data:
            if field_value:  # N'afficher que les champs non vides
                row_cells = table.add_row().cells
                row_cells[0].text = str(field_name)
                row_cells[1].text = str(field_value)
                
                # Style pour la colonne "Champ"
                for paragraph in row_cells[0].paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.size = Pt(10)
                
                # Style pour la colonne "Valeur"
                for paragraph in row_cells[1].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(10)
        
        doc.add_paragraph()  # Espacement
        
        # Section Notes / Commentaires
        doc.add_heading('Notes / Commentaires', level=2)
        notes = donnee.commentaire or "Aucune note"
        if donnee_enqueteur and donnee_enqueteur.notes_personnelles:
            notes += f"\n\nNotes de l'enquêteur:\n{donnee_enqueteur.notes_personnelles}"
        
        notes_para = doc.add_paragraph(notes)
        for run in notes_para.runs:
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(64, 64, 64)
    
    return doc

@export_bp.route('/api/export/enquete/<int:enquete_id>', methods=['POST'])
def export_and_archive_enquete(enquete_id):
    """Exporte une enquête individuelle en Word et l'archive"""
    try:
        donnee = Donnee.query.get(enquete_id)
        if not donnee:
            return jsonify({"error": "Enquête non trouvée"}), 404
        
        if donnee.statut_validation != 'confirmee':
            return jsonify({"error": "Seules les enquêtes confirmées peuvent être exportées"}), 400
        
        from models.enquete_archive import EnqueteArchive
        existing_archive = EnqueteArchive.query.filter_by(enquete_id=enquete_id).first()
        if existing_archive:
            return jsonify({"error": "Cette enquête a déjà été archivée"}), 400
        
        doc = generate_word_document([donnee])
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        filename = f"Enquete_{donnee.numeroDossier}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        archive = EnqueteArchive(
            enquete_id=enquete_id,
            nom_fichier=filename,
            utilisateur=request.json.get('utilisateur', 'Administrateur') if request.json else 'Administrateur'
        )
        db.session.add(archive)
        db.session.commit()
        
        logger.info(f"Enquête {enquete_id} exportée et archivée avec succès")
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de l'export et archivage de l'enquête: {str(e)}")
        return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500

@export_bp.route('/api/archives', methods=['GET'])
def get_archives():
    """Récupère la liste des enquêtes archivées"""
    try:
        from models.enquete_archive import EnqueteArchive
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        archives_query = db.session.query(
            EnqueteArchive, Donnee
        ).join(
            Donnee, EnqueteArchive.enquete_id == Donnee.id
        ).order_by(
            EnqueteArchive.date_export.desc()
        )
        
        archives_paginated = archives_query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for archive, donnee in archives_paginated.items:
            result.append({
                'id': archive.id,
                'enquete_id': archive.enquete_id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'nom_fichier': archive.nom_fichier,
                'date_export': archive.date_export.strftime('%Y-%m-%d %H:%M:%S'),
                'utilisateur': archive.utilisateur
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'page': page,
            'per_page': per_page,
            'total': archives_paginated.total,
            'pages': archives_paginated.pages
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des archives: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@export_bp.route('/api/archives/<int:archive_id>', methods=['GET'])
def get_archive_file(archive_id):
    """Télécharge un fichier archivé"""
    try:
        from models.enquete_archive import EnqueteArchive
        
        archive = EnqueteArchive.query.get(archive_id)
        if not archive:
            return jsonify({"error": "Archive non trouvée"}), 404
        
        donnee = Donnee.query.get(archive.enquete_id)
        if not donnee:
            return jsonify({"error": "Enquête non trouvée"}), 404
        
        doc = generate_word_document([donnee])
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=archive.nom_fichier,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du fichier archivé: {str(e)}")
        return jsonify({"error": f"Erreur lors de la récupération: {str(e)}"}), 500

def register_export_routes(app):
    """
    Enregistre les routes d'export dans l'application
    """
    app.register_blueprint(export_bp)