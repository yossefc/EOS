"""
Routes de validation V2 - Validation depuis l'onglet Données
"""
from flask import Blueprint, request, jsonify
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.enquete_archive import EnqueteArchive
from extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

validation_v2_bp = Blueprint('validation_v2', __name__)

@validation_v2_bp.route('/api/enquetes/<int:enquete_id>/valider', methods=['PUT'])
def valider_enquete(enquete_id):
    """
    Valide une enquête et la marque comme archivée
    L'enquête disparaîtra du tableau Données et apparaîtra dans Export des résultats
    """
    try:
        # Vérifier que l'enquête existe
        donnee = db.session.get(Donnee, enquete_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Vérifier qu'il y a une réponse d'enquêteur
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=enquete_id).first()
        if not donnee_enqueteur or not donnee_enqueteur.code_resultat:
            return jsonify({
                'success': False,
                'error': 'Cette enquête n\'a pas de réponse d\'enquêteur'
            }), 400
        
        # Vérifier que l'enquête n'est pas déjà validée
        if donnee.statut_validation == 'archive':
            return jsonify({
                'success': False,
                'error': 'Cette enquête est déjà validée et archivée'
            }), 400
        
        # Récupérer le nom de l'utilisateur depuis la requête
        data = request.json or {}
        utilisateur = data.get('utilisateur', 'Administrateur')
        
        # Mettre à jour le statut
        donnee.statut_validation = 'archive'
        
        # Ajouter à l'historique
        donnee.add_to_history(
            'validation',
            f'Enquête validée et archivée par {utilisateur}',
            utilisateur
        )
        
        # Créer une entrée dans les archives pour l'export
        archive = EnqueteArchive(
            enquete_id=enquete_id,
            date_export=datetime.now(),
            utilisateur=utilisateur,
            nom_fichier=None  # Sera rempli lors de l'export réel
        )
        db.session.add(archive)
        
        db.session.commit()
        
        logger.info(f"Enquête {enquete_id} validée et archivée par {utilisateur}")
        
        return jsonify({
            'success': True,
            'message': 'Enquête validée avec succès',
            'data': {
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'statut_validation': donnee.statut_validation,
                'validated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'validated_by': utilisateur
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la validation de l'enquête {enquete_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la validation: {str(e)}'
        }), 500


@validation_v2_bp.route('/api/enquetes/<int:enquete_id>/refuser', methods=['PUT'])
def refuser_enquete(enquete_id):
    """
    Refuse une enquête et remet son statut à en_attente
    Les boutons de validation disparaissent mais la ligne reste visible
    """
    try:
        # Vérifier que l'enquête existe
        donnee = db.session.get(Donnee, enquete_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Récupérer le nom de l'utilisateur et le motif depuis la requête
        data = request.json or {}
        utilisateur = data.get('utilisateur', 'Administrateur')
        motif = data.get('motif', 'Aucun motif spécifié')
        
        # Remettre le statut à en_attente
        ancien_statut = donnee.statut_validation
        donnee.statut_validation = 'en_attente'
        
        # Ajouter à l'historique
        donnee.add_to_history(
            'refus_validation',
            f'Enquête refusée par {utilisateur}. Motif: {motif}. Statut remis à en_attente.',
            utilisateur
        )
        
        # Ne pas créer d'archive
        # Supprimer l'archive si elle existe (au cas où)
        EnqueteArchive.query.filter_by(enquete_id=enquete_id).delete()
        
        db.session.commit()
        
        logger.info(f"Enquête {enquete_id} refusée par {utilisateur}. Statut: {ancien_statut} -> en_attente")
        
        return jsonify({
            'success': True,
            'message': 'Enquête refusée, statut remis à en_attente',
            'data': {
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'statut_validation': donnee.statut_validation,
                'refused_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'refused_by': utilisateur
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors du refus de l'enquête {enquete_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors du refus: {str(e)}'
        }), 500


def register_validation_v2_routes(app):
    """Enregistre les routes de validation V2"""
    app.register_blueprint(validation_v2_bp)
    logger.info("Routes de validation V2 enregistrées")


