# backend/routes/enqueteur.py
from flask import jsonify, request, send_file
from models.enqueteur import Enqueteur
from extensions import db
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def register_enqueteur_routes(app):
    @app.route('/api/enqueteurs', methods=['GET'])
    def get_enqueteurs():
        try:
            enqueteurs = Enqueteur.query.all()
            return jsonify({
                'success': True,
                'data': [enqueteur.to_dict() for enqueteur in enqueteurs]
            })
        except Exception as e:
            app.logger.error(f"Erreur lors de la récupération des enquêteurs: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/enqueteurs', methods=['POST'])
    def create_enqueteur():
        try:
            data = request.json
            nouvel_enqueteur = Enqueteur(
                nom=data['nom'],
                prenom=data['prenom'],
                email=data['email'],
                telephone=data.get('telephone')
            )
            
            db.session.add(nouvel_enqueteur)
            db.session.commit()
            
            try:
                nouvel_enqueteur.generate_vpn_config()
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Erreur VPN: {str(e)}")
                
            return jsonify({
                'success': True,
                'message': 'Enquêteur créé avec succès',
                'data': nouvel_enqueteur.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/enqueteurs/<int:id>', methods=['DELETE'])
    def delete_enqueteur(id):
        try:
            enqueteur = Enqueteur.query.get_or_404(id)
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'vpn_configs', f'enqueteur_{id}.ovpn')
            if os.path.exists(config_path):
                os.remove(config_path)
            
            db.session.delete(enqueteur)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Enquêteur supprimé avec succès'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/enqueteurs/<int:id>/vpn-config', methods=['GET'])
    def get_vpn_config(id):
        try:
            enqueteur = Enqueteur.query.get_or_404(id)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'vpn_configs', f'client{id}.ovpn')
            
            if not os.path.exists(config_path):
                config_path = enqueteur.generate_vpn_config()
                db.session.commit()
            
            return jsonify({
                'success': True,
                'config_path': config_path,
                'message': 'Configuration VPN générée avec succès',
                'enqueteur': {
                    'nom': enqueteur.nom,
                    'prenom': enqueteur.prenom,
                    'email': enqueteur.email
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# backend/routes/vpn_template.py
from flask import request, jsonify
import os

def register_vpn_template_routes(app):
    @app.route('/api/vpn-template', methods=['POST'])
    def upload_vpn_template():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'Aucun fichier fourni'}), 400
                
            file = request.files['file']
            if not file.filename.endswith('.ovpn'):
                return jsonify({'error': 'Le fichier doit être un .ovpn'}), 400
                
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(base_dir, 'vpn_template')
            
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
                
            template_path = os.path.join(template_dir, 'client_template.ovpn')
            file.save(template_path)
            
            return jsonify({
                'message': 'Template VPN uploadé avec succès',
                'path': template_path
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/vpn-template', methods=['GET'])
    def check_vpn_template():
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(base_dir, 'vpn_template', 'client_template.ovpn')
            
            exists = os.path.exists(template_path)
            
            return jsonify({
                'exists': exists,
                'path': template_path if exists else None
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500