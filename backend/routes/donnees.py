from flask import Blueprint, jsonify, request
from models.models import Donnee
from extensions import db

donnees_bp = Blueprint('donnees', __name__)

@donnees_bp.route('/api/donnees', methods=['GET'])
def get_donnees():
    try:
        donnees = Donnee.query.all()
        return jsonify([{
            'numeroDossier': d.numeroDossier,
            'referenceDossier': d.referenceDossier,
            'typeDemande': d.typeDemande,
            'nom': d.nom,
            'prenom': d.prenom,
            'dateNaissance': d.dateNaissance.strftime('%Y-%m-%d') if d.dateNaissance else None,
            'lieuNaissance': d.lieuNaissance,
            'codePostal': d.codePostal,
            'ville': d.ville,
            'numeroDemande': d.numeroDemande,
            'numeroDemandeContestee': d.numeroDemandeContestee,
            'dateRetourEspere': d.dateRetourEspere.strftime('%Y-%m-%d') if d.dateRetourEspere else None,
            'enqueteurId': d.enqueteurId
        } for d in donnees])
    except Exception as e:
        print(f"Error: {str(e)}")  # Pour le débogage
        return jsonify({'error': str(e)}), 500

@donnees_bp.route('/api/assign-enquete', methods=['POST'])
def assign_enquete():
    try:
        data = request.get_json()
        enquete_id = data.get('enqueteId')
        enqueteur_id = data.get('enqueteurId')
        
        enquete = Donnee.query.filter_by(numeroDossier=enquete_id).first()
        if not enquete:
            return jsonify({'error': 'Enquête non trouvée'}), 404
            
        enquete.enqueteurId = enqueteur_id
        db.session.commit()
        
        return jsonify({'message': 'Assignation réussie'}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
