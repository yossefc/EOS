from flask import Blueprint, request, jsonify
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.enqueteur import Enqueteur
from extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/api/enquetes/a-valider', methods=['GET'])
def get_enquetes_a_valider():
    """Récupère les enquêtes en attente de validation"""
    try:
        # Récupérer les enquêtes avec statut_validation = 'en_attente'
        # et qui ont été mises à jour par un enquêteur
        enquetes_a_valider = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.statut_validation == 'en_attente',
            Donnee.enqueteurId.isnot(None),
            DonneeEnqueteur.code_resultat.in_(['P', 'N', 'H', 'Z', 'I', 'Y']),
            DonneeEnqueteur.elements_retrouves.isnot(None),
            DonneeEnqueteur.adresse1.isnot(None)
        ).order_by(
            DonneeEnqueteur.updated_at.desc()
        ).all()
        
        # Formater les données
        result = []
        for donnee, donnee_enqueteur in enquetes_a_valider:
            # Récupérer le nom de l'enquêteur
            enqueteur = db.session.get(Enqueteur, donnee.enqueteurId) if donnee.enqueteurId else None
            enqueteur_nom = f"{enqueteur.nom} {enqueteur.prenom}" if enqueteur else "Non assigné"
            
            result.append({
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'nom': donnee.nom,
                'prenom': donnee.prenom,
                'typeDemande': donnee.typeDemande,
                'enqueteurId': donnee.enqueteurId,
                'enqueteurNom': enqueteur_nom,
                'code_resultat': donnee_enqueteur.code_resultat,
                'elements_retrouves': donnee_enqueteur.elements_retrouves,
                'updated_at': donnee_enqueteur.updated_at.strftime('%Y-%m-%d %H:%M:%S') if donnee_enqueteur.updated_at else None,
                'statut_validation': donnee.statut_validation
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes à valider: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@validation_bp.route('/api/enquete/valider/<int:enquete_id>', methods=['PUT'])
def valider_enquete(enquete_id):
    """Valide (confirme) ou refuse une enquête"""
    try:
        data = request.json
        action = data.get('action')  # 'confirmer' ou 'refuser'
        admin_nom = data.get('admin_nom', 'Administrateur')
        
        if action not in ['confirmer', 'refuser']:
            return jsonify({
                'success': False,
                'error': 'Action invalide. Utilisez "confirmer" ou "refuser"'
            }), 400
        
        # Vérifier si l'enquête existe
        donnee = db.session.get(Donnee, enquete_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Vérifier si l'enquête est en attente de validation
        if donnee.statut_validation != 'en_attente':
            return jsonify({
                'success': False,
                'error': f'Cette enquête a déjà le statut: {donnee.statut_validation}'
            }), 400
        
        # Mettre à jour le statut
        if action == 'confirmer':
            donnee.statut_validation = 'confirmee'
        else:
            donnee.statut_validation = 'refusee'
        
        # Ajouter à l'historique
        donnee.add_to_history(
            'validation',
            f'Enquête {action}e par {admin_nom}',
            admin_nom
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Enquête {action}e avec succès',
            'data': {
                'id': donnee.id,
                'numeroDossier': donnee.numeroDossier,
                'statut_validation': donnee.statut_validation,
                'validated_by': admin_nom,
                'validated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la validation de l'enquête: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@validation_bp.route('/api/donnees/<int:donnee_id>/statut', methods=['PUT'])
def update_statut_validation(donnee_id):
    """Met à jour le statut de validation d'une enquête"""
    try:
        data = request.json
        nouveau_statut = data.get('statut_validation')
        
        if nouveau_statut not in ['en_attente', 'confirmee', 'refusee']:
            return jsonify({
                'success': False,
                'error': 'Statut de validation invalide'
            }), 400
        
        # Vérifier si l'enquête existe
        donnee = db.session.get(Donnee, donnee_id)
        if not donnee:
            return jsonify({
                'success': False,
                'error': 'Enquête non trouvée'
            }), 404
        
        # Mettre à jour le statut
        donnee.statut_validation = nouveau_statut
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Statut de validation mis à jour',
            'data': {
                'id': donnee.id,
                'statut_validation': donnee.statut_validation
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_validation_routes(app):
    """Enregistre les routes pour la validation"""
    app.register_blueprint(validation_bp)
