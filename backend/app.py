from flask import Flask, request, jsonify
from extensions import init_extensions, db
from routes.enqueteur import register_enqueteur_routes
from routes.vpn_template import register_vpn_template_routes
from routes.export import register_export_routes  # Nouvelle route d'export
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur
from models.enqueteur import Enqueteur
from datetime import datetime
import logging
import os
import sys
import codecs
from config import create_app
from flask_cors import CORS

# Configuration de l'encodage par défaut
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration avancée du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def init_app():
    app = create_app()
    
    # Configuration CORS de base
    CORS(app)
    
    @app.after_request
    def after_request(response):
        response.headers.set('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response
        
    init_extensions(app)
    register_enqueteur_routes(app)
    register_vpn_template_routes(app)
    register_export_routes(app)  # Enregistrement des routes d'export

    with app.app_context():
        db.create_all()

    @app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
    def test_cors():
        if request.method == 'OPTIONS':
            return '', 200
        return jsonify({"status": "ok"})

    @app.route('/api/donnees', methods=['GET'])
    def get_donnees():
        try:
            donnees = Donnee.query.all()
            return jsonify({
                "success": True,
                "data": [donnee.to_dict() for donnee in donnees]
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/donnees/<int:id>', methods=['DELETE'])
    def delete_donnee(id):
        try:
            donnee = Donnee.query.get_or_404(id)
            db.session.delete(donnee)
            db.session.commit()
            return jsonify({'message': 'Enregistrement supprimé avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression : {str(e)}")
            return jsonify({'error': 'Erreur lors de la suppression'}), 500

    @app.route('/api/donnees', methods=['POST'])
    def add_donnee():
        try:
            data = request.json
            nouvelle_donnee = Donnee(
                numeroDossier=data.get('numeroDossier'),
                referenceDossier=data.get('referenceDossier'),
                typeDemande=data.get('typeDemande'),
                nom=data.get('nom'),
                prenom=data.get('prenom'),
                dateNaissance=datetime.strptime(data.get('dateNaissance'), '%Y-%m-%d').date() if data.get('dateNaissance') else None,
                lieuNaissance=data.get('lieuNaissance'),
                codePostal=data.get('codePostal'),
                ville=data.get('ville'),
                adresse1=data.get('adresse1'),
                adresse2=data.get('adresse2'),
                adresse3=data.get('adresse3'),
                telephonePersonnel=data.get('telephonePersonnel'),
                elementDemandes=data.get('elementDemandes', 'AT'),
                elementObligatoires=data.get('elementObligatoires', 'A')
            )
            db.session.add(nouvelle_donnee)
            db.session.commit()
            
            # Créer automatiquement une entrée dans DonneeEnqueteur
            new_donnee_enqueteur = DonneeEnqueteur(
                donnee_id=nouvelle_donnee.id
            )
            db.session.add(new_donnee_enqueteur)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Données ajoutées avec succès',
                'data': nouvelle_donnee.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['GET'])
    def get_donnee_enqueteur(donnee_id):
        try:
            # Récupérer les données enquêteur
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            
            if not donnee_enqueteur:
                return jsonify({
                    'success': False, 
                    'error': 'Aucune donnée enquêteur trouvée pour cet ID'
                }), 404
                
            return jsonify({
                'success': True, 
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données enquêteur: {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e)
            }), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['POST'])
    def update_donnee_enqueteur(donnee_id):
        try:
            data = request.get_json()
            logger.info(f"Données reçues pour mise à jour: {data}")
            
            # Récupérer l'entrée existante ou en créer une nouvelle
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            if not donnee_enqueteur:
                donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee_id)
                db.session.add(donnee_enqueteur)
            
            # Mettre à jour tous les champs reçus
            if 'code_resultat' in data:
                donnee_enqueteur.code_resultat = data.get('code_resultat')
            if 'elements_retrouves' in data:
                donnee_enqueteur.elements_retrouves = data.get('elements_retrouves')
            if 'flag_etat_civil_errone' in data:
                donnee_enqueteur.flag_etat_civil_errone = data.get('flag_etat_civil_errone')
            
            # Adresse
            if 'adresse1' in data:
                donnee_enqueteur.adresse1 = data.get('adresse1')
            if 'adresse2' in data:
                donnee_enqueteur.adresse2 = data.get('adresse2')
            if 'adresse3' in data:
                donnee_enqueteur.adresse3 = data.get('adresse3')
            if 'adresse4' in data:
                donnee_enqueteur.adresse4 = data.get('adresse4')
            if 'code_postal' in data:
                donnee_enqueteur.code_postal = data.get('code_postal')
            if 'ville' in data:
                donnee_enqueteur.ville = data.get('ville')
            if 'pays_residence' in data:
                donnee_enqueteur.pays_residence = data.get('pays_residence')
            if 'telephone_personnel' in data:
                donnee_enqueteur.telephone_personnel = data.get('telephone_personnel')
            
            # Employeur
            if 'nom_employeur' in data:
                donnee_enqueteur.nom_employeur = data.get('nom_employeur')
            if 'telephone_employeur' in data:
                donnee_enqueteur.telephone_employeur = data.get('telephone_employeur')
            if 'telecopie_employeur' in data:
                donnee_enqueteur.telecopie_employeur = data.get('telecopie_employeur')
            if 'adresse1_employeur' in data:
                donnee_enqueteur.adresse1_employeur = data.get('adresse1_employeur')
            if 'adresse2_employeur' in data:
                donnee_enqueteur.adresse2_employeur = data.get('adresse2_employeur')
            if 'adresse3_employeur' in data:
                donnee_enqueteur.adresse3_employeur = data.get('adresse3_employeur')
            if 'adresse4_employeur' in data:
                donnee_enqueteur.adresse4_employeur = data.get('adresse4_employeur')
            if 'code_postal_employeur' in data:
                donnee_enqueteur.code_postal_employeur = data.get('code_postal_employeur')
            if 'ville_employeur' in data:
                donnee_enqueteur.ville_employeur = data.get('ville_employeur')
            if 'pays_employeur' in data:
                donnee_enqueteur.pays_employeur = data.get('pays_employeur')
            
            # Banque
            if 'banque_domiciliation' in data:
                donnee_enqueteur.banque_domiciliation = data.get('banque_domiciliation')
            if 'libelle_guichet' in data:
                donnee_enqueteur.libelle_guichet = data.get('libelle_guichet')
            if 'titulaire_compte' in data:
                donnee_enqueteur.titulaire_compte = data.get('titulaire_compte')
            if 'code_banque' in data:
                donnee_enqueteur.code_banque = data.get('code_banque')
            if 'code_guichet' in data:
                donnee_enqueteur.code_guichet = data.get('code_guichet')
            
            # Décès
            if 'date_deces' in data:
                donnee_enqueteur.date_deces = datetime.strptime(data.get('date_deces'), '%Y-%m-%d').date() if data.get('date_deces') else None
            if 'numero_acte_deces' in data:
                donnee_enqueteur.numero_acte_deces = data.get('numero_acte_deces')
            if 'code_insee_deces' in data:
                donnee_enqueteur.code_insee_deces = data.get('code_insee_deces')
            if 'code_postal_deces' in data:
                donnee_enqueteur.code_postal_deces = data.get('code_postal_deces')
            if 'localite_deces' in data:
                donnee_enqueteur.localite_deces = data.get('localite_deces')
            
            # Revenus
            if 'commentaires_revenus' in data:
                donnee_enqueteur.commentaires_revenus = data.get('commentaires_revenus')
            
            # Gestion des montants (avec conversion en decimal)
            if 'montant_salaire' in data:
                montant = data.get('montant_salaire')
                donnee_enqueteur.montant_salaire = float(montant) if montant else None
            
            # Mémos
            if 'memo1' in data:
                donnee_enqueteur.memo1 = data.get('memo1')
            if 'memo2' in data:
                donnee_enqueteur.memo2 = data.get('memo2')
            if 'memo3' in data:
                donnee_enqueteur.memo3 = data.get('memo3')
            if 'memo4' in data:
                donnee_enqueteur.memo4 = data.get('memo4')
            if 'memo5' in data:
                donnee_enqueteur.memo5 = data.get('memo5')
            
            # Mise à jour de la date de modification
            donnee_enqueteur.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Données mises à jour avec succès',
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour des données enquêteur: {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e)
            }), 400

    @app.route('/api/assign-enquete', methods=['POST'])
    def assign_enquete():
        try:
            data = request.json
            logger.info(f"Données reçues pour l'assignation: {data}")
            
            enquete_id = data.get('enqueteId')
            enqueteur_id = data.get('enqueteurId')
            
            logger.info(f"Tentative d'assignation de l'enquête {enquete_id} à l'enquêteur {enqueteur_id}")
            
            if not enquete_id:
                logger.error("Erreur: enqueteId manquant")
                return jsonify({'success': False, 'error': 'Missing enqueteId'}), 400
                
            enquete = Donnee.query.filter_by(numeroDossier=enquete_id).first()
            if not enquete:
                logger.error(f"Erreur: enquête {enquete_id} non trouvée")
                return jsonify({'success': False, 'error': 'Enquête not found'}), 404
                
            if enqueteur_id:
                enqueteur = Enqueteur.query.get(enqueteur_id)
                if not enqueteur:
                    logger.error(f"Erreur: enquêteur {enqueteur_id} non trouvé")
                    return jsonify({'success': False, 'error': 'Enquêteur not found'}), 404
                logger.info(f"Enquêteur trouvé: {enqueteur.nom}")
            
            logger.info(f"Assignation de l'enquête {enquete_id} à l'enquêteur {enqueteur_id}")
            enquete.enqueteurId = enqueteur_id if enqueteur_id != '' else None
            db.session.commit()
            logger.info("Assignation réussie")
            
            return jsonify({
                'success': True,
                'message': 'Assignment successful',
                'data': enquete.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"Erreur lors de l'assignation: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

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
                from utils import process_file_content
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
            from utils import process_file_content
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

    return app

if __name__ == '__main__':
    app = init_app()
    app.run(debug=True)