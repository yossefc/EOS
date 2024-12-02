from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Donnee, Fichier
from utils import process_file_content
import logging
import sys

# Configuration avancée du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/parse', methods=['POST'])
    def parse_file():
        logger.info("Début du traitement de la requête d'import")
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # Vérifier si le fichier existe déjà
            existing_file = Fichier.query.filter_by(nom=file.filename).first()
            if existing_file:
                return jsonify({
                    "status": "file_exists",
                    "message": "Ce fichier existe déjà. Voulez-vous le remplacer ?",
                    "existing_file_info": {
                        "nom": existing_file.nom,
                        "date_upload": existing_file.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                        "nombre_donnees": Donnee.query.filter_by(fichier_id=existing_file.id).count()
                    }
                }), 409

            # 1. Lire le contenu du fichier
            content = file.read()
            if not content:
                return jsonify({"error": "Fichier vide"}), 400

            try:
                # 2. Créer d'abord l'entrée du fichier
                nouveau_fichier = Fichier(nom=file.filename)
                db.session.add(nouveau_fichier)
                db.session.commit()
                logger.info(f"Fichier créé avec ID: {nouveau_fichier.id}")

                # 3. Traiter le contenu avec l'ID du fichier
                processed_records = process_file_content(content, nouveau_fichier.id)
                
                if processed_records:
                    return jsonify({
                        "message": "Fichier traité avec succès",
                        "file_id": nouveau_fichier.id,
                        "records_processed": len(processed_records)
                    })
                else:
                    # Si aucun enregistrement n'a été créé, on supprime le fichier
                    db.session.delete(nouveau_fichier)
                    db.session.commit()
                    return jsonify({"error": "Aucun enregistrement valide trouvé dans le fichier"}), 400

            except Exception as e:
                # En cas d'erreur, on s'assure de supprimer le fichier s'il a été créé
                if 'nouveau_fichier' in locals():
                    try:
                        db.session.delete(nouveau_fichier)
                        db.session.commit()
                    except:
                        db.session.rollback()
                
                logger.error(f"Erreur lors du traitement du contenu: {str(e)}")
                return jsonify({"error": str(e)}), 400

        except Exception as e:
            logger.error(f"Erreur lors du traitement: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/replace-file', methods=['POST'])
    def replace_file():
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # Supprimer l'ancien fichier et ses données
            existing_file = Fichier.query.filter_by(nom=file.filename).first()
            if existing_file:
                Donnee.query.filter_by(fichier_id=existing_file.id).delete()
                db.session.delete(existing_file)
                db.session.commit()

            # Créer le nouveau fichier
            nouveau_fichier = Fichier(nom=file.filename)
            db.session.add(nouveau_fichier)
            db.session.commit()
            
            content = file.read()
            processed_records = process_file_content(content, nouveau_fichier.id)

            return jsonify({
                "message": "Fichier remplacé avec succès",
                "file_id": nouveau_fichier.id,
                "records_processed": len(processed_records)
            })

        except Exception as e:
            logger.error(f"Erreur lors du remplacement: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
            try:
                total_fichiers = Fichier.query.count()
                total_donnees = Donnee.query.count()
                
                derniers_fichiers = (Fichier.query
                                .order_by(Fichier.date_upload.desc())
                                .limit(5)
                                .all())
                
                fichiers_info = [{
                    "id": f.id,
                    "nom": f.nom,
                    "date_upload": f.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                    "nombre_donnees": Donnee.query.filter_by(fichier_id=f.id).count()
                } for f in derniers_fichiers]
                
                logger.info(f"Stats - Fichiers: {total_fichiers}, Données: {total_donnees}")
                return jsonify({
                    "total_fichiers": total_fichiers,
                    "total_donnees": total_donnees,
                    "derniers_fichiers": fichiers_info
                })
                
            except Exception as e:
                logger.error(f"Erreur dans get_stats: {str(e)}")
                return jsonify({"error": str(e)}), 500

        # Route de suppression
    @app.route('/api/files/<int:file_id>', methods=['DELETE'])
    def delete_file(file_id):
            try:
                logger.info(f"Tentative de suppression du fichier {file_id}")
                fichier = Fichier.query.get_or_404(file_id)
                
                # Supprimer d'abord toutes les données associées
                try:
                    Donnee.query.filter_by(fichier_id=file_id).delete()
                    logger.info(f"Données du fichier {file_id} supprimées")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression des données: {e}")
                    db.session.rollback()
                    return jsonify({"error": "Erreur lors de la suppression des données"}), 500
                
                # Supprimer le fichier
                try:
                    db.session.delete(fichier)
                    db.session.commit()
                    logger.info(f"Fichier {file_id} supprimé avec succès")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du fichier: {e}")
                    db.session.rollback()
                    return jsonify({"error": "Erreur lors de la suppression du fichier"}), 500
                
                return jsonify({"message": "Fichier supprimé avec succès"}), 200
                
            except Exception as e:
                logger.error(f"Erreur générale lors de la suppression: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route('/api/donnees', methods=['GET'])
    def get_donnees():
            """Route pour récupérer les données"""
            try:
                donnees = Donnee.query.all()
                data = [donnee.to_dict() for donnee in donnees]
                return jsonify({
                    "success": True,
                    "data": data,
                    "count": len(data)
                })
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des données: {str(e)}")
                return jsonify({"error": str(e)}), 500

    @app.route('/donnees', methods=['GET'])
    def get_donnees_alt():
            """Route alternative pour la récupération des données"""
            return get_donnees()
    return app

# Création de l'application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)