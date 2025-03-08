# backend/routes/vpn_download.py
from flask import Blueprint, send_file, jsonify
from models.enqueteur import Enqueteur
import os
import logging

logger = logging.getLogger(__name__)

vpn_download_bp = Blueprint('vpn_download', __name__)

@vpn_download_bp.route('/api/download/vpn-config/<int:id>', methods=['GET'])
def download_vpn_config(id):
    """Télécharge la configuration VPN d'un enquêteur spécifique"""
    try:
        # Vérifier que l'enquêteur existe
        enqueteur = Enqueteur.query.get_or_404(id)
        
        # Chemin du fichier de configuration VPN
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'vpn_configs', f'client{id}.ovpn')
        
        # Vérifier si le fichier existe
        if not os.path.exists(config_path):
            # Générer la configuration à la volée si elle n'existe pas
            try:
                config_path = enqueteur.generate_vpn_config()
                from extensions import db
                db.session.commit()
            except Exception as e:
                logger.error(f"Erreur lors de la génération de la configuration VPN: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f"Erreur lors de la génération de la configuration VPN: {str(e)}"
                }), 500
        
        # Envoyer le fichier au client
        return send_file(
            config_path,
            as_attachment=True,
            download_name=f'client{id}.ovpn',
            mimetype='application/x-openvpn-profile'
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la configuration VPN: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_vpn_download_routes(app):
    """Enregistre les routes de téléchargement VPN"""
    app.register_blueprint(vpn_download_bp)