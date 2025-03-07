# backend/routes/vpn_template.py

from flask import request, jsonify
import os
import sys
import logging

# Ajout du chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

def register_vpn_template_routes(app):
    @app.route('/api/vpn-template', methods=['POST'])
    def upload_vpn_template():
        """Upload le fichier template de configuration VPN"""
        try:
            # Vérifier si un fichier a été envoyé
            if 'file' not in request.files:
                return jsonify({'error': 'Aucun fichier fourni'}), 400
                
            file = request.files['file']
            
            # Vérifier l'extension du fichier
            if not file.filename.endswith('.ovpn'):
                return jsonify({'error': 'Le fichier doit être un .ovpn'}), 400
                
            # Créer le chemin du dossier template
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(base_dir, 'vpn_template')
            
            # Créer le dossier s'il n'existe pas
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
                
            # Chemin complet du fichier template
            template_path = os.path.join(template_dir, 'client_template.ovpn')
            
            # Sauvegarder le fichier
            file.save(template_path)
            
            logger.info(f"Template VPN uploadé avec succès: {template_path}")
            
            return jsonify({
                'success': True,
                'message': 'Template VPN uploadé avec succès',
                'path': template_path
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload du template VPN: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Erreur lors de l'upload: {str(e)}"
            }), 500
            
    @app.route('/api/vpn-template', methods=['GET'])
    def check_vpn_template():
        """Vérifie si un template VPN existe"""
        try:
            # Chemin du fichier template
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(base_dir, 'vpn_template', 'client_template.ovpn')
            
            # Vérifier si le fichier existe
            exists = os.path.exists(template_path)
            
            return jsonify({
                'success': True,
                'exists': exists,
                'path': template_path if exists else None
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du template VPN: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Erreur lors de la vérification: {str(e)}"
            }), 500

    @app.route('/api/vpn-template/download', methods=['GET'])
    def download_vpn_template():
        """Télécharge le template VPN actuel"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(base_dir, 'vpn_template', 'client_template.ovpn')
            
            if not os.path.exists(template_path):
                return jsonify({
                    'success': False,
                    'error': 'Aucun template VPN trouvé'
                }), 404
            
            return send_file(
                template_path,
                as_attachment=True,
                download_name='client_template.ovpn',
                mimetype='application/x-openvpn-profile'
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du template VPN: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Erreur lors du téléchargement: {str(e)}"
            }), 500