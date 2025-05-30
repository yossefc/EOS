# backend/routes/enqueteurs.py

from flask import Blueprint, request, jsonify
from models.enqueteur import Enqueteur
from extensions import db
import os
import logging

logger = logging.getLogger(__name__)

enqueteurs_bp = Blueprint('enqueteurs', __name__)

@enqueteurs_bp.route('/api/enqueteurs', methods=['GET', 'OPTIONS'])
def get_enqueteurs():
    if request.method == 'OPTIONS':
        # Gérer la requête preflight OPTIONS
        return '', 200
        
    try:
        enqueteurs = Enqueteur.query.all()
        return jsonify({
            'success': True,
            'data': [enqueteur.to_dict() for enqueteur in enqueteurs]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêteurs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enqueteurs_bp.route('/api/enqueteurs', methods=['POST', 'OPTIONS'])
def create_enqueteur():
    if request.method == 'OPTIONS':
        # Gérer la requête preflight OPTIONS
        return '', 200
    
    try:
        data = request.json
        
        # Vérification des champs obligatoires
        required_fields = ['nom', 'prenom', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Le champ {field} est obligatoire'
                }), 400
        
        # Vérifier si l'email existe déjà
        existing_enqueteur = Enqueteur.query.filter_by(email=data.get('email')).first()
        if existing_enqueteur:
            return jsonify({
                'success': False,
                'error': 'Un enquêteur avec cet email existe déjà'
            }), 409
        
        # Créer l'enquêteur
        nouvel_enqueteur = Enqueteur(
            nom=data.get('nom'),
            prenom=data.get('prenom'),
            email=data.get('email'),
            telephone=data.get('telephone')
        )
        
        db.session.add(nouvel_enqueteur)
        db.session.commit()
        
        # Générer la configuration VPN
        try:
            config_path = nouvel_enqueteur.generate_vpn_config()
            logger.info(f"Configuration VPN générée: {config_path}")
        except Exception as e:
            logger.warning(f"Erreur lors de la génération de la configuration VPN: {str(e)}")
            # On continue même si la génération de config VPN échoue
        
        return jsonify({
            'success': True,
            'message': 'Enquêteur créé avec succès',
            'data': nouvel_enqueteur.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création de l'enquêteur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enqueteurs_bp.route('/api/enqueteurs/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_enqueteur(id):
    if request.method == 'OPTIONS':
        # Gérer la requête preflight OPTIONS
        return '', 200
    
    try:
        enqueteur = Enqueteur.query.get_or_404(id)
        
        # Supprimer la configuration VPN si elle existe
        try:
            # Chemin présumé de la config VPN
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'vpn_configs', f'client{id}.ovpn')
            
            if os.path.exists(config_path):
                os.remove(config_path)
                logger.info(f"Configuration VPN supprimée: {config_path}")
        except Exception as e:
            logger.warning(f"Erreur lors de la suppression de la configuration VPN: {str(e)}")
        
        # Supprimer les assignations d'enquêtes
        from models.models import Donnee
        Donnee.query.filter_by(enqueteurId=id).update({'enqueteurId': None})
        
        # Supprimer l'enquêteur
        db.session.delete(enqueteur)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enquêteur supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression de l'enquêteur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enqueteurs_bp.route('/api/enqueteurs/<int:id>/vpn-config', methods=['GET', 'OPTIONS'])
def get_vpn_config(id):
    if request.method == 'OPTIONS':
        # Gérer la requête preflight OPTIONS
        return '', 200
    
    try:
        enqueteur = Enqueteur.query.get_or_404(id)
        
        # Vérifier si la configuration VPN existe déjà
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'vpn_configs', f'client{id}.ovpn')
        
        if not os.path.exists(config_path):
            # Générer la configuration si elle n'existe pas
            config_path = enqueteur.generate_vpn_config()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configuration VPN disponible',
            'path': config_path
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la configuration VPN: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@enqueteurs_bp.route('/api/enqueteur/auth', methods=['POST'])
def auth_enqueteur():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requis'}), 400
            
        # Rechercher l'enquêteur par email
        enqueteur = Enqueteur.query.filter_by(email=email).first()
        
        if not enqueteur:
            return jsonify({'success': False, 'error': 'Email non trouvé'}), 404
            
        # Renvoyer les informations de l'enquêteur
        return jsonify({
            'success': True,
            'data': {
                'id': enqueteur.id,  # Assurez-vous que ce champ existe
                'nom': enqueteur.nom,
                'prenom': enqueteur.prenom,
                'email': enqueteur.email
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
def register_enqueteurs_routes(app):
    """Enregistre les routes de gestion des enquêteurs"""
    app.register_blueprint(enqueteurs_bp)