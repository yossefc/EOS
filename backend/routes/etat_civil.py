from flask import Blueprint, request, jsonify
from models.models_enqueteur import DonneeEnqueteur
from models.models import Donnee
from extensions import db
from datetime import datetime
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

etat_civil_bp = Blueprint('etat_civil', __name__)

@etat_civil_bp.route('/api/donnees-enqueteur/<int:donnee_id>/etat-civil', methods=['POST'])
def update_etat_civil(donnee_id):
    """
    Met à jour les informations d'état civil corrigées pour une donnée enquêteur
    """
    try:
        data = request.get_json()
        logger.info(f"Mise à jour de l'état civil pour donnée {donnee_id}: {data}")
        
        # Récupérer la donnée originale pour référence
        donnee = Donnee.query.get_or_404(donnee_id)
        
        # Récupérer ou créer l'entrée DonneeEnqueteur
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
        if not donnee_enqueteur:
            donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee_id)
            db.session.add(donnee_enqueteur)
        
        # Mise à jour des champs d'état civil corrigé
        if 'qualite_corrigee' in data:
            donnee_enqueteur.qualite_corrigee = data.get('qualite_corrigee')
        if 'nom_corrige' in data:
            donnee_enqueteur.nom_corrige = data.get('nom_corrige')
        if 'prenom_corrige' in data:
            donnee_enqueteur.prenom_corrige = data.get('prenom_corrige')
        if 'nom_patronymique_corrige' in data:
            donnee_enqueteur.nom_patronymique_corrige = data.get('nom_patronymique_corrige')
        if 'date_naissance_corrigee' in data:
            date_str = data.get('date_naissance_corrigee')
            if date_str:
                try:
                    # Convertir la date du format JJ/MM/AAAA
                    day, month, year = date_str.split('/')
                    date_obj = datetime(int(year), int(month), int(day)).date()
                    donnee_enqueteur.date_naissance_corrigee = date_obj
                except Exception as e:
                    logger.error(f"Erreur lors de la conversion de la date: {e}")
                    return jsonify({
                        'success': False, 
                        'error': f"Format de date invalide: {date_str}"
                    }), 400
        if 'lieu_naissance_corrige' in data:
            donnee_enqueteur.lieu_naissance_corrige = data.get('lieu_naissance_corrige')
        if 'code_postal_naissance_corrige' in data:
            donnee_enqueteur.code_postal_naissance_corrige = data.get('code_postal_naissance_corrige')
        if 'pays_naissance_corrige' in data:
            donnee_enqueteur.pays_naissance_corrige = data.get('pays_naissance_corrige')
            
        # Mise à jour du flag d'état civil erroné
        if 'flag_etat_civil_errone' in data:
            donnee_enqueteur.flag_etat_civil_errone = data.get('flag_etat_civil_errone')
            
        # Mise à jour du type de divergence
        if 'type_divergence' in data:
            donnee_enqueteur.type_divergence = data.get('type_divergence')
        
        # Sauvegarde des modifications
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'État civil corrigé mis à jour avec succès',
            'data': donnee_enqueteur.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la mise à jour de l'état civil: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_etat_civil_routes(app):
    """
    Enregistre les routes de gestion d'état civil dans l'application
    """
    app.register_blueprint(etat_civil_bp)