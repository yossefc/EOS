# backend/routes/enqueteur_auth.py
from flask import Blueprint, request, jsonify
from models.enqueteur import Enqueteur
import logging

logger = logging.getLogger(__name__)

enqueteur_auth_bp = Blueprint('enqueteur_auth', __name__)

@enqueteur_auth_bp.route('/api/enqueteur/auth', methods=['POST'])
def authenticate_enqueteur():
    """Authentifie un enquêteur par son email"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email obligatoire'
            }), 400
            
        # Rechercher l'enquêteur par email
        enqueteur = Enqueteur.query.filter_by(email=email).first()
        
        if not enqueteur:
            return jsonify({
                'success': False,
                'error': 'Aucun enquêteur trouvé avec cet email'
            }), 404
            
        # Renvoyer les informations de l'enquêteur
        return jsonify({
            'success': True,
            'message': 'Authentification réussie',
            'data': enqueteur.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification de l'enquêteur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enqueteur_auth_bp.route('/api/enqueteur/<int:id>/enquetes', methods=['GET'])
def get_enqueteur_enquetes(id):
    """Récupère les enquêtes assignées à un enquêteur spécifique"""
    try:
        # Vérifier que l'enquêteur existe
        enqueteur = Enqueteur.query.get_or_404(id)
        
        # Récupérer les enquêtes assignées à cet enquêteur
        # avec les détails enquêteur
        from models.models import Donnee, db
        from models.models_enqueteur import DonneeEnqueteur

        # Requête avec jointure
        enquetes = (db.session.query(Donnee)
                  .outerjoin(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id)
                  .filter(Donnee.enqueteurId == id)
                  .all())
        
        # Construire la réponse avec les données complètes
        enquetes_data = []
        for enquete in enquetes:
            enquete_dict = enquete.to_dict()
            if enquete.donnee_enqueteur:
                # Ajouter les données de l'enquêteur à la réponse
                for k, v in enquete.donnee_enqueteur.to_dict().items():
                    if k not in ['id', 'donnee_id']:
                        enquete_dict[k] = v
            
            enquetes_data.append(enquete_dict)
        
        return jsonify({
            'success': True,
            'data': enquetes_data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes de l'enquêteur {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_enqueteur_auth_routes(app):
    """Enregistre les routes d'authentification des enquêteurs"""
    app.register_blueprint(enqueteur_auth_bp)