"""
Routes d'export spécifiques au client PARTNER
Génère des fichiers Word (.docx) et Excel (.xls) selon le cahier des charges PARTNER
"""
import os
import logging
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import zipfile

from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client
from services.partner_export_service import PartnerExportService

logger = logging.getLogger(__name__)

partner_export_bp = Blueprint('partner_export', __name__)


def get_partner_client_id():
    """Récupère l'ID du client PARTNER"""
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        raise Exception("Client PARTNER non trouvé")
    return partner.id


@partner_export_bp.route('/api/partner/exports/enquetes/positives/both', methods=['POST'])
def export_enquetes_positives_both():
    """
    Génère Word ET Excel pour les enquêtes positives en une seule fois
    Archive seulement après avoir généré les 2 fichiers
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        enquetes = query.all()
        
        if not enquetes:
            return jsonify({
                'success': False,
                'error': 'Aucune enquête positive à exporter'
            }), 404
        
        # Générer les 2 fichiers
        word_output = service.generate_enquetes_positives_word(enquetes)
        excel_output = service.generate_enquetes_positives_excel(enquetes)
        
        # Créer un ZIP avec les 2 fichiers
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'cr_{timestamp}.docx', word_output.getvalue())
            zip_file.writestr(f'cr_{timestamp}.xls', excel_output.getvalue())
        
        zip_buffer.seek(0)
        
        # Archiver MAINTENANT après avoir généré les 2 fichiers
        enquete_ids = [e.id for e in enquetes]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='enquete_positive_both',
            filename=f'export_positif_{timestamp}.zip',
            filepath=f'archives/partner/export_positif_{timestamp}.zip',
            file_size=len(zip_buffer.getvalue())
        )
        
        logger.info(f"Export combiné enquêtes positives PARTNER: {len(enquetes)} enquêtes, batch #{batch.id}")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'export_positif_{timestamp}.zip'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export combiné positif PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/positives', methods=['POST'])
def export_enquetes_positives():
    """
    Génère les exports Word (.docx) et Excel (.xls) pour les enquêtes positives PARTNER
    Retourne un fichier ZIP contenant les deux fichiers
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')  # Optionnel : filtrer par batch d'import
        
        # Construire la requête pour les enquêtes positives
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        # Filtrer par batch si spécifié
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        # Joindre avec DonneeEnqueteur et filtrer les résultats positifs
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        enquetes = query.all()
        
        if not enquetes:
            return jsonify({
                'success': False,
                'error': 'Aucune enquête positive à exporter'
            }), 404
        
        # Générer les fichiers
        word_output = service.generate_enquetes_positives_word(enquetes)
        excel_output = service.generate_enquetes_positives_excel(enquetes)
        
        # Créer un fichier ZIP
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Ajouter le fichier Word
            word_filename = f'cr_{timestamp}.docx'
            zip_file.writestr(word_filename, word_output.getvalue())
            
            # Ajouter le fichier Excel
            excel_filename = f'cr_{timestamp}.xls'
            zip_file.writestr(excel_filename, excel_output.getvalue())
        
        zip_buffer.seek(0)
        
        # Enregistrer le batch d'export
        enquete_ids = [e.id for e in enquetes]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='enquete_positive',
            filename=f'export_positif_{timestamp}.zip',
            filepath=f'archives/partner/export_positif_{timestamp}.zip',
            file_size=len(zip_buffer.getvalue())
        )
        
        logger.info(f"Export enquêtes positives PARTNER créé: {len(enquetes)} enquêtes, batch #{batch.id}")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'export_positif_{timestamp}.zip'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des enquêtes positives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/positives/docx', methods=['POST'])
