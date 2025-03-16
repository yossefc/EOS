from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models.models import db, Fichier, Donnee
import pandas as pd

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'ost'}

@files_bp.route('/parse', methods=['POST'])
def parse_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

    try:
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Vérifier si le fichier existe déjà
        existing_file = Fichier.query.filter_by(nom=filename).first()
        if existing_file:
            return jsonify({
                'error': 'Le fichier existe déjà',
                'existing_file_info': {
                    'nom': existing_file.nom,
                    'date_upload': existing_file.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                    'nombre_donnees': Donnee.query.filter_by(fichier_id=existing_file.id).count()
                }
            }), 409

        # Sauvegarder le fichier
        file.save(filepath)
        
        # Créer l'entrée dans la base de données
        new_file = Fichier(
            nom=filename,
            date_upload=datetime.now(),
            chemin=filepath
        )
        db.session.add(new_file)
        db.session.commit()

        # Lire et parser le fichier OST
        # Note: Cette partie doit être adaptée selon le format exact de vos fichiers OST
        df = pd.read_csv(filepath, delimiter=';')  # Ajustez le délimiteur selon votre format
        
        # Ajouter les données
        for _, row in df.iterrows():
            donnee = Donnee(
                numeroDossier=row.get('numeroDossier', ''),
                nom=row.get('nom', ''),
                prenom=row.get('prenom', ''),
                typeDemande=row.get('typeDemande', ''),
                fichier_id=new_file.id
            )
            # Si c'est une contestation (type = 'CON'), chercher l'enquête originale
            # Dans la fonction parse_file

            # Si c'est une contestation, rechercher l'enquête originale
            if donnee.typeDemande == 'CON':
                # Rechercher l'enquête originale par numéro de dossier contesté
                enquete_originale = Donnee.query.filter_by(
                    numeroDossier=row.get('numeroDemandeContestee', '')
                ).first()
                
                if enquete_originale:
                    # Marquer comme contestation
                    donnee.est_contestation = True
                    donnee.enquete_originale_id = enquete_originale.id
                    donnee.date_contestation = datetime.now().date()
                    donnee.motif_contestation_code = row.get('codeMotif', '')
                    donnee.motif_contestation_detail = row.get('motifDeContestation', '')
                    
                    # Récupérer l'enquêteur de l'enquête originale
                    donnee.enqueteurId = enquete_originale.enqueteurId
                    
                    # Ajouter l'événement à l'historique
                    enquete_originale.add_to_history(
                        'contestation', 
                        f"Contestation reçue: {donnee.numeroDossier}. Motif: {donnee.motif_contestation_detail}",
                        'Système d\'import'
                    )
                    
                    # Mettre à jour l'enquête originale
                    db.session.add(enquete_originale)
                
                # Ajouter à l'historique de la contestation
                donnee.add_to_history(
                    'creation', 
                    f"Contestation de l'enquête {row.get('numeroDemandeContestee', '')}",
                    'Système d\'import'
                )
            else:
                # Pour les enquêtes normales
                donnee.add_to_history(
                    'creation',
                    f"Création de l'enquête depuis le fichier {filename}",
                    'Système d\'import'
                )
            
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fichier importé avec succès',
            'file_id': new_file.id
        }), 200

    except Exception as e:
        db.session.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 400

@files_bp.route('/replace-file', methods=['POST'])
def replace_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Supprimer l'ancien fichier et ses données
        existing_file = Fichier.query.filter_by(nom=filename).first()
        if existing_file:
            Donnee.query.filter_by(fichier_id=existing_file.id).delete()
            db.session.delete(existing_file)
            if os.path.exists(existing_file.chemin):
                os.remove(existing_file.chemin)
        
        # Sauvegarder le nouveau fichier
        file.save(filepath)
        
        # Créer la nouvelle entrée
        new_file = Fichier(
            nom=filename,
            date_upload=datetime.now(),
            chemin=filepath
        )
        db.session.add(new_file)
        db.session.commit()

        # Lire et parser le fichier OST
        df = pd.read_csv(filepath, delimiter=';')
        
        # Ajouter les nouvelles données
        for _, row in df.iterrows():
            donnee = Donnee(
                numeroDossier=row.get('numeroDossier', ''),
                nom=row.get('nom', ''),
                prenom=row.get('prenom', ''),
                typeDemande=row.get('typeDemande', ''),
                fichier_id=new_file.id
            )
            db.session.add(donnee)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fichier remplacé avec succès',
            'file_id': new_file.id
        }), 200

    except Exception as e:
        db.session.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 400

@files_bp.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # Récupérer les 10 derniers fichiers
        derniers_fichiers = Fichier.query.order_by(Fichier.date_upload.desc()).limit(10).all()
        
        stats = {
            'derniers_fichiers': [{
                'id': f.id,
                'nom': f.nom,
                'date_upload': f.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                'nombre_donnees': Donnee.query.filter_by(fichier_id=f.id).count()
            } for f in derniers_fichiers]
        }
        
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        file = Fichier.query.get_or_404(file_id)
        
        # Supprimer les données associées
        Donnee.query.filter_by(fichier_id=file.id).delete()
        
        # Supprimer le fichier physique
        if os.path.exists(file.chemin):
            os.remove(file.chemin)
        
        # Supprimer l'entrée de la base de données
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'message': 'Fichier supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
