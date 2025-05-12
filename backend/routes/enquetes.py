from flask import Blueprint, request, jsonify
from models.models import Donnee
from models.enquetes_terminees import EnqueteTerminee
from extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

enquetes_bp = Blueprint('enquetes', __name__)

@enquetes_bp.route('/api/enquetes/pending', methods=['GET'])
def get_pending_enquetes():
    """Récupère la liste des enquêtes en attente de validation"""
    try:
        # Récupérer toutes les enquêtes en attente de la table Donnee
        enquetes = Donnee.query.all()
        
        return jsonify({
            'success': True,
            'data': [enquete.to_dict() for enquete in enquetes]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes en attente: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/completed', methods=['GET'])
def get_completed_enquetes():
    """Récupère la liste des enquêtes terminées et validées"""
    try:
        # Récupérer toutes les enquêtes terminées
        enquetes = EnqueteTerminee.query.order_by(EnqueteTerminee.confirmedAt.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [enquete.to_dict() for enquete in enquetes]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes terminées: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enquetes_bp.route('/api/enquetes/confirm', methods=['POST'])
def confirm_enquete():
    """Confirme une enquête et la transfère de la table Donnee vers EnqueteTerminee"""
    try:
        data = request.json
        enquete_id = data.get('enqueteId')
        director = data.get('director', 'Directeur')  # Directeur par défaut
        
        if not enquete_id:
            return jsonify({
                'success': False,
                'error': 'ID d\'enquête manquant'
            }), 400
        
        # Récupérer l'enquête à confirmer
        enquete = Donnee.query.get(enquete_id)
        
        if not enquete:
            return jsonify({
                'success': False,
                'error': f'Enquête avec ID {enquete_id} non trouvée'
            }), 404
        
        # Vérifier si l'enquête existe déjà dans la table des terminées
        existing = EnqueteTerminee.query.filter_by(numeroDossier=enquete.numeroDossier).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Cette enquête a déjà été confirmée par {existing.confirmedBy} le {existing.confirmedAt}'
            }), 409
        
        # Créer l'entrée dans la table EnqueteTerminee
        now = datetime.utcnow()
        
        enquete_terminee = EnqueteTerminee(
            # Copier tous les champs de l'enquête originale
            numeroDossier=enquete.numeroDossier,
            referenceDossier=enquete.referenceDossier,
            typeDemande=enquete.typeDemande,
            nom=enquete.nom,
            prenom=enquete.prenom,
            dateNaissance=enquete.dateNaissance,
            lieuNaissance=enquete.lieuNaissance,
            codePostal=enquete.codePostal,
            ville=enquete.ville,
            # Ajouter les informations de confirmation
            confirmedBy=director,
            confirmedAt=now,
            # Conserver l'ID original pour référence
            originalId=enquete.id
        )
        
        # Sauvegarder l'enquête terminée
        db.session.add(enquete_terminee)
        
        # Supprimer l'enquête originale
        db.session.delete(enquete)
        
        # Valider les modifications
        db.session.commit()
        
        # Retourner l'enquête confirmée
        return jsonify({
            'success': True,
            'message': 'Enquête confirmée avec succès',
            'data': enquete_terminee.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la confirmation de l'enquête: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_enquetes_routes(app):
    """Enregistre les routes des enquêtes"""
    app.register_blueprint(enquetes_bp)