def export_enquetes_positives_docx():
    """
    Génère uniquement le fichier Word (.docx) pour les enquêtes positives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        enquetes = query.all()
        
        if not enquetes:
            return jsonify({
                'success': False,
                'error': 'Aucune enquête positive à exporter'
            }), 404
        
        # Générer le fichier Word
        output = service.generate_enquetes_positives_word(enquetes)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'cr_{timestamp}.docx'
        
        # Enregistrer le batch et archiver les enquêtes
        enquete_ids = [e.id for e in enquetes]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='enquete_positive_word',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        logger.info(f"Export Word enquêtes positives PARTNER: {len(enquetes)} enquêtes, batch #{batch.id}")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export Word positif PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/positives/xls', methods=['POST'])
def export_enquetes_positives_xls():
    """
    Génère uniquement le fichier Excel (.xls) pour les enquêtes positives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        enquetes = query.all()
        
        if not enquetes:
            return jsonify({
                'success': False,
                'error': 'Aucune enquête positive à exporter'
            }), 404
        
        # Générer le fichier Excel
        output = service.generate_enquetes_positives_excel(enquetes)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'cr_{timestamp}.xls'
        
        # Enregistrer le batch et archiver les enquêtes
        enquete_ids = [e.id for e in enquetes]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='enquete_positive_excel',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        logger.info(f"Export Excel enquêtes positives PARTNER: {len(enquetes)} enquêtes, batch #{batch.id}")
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export Excel positif PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/negatives', methods=['POST'])
def export_enquetes_negatives():
    """
    Génère le fichier Excel (.xls) pour les enquêtes négatives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête pour les enquêtes négatives
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        # LEFT OUTER JOIN pour gérer les dossiers sans DonneeEnqueteur
        query = query.outerjoin(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id).filter(
            db.or_(
                DonneeEnqueteur.code_resultat.in_(['N', 'I']),
                DonneeEnqueteur.id == None  # Dossiers sans enquêteur (considérés comme NEG)
            )
        )
        
        enquetes = query.all()
        
        # Générer le fichier Excel (même si vide, avec headers uniquement)
        if not enquetes:
            logger.info("Export enquêtes négatives PARTNER: 0 enquêtes (fichier vide généré)")
        
        output = service.generate_enquetes_negatives_excel(enquetes)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'cr_{timestamp}.xls'
        
        # Enregistrer le batch d'export (uniquement si des enquêtes existent)
        if enquetes:
            enquete_ids = [e.id for e in enquetes]
            batch = service.create_export_batch(
                enquete_ids=enquete_ids,
                export_type='enquete_negative',
                filename=filename,
                filepath=f'archives/partner/{filename}',
                file_size=len(output.getvalue())
            )
            logger.info(f"Export enquêtes négatives PARTNER créé: {len(enquetes)} enquêtes, batch #{batch.id}")
        else:
            logger.info("Export enquêtes négatives PARTNER créé: fichier vide (0 enquêtes)")
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des enquêtes négatives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/negatives/both', methods=['POST'])
def export_enquetes_negatives_both():
    """
    Génère Word ET Excel pour les enquêtes négatives en une seule fois
    Archive seulement après avoir généré les 2 fichiers
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        )
        
        enquetes = query.all()
        
        # Générer les fichiers (même si vide)
        if not enquetes:
            logger.info("Export enquêtes négatives PARTNER /both: 0 enquêtes (fichiers vides générés)")
        
        word_output = service.generate_enquetes_positives_word(enquetes)  # Réutilise le générateur Word
        excel_output = service.generate_enquetes_negatives_excel(enquetes)
        
        # Créer un ZIP avec les 2 fichiers
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'cr_{timestamp}.docx', word_output.getvalue())
            zip_file.writestr(f'cr_{timestamp}.xls', excel_output.getvalue())
        
        zip_buffer.seek(0)
        
        # Archiver MAINTENANT après avoir généré les 2 fichiers (seulement si des enquêtes)
        if enquetes:
            enquete_ids = [e.id for e in enquetes]
            batch = service.create_export_batch(
                enquete_ids=enquete_ids,
                export_type='enquete_negative_both',
                filename=f'export_negatif_{timestamp}.zip',
                filepath=f'archives/partner/export_negatif_{timestamp}.zip',
                file_size=len(zip_buffer.getvalue())
            )
            logger.info(f"Export combiné enquêtes négatives PARTNER: {len(enquetes)} enquêtes, batch #{batch.id}")
        else:
            logger.info("Export combiné enquêtes négatives PARTNER: fichiers vides (0 enquêtes)")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'export_negatif_{timestamp}.zip'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export combiné négatif PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/enquetes/negatives/docx', methods=['POST'])
def export_enquetes_negatives_docx():
    """
    Génère le fichier Word (.docx) pour les enquêtes négatives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        )
        
        enquetes = query.all()
        
        if not enquetes:
            return jsonify({
                'success': False,
                'error': 'Aucune enquête négative à exporter'
            }), 404
        
        # Réutiliser le générateur Word des positives (même structure)
        output = service.generate_enquetes_positives_word(enquetes)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'cr_{timestamp}.docx'
        
        # Enregistrer le batch et archiver
        enquete_ids = [e.id for e in enquetes]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='enquete_negative_word',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export Word enquêtes négatives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/contestations/positives/xls', methods=['POST'])
def export_contestations_positives_xls():
    """
    Génère le fichier Excel (.xls) pour les contestations positives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        contestations = query.all()
        
        if not contestations:
            return jsonify({
                'success': False,
                'error': 'Aucune contestation positive à exporter'
            }), 404
        
        # Réutiliser le générateur Excel des enquêtes positives
        output = service.generate_enquetes_positives_excel(contestations)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'crcont_{timestamp}.xls'
        
        # Enregistrer le batch et archiver
        enquete_ids = [c.id for c in contestations]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='contestation_positive_excel',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export Excel contestations positives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/contestations/negatives/docx', methods=['POST'])
