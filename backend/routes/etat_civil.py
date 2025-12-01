# backend/routes/etat_civil.py

from flask import Blueprint, request, jsonify
import logging
from models.models_enqueteur import DonneeEnqueteur
from extensions import db
from datetime import datetime

etat_civil_bp = Blueprint('etat_civil', __name__)
logger = logging.getLogger(__name__)

def register_etat_civil_routes(app):
    @app.route('/api/etat-civil/<int:donnee_id>', methods=['GET'])
    def get_etat_civil(donnee_id):
        """Récupérer les informations d'état civil pour une donnée"""
        try:
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            
            if not donnee_enqueteur:
                return jsonify({
                    'success': False,
                    'error': 'Aucune donnée trouvée pour cet ID'
                }), 404
                
            # Extraire uniquement les informations d'état civil
            etat_civil_data = {
                'flag_etat_civil_errone': donnee_enqueteur.flag_etat_civil_errone,
                'qualite_corrigee': donnee_enqueteur.qualite_corrigee,
                'nom_corrige': donnee_enqueteur.nom_corrige,
                'prenom_corrige': donnee_enqueteur.prenom_corrige,
                'nom_patronymique_corrige': donnee_enqueteur.nom_patronymique_corrige,
                'date_naissance_corrigee': donnee_enqueteur.date_naissance_corrigee.strftime('%Y-%m-%d') if donnee_enqueteur.date_naissance_corrigee else None,
                'lieu_naissance_corrige': donnee_enqueteur.lieu_naissance_corrige,
                'code_postal_naissance_corrige': donnee_enqueteur.code_postal_naissance_corrige,
                'pays_naissance_corrige': donnee_enqueteur.pays_naissance_corrige,
                'type_divergence': donnee_enqueteur.type_divergence
            }
            
            return jsonify({
                'success': True,
                'data': etat_civil_data
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données d'état civil: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/etat-civil/<int:donnee_id>', methods=['POST'])
    def update_etat_civil(donnee_id):
        """Mettre à jour les informations d'état civil pour une donnée"""
        try:
            data = request.get_json()
            logger.info(f"Données reçues pour mise à jour d'état civil: {data}")
            
            # Récupérer l'entrée existante ou en créer une nouvelle
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            if not donnee_enqueteur:
                donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee_id)
                db.session.add(donnee_enqueteur)
            
            # Mise à jour des champs d'état civil
            if 'flag_etat_civil_errone' in data:
                donnee_enqueteur.flag_etat_civil_errone = data.get('flag_etat_civil_errone')
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
                    # Tenter de convertir la date en objet datetime
                    try:
                        # Pour un format YYYY-MM-DD
                        donnee_enqueteur.date_naissance_corrigee = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            # Pour un format DD/MM/YYYY
                            donnee_enqueteur.date_naissance_corrigee = datetime.strptime(date_str, '%d/%m/%Y').date()
                        except ValueError:
                            logger.warning(f"Format de date non reconnu: {date_str}")
                            # On garde la valeur None
                            donnee_enqueteur.date_naissance_corrigee = None
                else:
                    donnee_enqueteur.date_naissance_corrigee = None
            if 'lieu_naissance_corrige' in data:
                donnee_enqueteur.lieu_naissance_corrige = data.get('lieu_naissance_corrige')
            if 'code_postal_naissance_corrige' in data:
                donnee_enqueteur.code_postal_naissance_corrige = data.get('code_postal_naissance_corrige')
            if 'pays_naissance_corrige' in data:
                donnee_enqueteur.pays_naissance_corrige = data.get('pays_naissance_corrige')
            if 'type_divergence' in data:
                donnee_enqueteur.type_divergence = data.get('type_divergence')
            
            # Mise à jour de la date de modification
            donnee_enqueteur.updated_at = datetime.now()
            
            # Commit des modifications
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Données d\'état civil mises à jour avec succès',
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour des données d'état civil: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Enregistrement du Blueprint
    app.register_blueprint(etat_civil_bp)