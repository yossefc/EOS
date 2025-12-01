from flask import Blueprint, request, jsonify
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.enquetes_terminees import EnqueteTerminee
from extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

enquetes_bp = Blueprint('enquetes', __name__)

@enquetes_bp.route('/api/enquetes/pending', methods=['GET'])
def get_pending_enquetes():
    """Récupère les enquêtes en attente de validation"""
    try:
        # Récupérer les enquêtes avec un résultat, un enquêteur assigné, mais pas encore validées
        pending_enquetes = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.enqueteurId.isnot(None),  # Enquêteur assigné
            DonneeEnqueteur.code_resultat.isnot(None),  # Résultat renseigné
            ~Donnee.id.in_(db.session.query(EnqueteTerminee.donnee_id))  # Pas encore validée
        ).all()
        
        # Formater les données
        result = []
        for donnee, donnee_enqueteur in pending_enquetes:
            result.append({
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'created_at': donnee.created_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.created_at else None,
                'typeDemande': donnee.typeDemande,
                'code_resultat': donnee_enqueteur.code_resultat,
                'elements_retrouves': donnee_enqueteur.elements_retrouves
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes en attente: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/completed', methods=['GET'])
def get_completed_enquetes():
    """Récupère les enquêtes validées"""
    try:
        # Récupérer les enquêtes terminées
        completed_enquetes = db.session.query(
            EnqueteTerminee, Donnee
        ).join(
            Donnee, EnqueteTerminee.donnee_id == Donnee.id
        ).order_by(
            EnqueteTerminee.confirmed_at.desc()
        ).limit(100).all()
        
        # Formater les données
        result = []
        for enquete_terminee, donnee in completed_enquetes:
            result.append({
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'typeDemande': donnee.typeDemande,
                'confirmedAt': enquete_terminee.confirmed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'confirmedBy': enquete_terminee.confirmed_by
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes validées: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/enqueteur/<int:enqueteur_id>', methods=['GET'])
def get_enquetes_by_enqueteur(enqueteur_id):
    """Récupère les enquêtes assignées à un enquêteur (exclut les archivées)"""
    try:
        # Récupérer les enquêtes assignées à l'enquêteur spécifié (exclure les archivées)
        enquetes = Donnee.query.filter_by(enqueteurId=enqueteur_id).filter(
            Donnee.statut_validation != 'archive'
        ).all()
        
        # Formater les données
        result = []
        for donnee in enquetes:
            # Récupérer les données enquêteur associées
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
            
            # Créer un dictionnaire avec les données de l'enquête
            enquete_data = {
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'created_at': donnee.created_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.created_at else None,
                'typeDemande': donnee.typeDemande,
                'code_resultat': donnee_enqueteur.code_resultat if donnee_enqueteur else None,
                'elements_retrouves': donnee_enqueteur.elements_retrouves if donnee_enqueteur else None
            }
            
            result.append(enquete_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes pour l'enquêteur {enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/enqueteur/<int:enqueteur_id>/completed', methods=['GET'])
def get_completed_enquetes_by_enqueteur(enqueteur_id):
    """Récupère les enquêtes complétées par un enquêteur (exclut les archivées)"""
    try:
        # Récupérer les enquêtes assignées à l'enquêteur spécifié avec un code_resultat renseigné (exclure les archivées)
        enquetes = (db.session.query(Donnee, DonneeEnqueteur)
                   .join(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id)
                   .filter(Donnee.enqueteurId == enqueteur_id)
                   .filter(DonneeEnqueteur.code_resultat.isnot(None))
                   .filter(Donnee.statut_validation != 'archive')
                   .all())
        
        # Formater les données
        result = []
        for donnee, donnee_enqueteur in enquetes:
            enquete_data = {
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'updated_at': donnee_enqueteur.updated_at.strftime('%Y-%m-%d %H:%M:%S') if donnee_enqueteur.updated_at else None,
                'typeDemande': donnee.typeDemande,
                'code_resultat': donnee_enqueteur.code_resultat,
                'elements_retrouves': donnee_enqueteur.elements_retrouves
            }
            
            result.append(enquete_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes complétées pour l'enquêteur {enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@enquetes_bp.route('/api/enquetes/confirm', methods=['POST'])
def confirm_enquete():
    """Confirme une enquête (la marque comme validée)"""
    try:
        data = request.json
        enquete_id = data.get('enqueteId')
        director = data.get('director', 'Directeur')
        
        if not enquete_id:
            return jsonify({
                'success': False,
                'error': 'ID de l\'enquête manquant'
            }), 400
        
        # Vérifier si l'enquête existe
        donnee = db.session.get(Donnee, enquete_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Vérifier si l'enquête a déjà été validée
        existing = EnqueteTerminee.query.filter_by(donnee_id=enquete_id).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Cette enquête a déjà été validée'
            }), 400
        
        # Créer l'entrée pour marquer l'enquête comme validée
        enquete_terminee = EnqueteTerminee(
            donnee_id=enquete_id,
            confirmed_at=datetime.now(),
            confirmed_by=director
        )
        
        db.session.add(enquete_terminee)
        db.session.commit()
        
        # Retourner les données de l'enquête confirmée
        result = {
            'id': donnee.id,
            'numeroDossier': donnee.numeroDossier,
            'nom': donnee.nom,
            'prenom': donnee.prenom,
            'typeDemande': donnee.typeDemande,
            'confirmedAt': enquete_terminee.confirmed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'confirmedBy': enquete_terminee.confirmed_by
        }
        
        return jsonify({
            'success': True,
            'message': 'Enquête confirmée avec succès',
            'data': result
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la confirmation de l'enquête: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/<int:enquete_id>', methods=['DELETE'])
def delete_enquete(enquete_id):
    """Supprime une enquête (pour les cas exceptionnels)"""
    try:
        # Vérifier si l'enquête existe
        donnee = db.session.get(Donnee, enquete_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Supprimer l'enquête
        db.session.delete(donnee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enquête supprimée avec succès'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression de l'enquête: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_enquetes_routes(app):
    """Enregistre les routes pour les enquêtes"""
    app.register_blueprint(enquetes_bp)