def export_contestations_negatives_docx():
    """
    Génère le fichier Word (.docx) pour les contestations négatives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        )
        
        contestations = query.all()
        
        if not contestations:
            return jsonify({
                'success': False,
                'error': 'Aucune contestation négative à exporter'
            }), 404
        
        # Réutiliser le générateur Word des contestations positives
        output = service.generate_contestations_positives_word(contestations)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'crcont_{timestamp}.docx'
        
        # Enregistrer le batch et archiver
        enquete_ids = [c.id for c in contestations]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='contestation_negative_word',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export Word contestations négatives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/contestations/positives', methods=['POST'])
def export_contestations_positives():
    """
    Génère le fichier Word (.docx) pour les contestations positives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête pour les contestations positives
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        # Joindre avec DonneeEnqueteur et filtrer les résultats positifs
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        )
        
        contestations = query.all()
        
        if not contestations:
            return jsonify({
                'success': False,
                'error': 'Aucune contestation positive à exporter'
            }), 404
        
        # Générer le fichier Word
        output = service.generate_contestations_positives_word(contestations)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'crcont_{timestamp}.docx'
        
        # Enregistrer le batch d'export
        enquete_ids = [c.id for c in contestations]
        batch = service.create_export_batch(
            enquete_ids=enquete_ids,
            export_type='contestation_positive',
            filename=filename,
            filepath=f'archives/partner/{filename}',
            file_size=len(output.getvalue())
        )
        
        output.seek(0)
        
        logger.info(f"Export contestations positives PARTNER créé: {len(contestations)} contestations, batch #{batch.id}")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des contestations positives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/contestations/negatives', methods=['POST'])
def export_contestations_negatives():
    """
    Génère le fichier Excel (.xls) pour les contestations négatives PARTNER
    """
    try:
        partner_id = get_partner_client_id()
        service = PartnerExportService(partner_id)
        
        # Récupérer les données du formulaire
        data = request.get_json() or {}
        fichier_id = data.get('fichier_id')
        
        # Construire la requête pour les contestations négatives
        query = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        )
        
        if fichier_id:
            query = query.filter(Donnee.fichier_id == fichier_id)
        
        # Joindre avec DonneeEnqueteur et filtrer les résultats négatifs
        query = query.join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        )
        
        contestations = query.all()
        
        # Générer le fichier Excel (même si vide, avec headers uniquement)
        if not contestations:
            logger.info("Export contestations négatives PARTNER: 0 contestations (fichier vide généré)")
        
        output = service.generate_contestations_negatives_excel(contestations)
        
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        filename = f'crcont_{timestamp}.xls'
        
        # Enregistrer le batch d'export (uniquement si des contestations existent)
        if contestations:
            enquete_ids = [c.id for c in contestations]
            batch = service.create_export_batch(
                enquete_ids=enquete_ids,
                export_type='contestation_negative',
                filename=filename,
                filepath=f'archives/partner/{filename}',
                file_size=len(output.getvalue())
            )
            logger.info(f"Export contestations négatives PARTNER créé: {len(contestations)} contestations, batch #{batch.id}")
        else:
            logger.info("Export contestations négatives PARTNER créé: fichier vide (0 contestations)")
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des contestations négatives PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/validated', methods=['GET'])
def get_enquetes_partner_validees():
    """
    Retourne la liste détaillée des enquêtes PARTNER validées prêtes pour l'export
    """
    try:
        partner_id = get_partner_client_id()
        
        # Récupérer toutes les enquêtes validées PARTNER
        enquetes_query = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.client_id == partner_id,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False,
            DonneeEnqueteur.code_resultat.in_(['P', 'H', 'N', 'I'])
        ).order_by(
            Donnee.est_contestation.asc(),
            Donnee.updated_at.desc()
        ).all()
        
        result = []
        for donnee, donnee_enqueteur in enquetes_query:
            result.append({
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom_complet if donnee.est_contestation else donnee.nom,
                'prenom': donnee.prenom,
                'est_contestation': donnee.est_contestation,
                'code_resultat': donnee_enqueteur.code_resultat,
                'type_export': 'Contestation' if donnee.est_contestation else 'Enquête',
                'resultat': 'Positive' if donnee_enqueteur.code_resultat in ['P', 'H'] else 'Négative',
                'updated_at': donnee.updated_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes PARTNER validées: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@partner_export_bp.route('/api/partner/exports/stats', methods=['GET'])
def get_export_stats():
    """
    Retourne les statistiques des enquêtes/contestations prêtes à être exportées
    """
    try:
        partner_id = get_partner_client_id()
        
        # Compter les enquêtes positives
        enquetes_positives = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        ).join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        ).count()
        
        # Compter les enquêtes négatives
        enquetes_negatives = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == False,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        ).join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        ).count()
        
        # Compter les contestations positives
        contestations_positives = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        ).join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('P', 'H')")
            )
        ).count()
        
        # Compter les contestations négatives
        contestations_negatives = Donnee.query.filter(
            Donnee.client_id == partner_id,
            Donnee.est_contestation == True,
            Donnee.statut_validation == 'validee',
            Donnee.exported == False
        ).join(Donnee.donnee_enqueteur).filter(
            db.or_(
                db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
            )
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'enquetes_positives': enquetes_positives,
                'enquetes_negatives': enquetes_negatives,
                'contestations_positives': contestations_positives,
                'contestations_negatives': contestations_negatives,
                'total': enquetes_positives + enquetes_negatives + contestations_positives + contestations_negatives
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques d'export PARTNER: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

