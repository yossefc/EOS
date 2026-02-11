"""
Application Flask principale pour le système EOS
"""
from flask import Flask
from flask_cors import CORS
from extensions import init_extensions, db
from config import Config, setup_logging
import logging
import os
import sys
import codecs
import pandas as pd
import io

# Configuration de l'encodage par défaut pour Windows
if hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Factory pour créer l'application Flask"""
    # Valider que PostgreSQL est configuré
    config_class.validate_database_url()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Mettre à jour l'URI avec la valeur validée
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.validate_database_url()
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Configuration CORS unifiée
    # En développement, autoriser toutes les origines du réseau local
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # Autoriser toutes les origines (développement)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": False  # Doit être False quand origins="*"
        }
    })
    
    # Créer les tables de la base de données via migrations
    with app.app_context():
        # Créer le dossier instance s'il n'existe pas (pour SQLite en dev)
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Importer tous les modèles pour s'assurer qu'ils sont enregistrés
        from models.enquete_archive_file import EnqueteArchiveFile
        from models.export_batch import ExportBatch
        
        # Note: db.create_all() temporairement réactivé pour migration PostgreSQL
        # Après migration, utiliser: flask db upgrade pour les futures modifications
        db.create_all()  # Temporairement réactivé
        logger.info("Base de données initialisée")
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Enregistrer les routes supplémentaires (legacy)
    register_legacy_routes(app)
    
    logger.info("Application Flask créée avec succès")
    return app


def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""
    from routes.enqueteur import register_enqueteurs_routes
    from routes.vpn_template import register_vpn_template_routes
    from routes.export import register_export_routes
    from routes.partner_export import partner_export_bp
    from routes.partner_admin import partner_admin_bp
    from routes.vpn_download import register_vpn_download_routes
    from routes.etat_civil import register_etat_civil_routes
    from routes.tarification import register_tarification_routes
    from routes.paiement import register_paiement_routes
    from routes.enquetes import register_enquetes_routes
    from routes.validation import register_validation_routes
    from routes.validation_v2 import register_validation_v2_routes
    from routes.maintenance import maintenance_bp
    from routes.archives import register_archives_routes
    from routes.excel_export import register_excel_export_routes
    
    # Enregistrer les blueprints
    register_enqueteurs_routes(app)
    register_vpn_template_routes(app)
    register_export_routes(app)
    register_excel_export_routes(app)
    app.register_blueprint(partner_export_bp)
    app.register_blueprint(partner_admin_bp)
    register_vpn_download_routes(app)
    register_etat_civil_routes(app)
    register_tarification_routes(app)
    register_paiement_routes(app)
    register_enquetes_routes(app)
    register_validation_routes(app)
    register_validation_v2_routes(app)
    register_archives_routes(app)
    app.register_blueprint(maintenance_bp)
    
    # Enregistrer le blueprint donnees (s'il n'est pas déjà enregistré ailleurs)
    
    logger.info("Blueprints enregistrés")


def register_legacy_routes(app):
    """
    Enregistre les routes legacy qui n'ont pas encore été migrées vers des blueprints
    Ces routes devraient être progressivement déplacées vers des blueprints appropriés
    """
    from flask import request, jsonify, render_template_string
    
    # ===========================
    # MULTI-CLIENT: Route pour récupérer les clients actifs
    # ===========================
    @app.route('/api/clients', methods=['GET'])
    def get_clients():
        """Récupère la liste des clients actifs"""
        try:
            from client_utils import get_all_active_clients
            
            clients = get_all_active_clients()
            return jsonify({
                "success": True,
                "clients": [client.to_dict() for client in clients]
            })
        except Exception as e:
            logger.error(f"Erreur dans get_clients: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    from models.models import Donnee, Fichier
    from models.models_enqueteur import DonneeEnqueteur
    from models.enqueteur import Enqueteur
    from datetime import datetime
    
    @app.route('/')
    def index():
        """Page d'accueil de l'API"""
        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API EOS - Système de Gestion d'Enquêtes</title>
            <link rel="stylesheet" href="/static/api.css">
        </head>
        <body>
            <div class="container">
                <h1>🚀 API EOS</h1>
                <p class="subtitle">Système de Gestion d'Enquêtes</p>
                
                <div class="status">
                    <div class="status-icon">✅</div>
                    <strong>Serveur opérationnel</strong><br>
                    L'API est en ligne et prête à recevoir des requêtes
                </div>

                <div class="endpoints">
                    <div class="endpoint-group">
                        <h3>📊 Routes Principales</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/stats</span> - Statistiques globales
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/donnees</span> - Liste des données
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enqueteurs</span> - Liste des enquêteurs
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>🔍 Enquêtes</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enquetes/pending</span> - Enquêtes en attente
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enquetes/completed</span> - Enquêtes terminées
                        </div>
                        <div class="endpoint">
                            <span class="method post">POST</span>
                            <span>/api/assign-enquete</span> - Assigner une enquête
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>💰 Tarification & Paiements</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/tarifs/eos</span> - Tarifs EOS
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/paiement/enqueteurs-a-payer</span> - Enquêteurs à payer
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>🧪 Test</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/test-cors</span> - Test de configuration CORS
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>Pour accéder à l'interface frontend, ouvrez : 
                        <a href="http://localhost:5173" target="_blank">http://localhost:5173</a>
                    </p>
                    <p style="margin-top: 10px;">
                        Documentation complète disponible dans le projet
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)
    
    @app.route('/api')
    def api_info():
        """Informations sur l'API au format JSON"""
        return jsonify({
            "name": "API EOS",
            "version": "1.0.0",
            "description": "Système de Gestion d'Enquêtes",
            "status": "operational",
            "endpoints": {
                "stats": "/api/stats",
                "donnees": "/api/donnees",
                "enqueteurs": "/api/enqueteurs",
                "enquetes": "/api/enquetes/*",
                "tarification": "/api/tarifs/*",
                "paiements": "/api/paiement/*",
                "validation": "/api/enquetes/a-valider",
                "export": "/api/export-enquetes"
            },
            "documentation": "Voir la page d'accueil à http://localhost:5000/"
        })
    
    @app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
    def test_cors():
        """Route de test pour vérifier la configuration CORS"""
        if request.method == 'OPTIONS':
            return '', 200
        return jsonify({"status": "ok", "message": "CORS fonctionne correctement"})

    @app.route('/api/stats', methods=['GET', 'OPTIONS'])
    def get_stats():
        """Récupère les statistiques globales et détaillées par client"""
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            from models.client import Client
            from models.models_enqueteur import DonneeEnqueteur
            from sqlalchemy import func

            total_fichiers = Fichier.query.count()
            total_donnees = Donnee.query.count()
            
            # Statistiques par client
            clients = Client.query.all()
            clients_stats = []
            
            for client in clients:
                # Nombre total importé pour ce client
                imported = Donnee.query.filter_by(client_id=client.id).count()
                
                # Nombre traité (ayant une réponse d'enquêteur)
                treated = (db.session.query(func.count(Donnee.id))
                          .join(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id)
                          .filter(Donnee.client_id == client.id)
                          .scalar())
                
                # Nombre archivé (validé)
                archived = Donnee.query.filter_by(client_id=client.id, statut_validation='validee').count()
                
                # Nombre de dossiers "Bon" (Positif - code 'P')
                bon = (db.session.query(func.count(Donnee.id))
                      .join(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id)
                      .filter(Donnee.client_id == client.id, DonneeEnqueteur.code_resultat == 'P')
                      .scalar())
                
                clients_stats.append({
                    "id": client.id,
                    "nom": client.nom,
                    "code": client.code,
                    "imported": imported,
                    "treated": treated,
                    "archived": archived,
                    "bon": bon,
                    "success_rate": round((bon / treated * 100), 1) if treated > 0 else 0
                })

            derniers_fichiers = (Fichier.query
                            .order_by(Fichier.date_upload.desc())
                            .limit(10)
                            .all())
            
            fichiers_info = [{
                "id": f.id,
                "nom": f.nom,
                "date_upload": f.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                "nombre_donnees": Donnee.query.filter_by(fichier_id=f.id).count(),
                "client_nom": f.client.nom if f.client else "Inconnu"
            } for f in derniers_fichiers]
            
            return jsonify({
                "success": True,
                "total_fichiers": total_fichiers,
                "total_donnees": total_donnees,
                "clients_stats": clients_stats,
                "derniers_fichiers": fichiers_info
            })
            
        except Exception as e:
            logger.error(f"Erreur dans get_stats: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/donnees', methods=['GET'])
    def get_donnees():
        """Récupère la liste des données avec pagination (multi-client)"""
        try:
            # MULTI-CLIENT: Récupérer le client
            from client_utils import get_client_or_default
            
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 500, type=int)
            
            # Logique spécifique pour Sherlock
            if client.code == 'RG_SHERLOCK':
                from models import SherlockDonnee
                pagination = SherlockDonnee.query.filter_by(fichier_id=Fichier.id).join(Fichier).filter(Fichier.client_id == client.id).paginate(
                    page=page, per_page=per_page, error_out=False
                )
                # Alternative simplifiée si on n'a pas besoin de jointure complexe (fichier_id est FK)
                # Mais SherlockDonnee n'a pas direct client_id, il passe par fichier_id
                # Ou on peut filtrer par fichier_id globaux du client.
                
                # Correction: SherlockDonnee a fichier_id. Fichier a client_id.
                pagination = (db.session.query(SherlockDonnee)
                             .join(Fichier, SherlockDonnee.fichier_id == Fichier.id)
                             .filter(Fichier.client_id == client.id)
                             .order_by(SherlockDonnee.id.desc())
                             .paginate(page=page, per_page=per_page, error_out=False))
                
                items = pagination.items
                data = []
                for item in items:
                    item_dict = item.to_dict()
                    # Mapping pour le frontend (AssignmentViewer)
                    item_dict['numeroDossier'] = item.dossier_id
                    item_dict['nom'] = item.ec_nom_usage
                    item_dict['prenom'] = item.ec_prenom
                    item_dict['typeDemande'] = item.demande or 'ENQ'
                    # Champs manquants pour éviter les erreurs prop-types
                    item_dict['enqueteurId'] = None 
                    data.append(item_dict)
            else:
                # Comportement standard
                pagination = Donnee.query.filter_by(client_id=client.id).paginate(
                    page=page, per_page=per_page, error_out=False
                )
                data = [donnee.to_dict() for donnee in pagination.items]

            return jsonify({
                "success": True,
                "data": data,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "client_code": client.code
            })
        except Exception as e:
            logger.error(f"Erreur dans get_donnees: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/donnees/<int:donnee_id>/historique', methods=['GET'])
    def get_donnee_historique(donnee_id):
        """Récupère l'historique d'une donnée"""
        try:
            donnee = Donnee.query.get_or_404(donnee_id)
            history = donnee.get_history()
            
            # Récupérer les contestations liées
            contestations = []
            if not donnee.est_contestation:
                contestations_data = Donnee.query.filter_by(enquete_originale_id=donnee.id).all()
                for cont in contestations_data:
                    contestations.append({
                        'id': cont.id,
                        'numeroDossier': cont.numeroDossier,
                        'date': cont.date_contestation.strftime('%Y-%m-%d') if cont.date_contestation else None,
                        'motif_code': cont.motif_contestation_code,
                        'motif_detail': cont.motif_contestation_detail,
                        'enqueteur': cont.enqueteurId
                    })
            
            # Si c'est une contestation, chercher l'enquête originale
            enquete_originale = None
            if donnee.est_contestation and donnee.enquete_originale_id:
                original = db.session.get(Donnee, donnee.enquete_originale_id)
                if original:
                    enquete_originale = {
                        'id': original.id,
                        'numeroDossier': original.numeroDossier,
                        'typeDemande': original.typeDemande,
                        'nom': original.nom,
                        'prenom': original.prenom,
                        'enqueteurId': original.enqueteurId
                    }
            
            # Récupérer l'historique des modifications
            modifications = []
            if donnee.donnee_enqueteur:
                modifications = [{
                    'date': donnee.donnee_enqueteur.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'code_resultat': donnee.donnee_enqueteur.code_resultat,
                    'elements_retrouves': donnee.donnee_enqueteur.elements_retrouves
                }]
            
            return jsonify({
                'success': True,
                'data': {
                    'historique': history,
                    'contestations': contestations,
                    'enquete_originale': enquete_originale,
                    'modifications': modifications,
                    'est_contestation': donnee.est_contestation
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees/<int:id>', methods=['GET'])
    def get_donnee(id):
        """Récupère une donnée spécifique avec les informations du client"""
        try:
            donnee = Donnee.query.get_or_404(id)
            donnee_dict = donnee.to_dict()
            
            # Ajouter les informations du client
            from models.client import Client
            client = db.session.get(Client, donnee.client_id)
            if client:
                donnee_dict['client'] = {
                    'id': client.id,
                    'code': client.code,
                    'nom': client.nom
                }
            
            return jsonify({'success': True, 'data': donnee_dict}), 200
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la donnée: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/donnees/<int:id>', methods=['DELETE'])
    def delete_donnee(id):
        """Supprime une donnée"""
        try:
            donnee = Donnee.query.get_or_404(id)
            db.session.delete(donnee)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Enregistrement supprimé avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            
            # Message d'erreur plus clair pour les violations de contraintes
            error_message = 'Erreur lors de la suppression'
            if 'ForeignKeyViolation' in str(e) or 'foreign key constraint' in str(e).lower():
                error_message = 'Impossible de supprimer ce dossier car il contient des données enquêteur. Exécutez CORRIGER_CASCADE_SUPPRESSION.bat pour résoudre ce problème.'
            
            return jsonify({'success': False, 'error': error_message}), 500

    @app.route('/api/donnees', methods=['POST'])
    def add_donnee():
        """Ajoute une nouvelle donnée avec assignation d'enquêteur (multi-client)"""
        try:
            data = request.json
            
            # MULTI-CLIENT: Récupérer le client
            from client_utils import get_client_or_default
            
            client_id = data.get('client_id')
            client_code = data.get('client_code')
            
            client = get_client_or_default(client_id=client_id, client_code=client_code)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404
            
            nouvelle_donnee = Donnee(
                client_id=client.id,  # MULTI-CLIENT
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
                elementObligatoires=data.get('elementObligatoires', 'A'),
                enqueteurId=data.get('enqueteurId'),  # Assignation d'enquêteur
                fichier_id=data.get('fichier_id', 1)  # Fichier par défaut
            )
            db.session.add(nouvelle_donnee)
            db.session.commit()
            
            # Créer automatiquement une entrée dans DonneeEnqueteur
            new_donnee_enqueteur = DonneeEnqueteur(
                donnee_id=nouvelle_donnee.id,
                client_id=client.id  # MULTI-CLIENT
            )
            db.session.add(new_donnee_enqueteur)
            db.session.commit()
            
            logger.info(f"Nouvelle enquête créée (ID: {nouvelle_donnee.id}) avec enquêteur ID: {nouvelle_donnee.enqueteurId}")
            
            return jsonify({
                'success': True,
                'message': 'Données ajoutées avec succès',
                'data': nouvelle_donnee.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/donnees/<int:id>', methods=['PUT'])
    def update_donnee(id):
        """Met à jour une donnée existante (y compris l'enquêteur assigné)"""
        try:
            donnee = Donnee.query.get_or_404(id)
            data = request.json
            
            # Récupérer le client pour vérifier les permissions
            from models.client import Client
            client = db.session.get(Client, donnee.client_id)
            is_client_x = client and client.code != 'EOS'
            
            # Mettre à jour les champs fournis
            if 'numeroDossier' in data:
                donnee.numeroDossier = data['numeroDossier']
            if 'referenceDossier' in data:
                donnee.referenceDossier = data['referenceDossier']
            if 'typeDemande' in data:
                donnee.typeDemande = data['typeDemande']
            if 'nom' in data:
                donnee.nom = data['nom']
            if 'prenom' in data:
                donnee.prenom = data['prenom']
            
            # Pour CLIENT_X, autoriser la modification de dateNaissance et lieuNaissance
            if 'dateNaissance' in data:
                if data['dateNaissance']:
                    donnee.dateNaissance = datetime.strptime(data['dateNaissance'], '%Y-%m-%d').date()
                elif is_client_x:
                    donnee.dateNaissance = None
            
            if 'lieuNaissance' in data:
                donnee.lieuNaissance = data['lieuNaissance']
            
            if 'codePostal' in data:
                donnee.codePostal = data['codePostal']
            if 'ville' in data:
                donnee.ville = data['ville']
            if 'adresse1' in data:
                donnee.adresse1 = data['adresse1']
            if 'adresse2' in data:
                donnee.adresse2 = data['adresse2']
            if 'adresse3' in data:
                donnee.adresse3 = data['adresse3']
            if 'telephonePersonnel' in data:
                donnee.telephonePersonnel = data['telephonePersonnel']
            if 'elementDemandes' in data:
                donnee.elementDemandes = data['elementDemandes']
            if 'elementObligatoires' in data:
                donnee.elementObligatoires = data['elementObligatoires']
            
            # Assignation/Modification d'enquêteur
            if 'enqueteurId' in data:
                donnee.enqueteurId = data['enqueteurId']
                logger.info(f"Enquête {id} : Enquêteur changé -> ID {donnee.enqueteurId}")
            
            donnee.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Données modifiées avec succès',
                'data': donnee.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la modification: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['GET'])
    def get_donnee_enqueteur(donnee_id):
        """Récupère les données enquêteur pour une donnée (crée automatiquement si inexistant pour PARTNER)"""
        try:
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            
            if not donnee_enqueteur:
                # Pour PARTNER : créer automatiquement un DonneeEnqueteur vide
                donnee = db.session.get(Donnee, donnee_id)
                if donnee:
                    from models.client import Client
                    client = db.session.get(Client, donnee.client_id)
                    is_partner = client and client.code == 'PARTNER'
                    
                    if is_partner:
                        # Créer un DonneeEnqueteur vide pour PARTNER
                        donnee_enqueteur = DonneeEnqueteur(
                            donnee_id=donnee_id,
                            client_id=donnee.client_id
                        )
                        db.session.add(donnee_enqueteur)
                        db.session.commit()
                        logger.info(f"DonneeEnqueteur créé automatiquement pour dossier PARTNER {donnee_id}")
                    else:
                        # Pour EOS : retourner 404 (comportement normal)
                        return jsonify({
                            'success': False, 
                            'error': 'Aucune donnée enquêteur trouvée pour cet ID'
                        }), 404
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'Dossier introuvable'
                    }), 404
                
            return jsonify({
                'success': True, 
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données enquêteur: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees/non-exportees/count', methods=['GET'])
    def get_non_exportees_count():
        """Compte le nombre d'enquêtes non encore exportées (filtré par client)"""
        try:
            # MULTI-CLIENT: Récupérer le client (par défaut EOS)
            from client_utils import get_client_or_default
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404

            count = Donnee.query.filter(
                Donnee.client_id == client.id,  # Filtrer par client
                Donnee.statut_validation.notin_(['validee', 'archivee']),
                Donnee.exported == False
            ).count()
            
            return jsonify({
                "success": True,
                "count": count,
                "client_id": client.id,
                "client_code": client.code
            })
        except Exception as e:
            logger.error(f"Erreur lors du comptage: {str(e)}")
            return jsonify({"success": False, "error": str(e), "count": 0}), 500
    
    @app.route('/api/donnees-complete', methods=['GET'])
    def get_donnees_complete():
        """Récupère les données complètes avec jointure, pagination et filtres (multi-client)"""
        try:
            # MULTI-CLIENT: Récupérer le client (par défaut EOS)
            from client_utils import get_client_or_default
            
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            # Si aucun client spécifié, utiliser EOS par défaut
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404
            
            logger.info(f"Liste des données pour client: {client.code} (ID: {client.id})")
            
            # Paramètres de pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 500, type=int)
            # Limiter per_page à 1000 max pour éviter les surcharges
            per_page = min(per_page, 1000)
            
            # LOGIQUE SPÉCIFIQUE SHERLOCK
            if client.code == 'RG_SHERLOCK':
                from models import SherlockDonnee, Fichier
                
                # 1. Base Query
                query = db.session.query(SherlockDonnee).join(
                    Fichier, SherlockDonnee.fichier_id == Fichier.id
                ).filter(
                    Fichier.client_id == client.id
                )
                
                # 2. Text Search
                search = request.args.get('search')
                if search:
                    search_pattern = f"%{search}%"
                    query = query.filter(
                        db.or_(
                            SherlockDonnee.dossier_id.ilike(search_pattern),
                            SherlockDonnee.ec_nom_usage.ilike(search_pattern),
                            SherlockDonnee.ec_prenom.ilike(search_pattern)
                        )
                    )
                
                # 3. Pagination
                pagination = query.order_by(SherlockDonnee.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
                
                # 4. Construction de la réponse
                result = []
                for item in pagination.items:
                    d = item.to_dict()
                    
                    # Mapping vers le schéma standard Donnee pour le frontend
                    frontend_item = {
                        'id': item.id,
                        'numeroDossier': item.dossier_id,
                        'nom': item.ec_nom_usage,
                        'prenom': item.ec_prenom,
                        'typeDemande': item.demande or 'ENQ',
                        
                        # Mapping Résultat -> Statut/Code Resultat
                        'code_resultat': item.resultat if item.resultat else None,
                        
                        # Infos Enquêteur (Non applicable)
                        'enqueteurId': None,
                        'enqueteur_nom': None,
                        'enqueteur_prenom': None,
                        'has_response': True if item.resultat else False,
                        'can_validate': False,
                        'statut_validation': 'en_cours',
                        
                        # Dates
                        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None,
                        # Pas de date butoir réelle, on met null ou une valeur par défaut
                        'date_butoir': None,
                        
                        # Autres champs pour compatibilité
                        'elements_retrouves': None, # Pourrait être mappé depuis les colonnes AD-...
                    }
                    
                    # Fusionner avec les données brutes d'abord
                    final_item = d.copy()
                    final_item.update(frontend_item)
                    
                    # Nettoyage des données (NaN -> None, "nan" -> None)
                    import math
                    cleaned_item = {}
                    for k, v in final_item.items():
                        if isinstance(v, float) and math.isnan(v):
                            cleaned_item[k] = None
                        elif isinstance(v, str) and v.lower() == 'nan':
                            cleaned_item[k] = None
                        else:
                            cleaned_item[k] = v
                    
                    result.append(cleaned_item)
                
                return jsonify({
                    "success": True,
                    "data": result,
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "client_code": client.code
                })

            # LOGIQUE STANDARD (DONNEE)
            # Construire la requête de base AVEC FILTRAGE CLIENT
            query = db.session.query(Donnee).options(
                db.joinedload(Donnee.donnee_enqueteur)
            ).filter(
                Donnee.client_id == client.id,  # MULTI-CLIENT: Filtre par client
                Donnee.statut_validation.notin_(['validee', 'archivee'])
            )
            
            # === FILTRES CÔTÉ SERVEUR ===
            
            # Filtre par statut de validation
            statut = request.args.get('statut_validation')
            if statut:
                query = query.filter(Donnee.statut_validation == statut)
            
            # Filtre par type de demande
            type_demande = request.args.get('typeDemande')
            if type_demande:
                query = query.filter(Donnee.typeDemande == type_demande)
            
            # Filtre par enquêteur assigné
            enqueteur_id = request.args.get('enqueteurId')
            if enqueteur_id:
                if enqueteur_id == 'unassigned':
                    query = query.filter(Donnee.enqueteurId.is_(None))
                else:
                    query = query.filter(Donnee.enqueteurId == int(enqueteur_id))
            
            # Filtre par code résultat
            code_resultat = request.args.get('code_resultat')
            if code_resultat:
                query = query.join(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id, isouter=True)\
                             .filter(DonneeEnqueteur.code_resultat == code_resultat)
            
            # Filtre par date butoir (range)
            date_butoir_start = request.args.get('date_butoir_start')
            date_butoir_end = request.args.get('date_butoir_end')
            if date_butoir_start:
                from datetime import datetime
                start_date = datetime.strptime(date_butoir_start, '%Y-%m-%d').date()
                query = query.filter(Donnee.date_butoir >= start_date)
            if date_butoir_end:
                from datetime import datetime
                end_date = datetime.strptime(date_butoir_end, '%Y-%m-%d').date()
                query = query.filter(Donnee.date_butoir <= end_date)
            
            # Filtre par date de réception (range)
            date_reception_start = request.args.get('date_reception_start')
            date_reception_end = request.args.get('date_reception_end')
            if date_reception_start:
                from datetime import datetime
                start_date = datetime.strptime(date_reception_start, '%Y-%m-%d')
                query = query.filter(Donnee.created_at >= start_date)
            if date_reception_end:
                from datetime import datetime
                end_date = datetime.strptime(date_reception_end, '%Y-%m-%d')
                query = query.filter(Donnee.created_at <= end_date)
            
            # Filtre par recherche textuelle (numeroDossier, nom, prenom, referenceDossier)
            search = request.args.get('search')
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Donnee.numeroDossier.ilike(search_pattern),
                        Donnee.nom.ilike(search_pattern),
                        Donnee.prenom.ilike(search_pattern),
                        Donnee.referenceDossier.ilike(search_pattern)
                    )
                )
            
            # Filtre enquêtes exportées/non exportées
            exported = request.args.get('exported')
            if exported:
                query = query.filter(Donnee.exported == (exported.lower() == 'true'))
            
            # Tri (par défaut : date de création décroissante)
            sort_by = request.args.get('sort_by', 'created_at')
            sort_order = request.args.get('sort_order', 'desc')
            
            if hasattr(Donnee, sort_by):
                sort_column = getattr(Donnee, sort_by)
                if sort_order == 'asc':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                # Par défaut
                query = query.order_by(Donnee.created_at.desc())
            
            # === PAGINATION ===
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            donnees = pagination.items
            
            # Construire les résultats avec données enrichies
            result = []
            for donnee in donnees:
                donnee_dict = donnee.to_dict()
                
                # PRÉSERVER les adresses originales du fichier importé
                adresses_originales = {
                    'adresse1_origine': donnee_dict.get('adresse1'),
                    'adresse2_origine': donnee_dict.get('adresse2'),
                    'adresse3_origine': donnee_dict.get('adresse3'),
                    'adresse4_origine': donnee_dict.get('adresse4'),
                    'ville_origine': donnee_dict.get('ville'),
                    'codePostal_origine': donnee_dict.get('codePostal'),
                    'paysResidence_origine': donnee_dict.get('paysResidence'),
                    'telephonePersonnel_origine': donnee_dict.get('telephonePersonnel'),
                    'telephoneEmployeur_origine': donnee_dict.get('telephoneEmployeur'),
                    'nomEmployeur_origine': donnee_dict.get('nomEmployeur'),
                    'banqueDomiciliation_origine': donnee_dict.get('banqueDomiciliation'),
                    'libelleGuichet_origine': donnee_dict.get('libelleGuichet'),
                    'titulaireCompte_origine': donnee_dict.get('titulaireCompte'),
                    'codeBanque_origine': donnee_dict.get('codeBanque'),
                    'codeGuichet_origine': donnee_dict.get('codeGuichet'),
                    'numeroCompte_origine': donnee_dict.get('numeroCompte'),
                    'ribCompte_origine': donnee_dict.get('ribCompte'),
                }
                
                # Indicateur si l'enquête a une réponse d'enquêteur
                has_response = False
                if donnee.donnee_enqueteur:
                    for k, v in donnee.donnee_enqueteur.to_dict().items():
                        if k not in ['id', 'donnee_id']:
                            donnee_dict[k] = v
                    # Vérifier si l'enquête a une réponse complète
                    has_response = (
                        donnee.donnee_enqueteur.code_resultat is not None and
                        donnee.donnee_enqueteur.code_resultat != ''
                    )
                
                # Ajouter les données originales (ne seront pas écrasées)
                donnee_dict.update(adresses_originales)
                
                # Ajouter les indicateurs pour la validation
                donnee_dict['has_response'] = has_response
                # Les enquêtes avec statut 'confirmee' peuvent être validées par l'admin
                donnee_dict['can_validate'] = has_response and donnee.statut_validation == 'confirmee'
                
                # Ajouter les informations de l'enquêteur assigné
                if donnee.enqueteurId:
                    enqueteur = db.session.get(Enqueteur, donnee.enqueteurId)
                    if enqueteur:
                        donnee_dict['enqueteur_nom'] = enqueteur.nom
                        donnee_dict['enqueteur_prenom'] = enqueteur.prenom
                    else:
                        donnee_dict['enqueteur_nom'] = None
                        donnee_dict['enqueteur_prenom'] = None
                else:
                    donnee_dict['enqueteur_nom'] = None
                    donnee_dict['enqueteur_prenom'] = None
                
                result.append(donnee_dict)
            
            # Réponse paginée
            return jsonify({
                "success": True,
                "data": result,
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            })
            
        except Exception as e:
            logger.error(f"Erreur dans get_donnees_complete: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['POST'])
    def update_donnee_enqueteur(donnee_id):
        """Met à jour les données enquêteur"""
        try:
            data = request.get_json()
            logger.info(f"Données reçues pour mise à jour: {data}")
            
            # Récupérer la Donnee parent pour obtenir le client_id
            donnee_parent = Donnee.query.get(donnee_id)
            if not donnee_parent:
                return jsonify({'success': False, 'error': 'Enquête introuvable'}), 404
            
            # Vérifier le type de client pour assouplir les validations
            from models.client import Client
            client = db.session.get(Client, donnee_parent.client_id)
            is_client_x = client and client.code != 'EOS'
            
            # Récupérer ou créer l'entrée
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            if not donnee_enqueteur:
                donnee_enqueteur = DonneeEnqueteur(
                    donnee_id=donnee_id,
                    client_id=donnee_parent.client_id  # AJOUT du client_id
                )
                db.session.add(donnee_enqueteur)
                # Flush pour obtenir l'ID avant de continuer
                db.session.flush()
            
            # Mettre à jour les champs
            for field in ['code_resultat', 'elements_retrouves', 'flag_etat_civil_errone',
                         'adresse1', 'adresse2', 'adresse3', 'adresse4', 'code_postal', 'ville',
                         'pays_residence', 'telephone_personnel', 'telephone_chez_employeur',
                         'nom_employeur', 'telephone_employeur', 'telecopie_employeur',
                         'adresse1_employeur', 'adresse2_employeur', 'adresse3_employeur',
                         'adresse4_employeur', 'code_postal_employeur', 'ville_employeur',
                         'pays_employeur', 'banque_domiciliation', 'libelle_guichet',
                         'titulaire_compte', 'code_banque', 'code_guichet',
                         'numero_acte_deces', 'code_insee_deces', 'code_postal_deces',
                         'localite_deces', 'commentaires_revenus', 'periode_versement_salaire',
                         'frequence_versement_salaire', 'nature_revenu1', 'periode_versement_revenu1',
                         'frequence_versement_revenu1', 'nature_revenu2', 'periode_versement_revenu2',
                         'frequence_versement_revenu2', 'nature_revenu3', 'periode_versement_revenu3',
                         'frequence_versement_revenu3', 'memo1', 'memo2', 'memo3', 'memo4', 'memo5',
                         'notes_personnelles']:
                if field in data:
                    setattr(donnee_enqueteur, field, data.get(field))
            
            # Champs de type date
            if 'date_deces' in data and data.get('date_deces'):
                donnee_enqueteur.date_deces = datetime.strptime(data.get('date_deces'), '%Y-%m-%d').date()
            
            # Champs de type montant
            for field in ['montant_salaire', 'montant_revenu1', 'montant_revenu2', 'montant_revenu3']:
                if field in data:
                    montant = data.get(field)
                    setattr(donnee_enqueteur, field, float(montant) if montant else None)
            
            # Mise à jour de la date de modification
            donnee_enqueteur.updated_at = datetime.now()
            
            # Pour PARTNER (CLIENT_X), mettre à jour dateNaissance_maj et lieuNaissance_maj dans Donnee
            if is_client_x:
                if 'dateNaissance_maj' in data:
                    if data.get('dateNaissance_maj'):
                        try:
                            donnee_parent.dateNaissance_maj = datetime.strptime(data.get('dateNaissance_maj'), '%Y-%m-%d').date()
                            logger.info(f"Date de naissance (MAJ) mise à jour pour enquête {donnee_id}: {donnee_parent.dateNaissance_maj}")
                        except ValueError as e:
                            logger.error(f"Format de date invalide: {data.get('dateNaissance_maj')} - {e}")
                            raise ValueError(f"Format de date invalide: {data.get('dateNaissance_maj')}. Attendu: YYYY-MM-DD")
                    else:
                        donnee_parent.dateNaissance_maj = None
                
                if 'lieuNaissance_maj' in data:
                    donnee_parent.lieuNaissance_maj = data.get('lieuNaissance_maj')
                    logger.info(f"Lieu de naissance (MAJ) mis à jour pour enquête {donnee_id}: {donnee_parent.lieuNaissance_maj}")
                
                donnee_parent.updated_at = datetime.now()
            
            # Si le code résultat est positif, préparer la facturation
            # Pour CLIENT_X, ne pas exiger de validation stricte
            if donnee_enqueteur.code_resultat in ['P', 'H']:
                try:
                    from services.tarification_service import TarificationService
                    from models.tarifs import EnqueteFacturation
                    
                    # Pour CLIENT_X, utiliser le tarif_lettre de la donnée parent si disponible
                    if is_client_x and donnee_parent.tarif_lettre and not donnee_enqueteur.elements_retrouves:
                        donnee_enqueteur.elements_retrouves = donnee_parent.tarif_lettre
                    
                    existing = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
                    if existing:
                        existing.paye = False
                        if not existing.resultat_enqueteur_montant or existing.resultat_enqueteur_montant <= 0:
                            existing.resultat_enqueteur_montant = 10.0
                        logger.info(f"Facturation existante mise à jour: {existing.id}")
                    else:
                        facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
                        if facturation:
                            if not facturation.resultat_enqueteur_montant or facturation.resultat_enqueteur_montant <= 0:
                                facturation.resultat_enqueteur_montant = 10.0
                            logger.info(f"Facturation créée: {facturation.id}")
                except Exception as e:
                    logger.error(f"Erreur lors du calcul de la facturation: {str(e)}")
                    # Pour CLIENT_X, ne pas bloquer si la facturation échoue
                    if not is_client_x:
                        raise
                
                # Mettre à jour le statut_validation automatiquement pour PARTNER
                # Quand un code résultat positif est saisi, l'enquête passe directement à 'validee'
                if is_client_x and donnee_parent.statut_validation == 'en_attente':
                    donnee_parent.statut_validation = 'validee'
                    donnee_parent.exported = False  # Marquer comme non exportée pour qu'elle apparaisse dans Export
                    logger.info(f"Statut mis à jour automatiquement: enquête {donnee_id} -> validee")
            
            # Si le code résultat est négatif (N, Z, I, Y), marquer comme validée aussi
            elif donnee_enqueteur.code_resultat in ['N', 'Z', 'I', 'Y']:
                if is_client_x and donnee_parent.statut_validation == 'en_attente':
                    donnee_parent.statut_validation = 'validee'
                    donnee_parent.exported = False
                    logger.info(f"Statut mis à jour automatiquement: enquête {donnee_id} (négative) -> validee")
            
            # UN SEUL COMMIT à la fin pour éviter les conflits
            db.session.commit()
            
            # Pour PARTNER : Recalculer automatiquement les demandes après la sauvegarde
            if is_client_x:
                try:
                    from services.partner_request_calculator import PartnerRequestCalculator
                    result = PartnerRequestCalculator.recalculate_all_requests(donnee_id)
                    logger.info(f"Recalcul automatique PARTNER pour donnee_id={donnee_id}: {result['pos']} POS, {result['neg']} NEG")
                except Exception as e:
                    logger.error(f"Erreur lors du recalcul automatique PARTNER: {str(e)}")
                    # Ne pas bloquer l'enregistrement si le recalcul échoue
                                    
            return jsonify({
                'success': True, 
                'message': 'Données mises à jour avec succès',
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour: {str(e)}")
            
            # Message plus clair si l'enquête a été supprimée
            error_msg = str(e)
            if "has been deleted" in error_msg or "is otherwise not present" in error_msg:
                error_msg = "Cette enquête a été supprimée. Veuillez rafraîchir la page (F5)."
            
            return jsonify({'success': False, 'error': error_msg}), 400

    @app.route('/api/assign-enquete', methods=['POST'])
    def assign_enquete():
        """Assigne une enquête à un enquêteur"""
        try:
            data = request.json
            logger.info(f"Données reçues pour l'assignation: {data}")
            
            enquete_id = data.get('enqueteId')
            enqueteur_id = data.get('enqueteurId')
            
            if not enquete_id:
                return jsonify({'success': False, 'error': 'Missing enqueteId'}), 400
                
            # Chercher par ID ou numeroDossier
            enquete = None
            try:
                enquete_id_int = int(enquete_id)
                enquete = Donnee.query.filter_by(id=enquete_id_int).first()
            except ValueError:
                pass
                
            if not enquete:
                enquete = Donnee.query.filter_by(numeroDossier=enquete_id).first()
                
            if not enquete:
                return jsonify({'success': False, 'error': 'Enquête not found'}), 404
                
            if enqueteur_id:
                enqueteur = db.session.get(Enqueteur, enqueteur_id)
                if not enqueteur:
                    return jsonify({'success': False, 'error': 'Enquêteur not found'}), 404
            
            enquete.enqueteurId = enqueteur_id if enqueteur_id != '' else None
            db.session.commit()
            
            # Recalculer la facturation si nécessaire
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=enquete.id).first()
            if donnee_enqueteur and donnee_enqueteur.code_resultat in ['P', 'H']:
                try:
                    from services.tarification_service import TarificationService
                    TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
                except Exception as e:
                    logger.error(f"Erreur lors du recalcul de la facturation: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Assignment successful',
                'data': enquete.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"Erreur lors de l'assignation: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/enqueteurs-stats', methods=['GET'])
    def get_enqueteurs_stats():
        """Obtenir des statistiques sur les enquêteurs"""
        try:
            from sqlalchemy import func
            
            enqueteurs = Enqueteur.query.all()
            stats = []
            
            for enqueteur in enqueteurs:
                total_enquetes = Donnee.query.filter_by(enqueteurId=enqueteur.id).count()
                
                status_counts = (db.session.query(
                    DonneeEnqueteur.code_resultat, 
                    func.count(DonneeEnqueteur.id)
                )
                .join(Donnee, Donnee.id == DonneeEnqueteur.donnee_id)
                .filter(Donnee.enqueteurId == enqueteur.id)
                .group_by(DonneeEnqueteur.code_resultat)
                .all())
                
                status_dict = {'P': 0, 'N': 0, 'H': 0, 'Z': 0, 'I': 0, 'Y': 0, 'pending': 0}
                
                for status, count in status_counts:
                    if status:
                        status_dict[status] = count
                
                status_dict['pending'] = total_enquetes - sum(status_dict.values())
                
                stats.append({
                    'id': enqueteur.id,
                    'nom': enqueteur.nom,
                    'prenom': enqueteur.prenom,
                    'email': enqueteur.email,
                    'total_enquetes': total_enquetes,
                    'statuts': status_dict
                })
            
            return jsonify({'success': True, 'data': stats})
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/parse', methods=['POST'])
    def parse_file():
        """Parse et importe un fichier de données (multi-client)"""
        logger.info("Début du traitement de la requête d'import")
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # MULTI-CLIENT: Récupérer le client (par défaut EOS)
            from client_utils import get_client_or_default, get_import_profile_for_client
            
            client_id = request.form.get('client_id', type=int)
            client_code = request.form.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id, client_code=client_code)
            if not client:
                return jsonify({"error": "Client introuvable"}), 404
            
            logger.info(f"Import pour le client: {client.code} (ID: {client.id})")

            # Vérifier si le fichier existe déjà pour ce client
            existing_file = Fichier.query.filter_by(
                nom=file.filename,
                client_id=client.id
            ).first()
            
            if existing_file:
                return jsonify({
                    "status": "file_exists",
                    "message": "Ce fichier existe déjà pour ce client. Voulez-vous le remplacer ?",
                    "existing_file_info": {
                        "nom": existing_file.nom,
                        "date_upload": existing_file.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                        "nombre_donnees": Donnee.query.filter_by(
                            fichier_id=existing_file.id,
                            client_id=client.id
                        ).count()
                    }
                }), 409

            # Récupérer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reçue: {date_butoir}")
                except ValueError:
                    logger.warning(f"Format de date butoir invalide: {date_butoir_str}")

            # Lire le contenu du fichier
            content = file.read()
            if not content:
                return jsonify({"error": "Fichier vide"}), 400

            # Déterminer le type de fichier (base)
            file_extension = file.filename.lower().split('.')[-1]
            base_file_type = 'EXCEL' if file_extension in ['xlsx', 'xls'] else 'TXT_FIXED'
            
            # Récupérer le profil d'import pour ce client
            # MULTI-CLIENT: On cherche d'abord s'il y a un profil spécifique comme EXCEL_VERTICAL
            import_profile = None
            if base_file_type == 'EXCEL':
                import_profile = get_import_profile_for_client(client.id, 'EXCEL_VERTICAL')
            
            # Sinon on prend le profil standard
            if not import_profile:
                import_profile = get_import_profile_for_client(client.id, base_file_type)

            if not import_profile:
                logger.error(f"Aucun profil d'import trouvé pour le client {client.code} (Extension: {file_extension})")
                return jsonify({
                    "error": f"Aucun profil d'import configuré pour ce type de fichier ({file_extension})"
                }), 400

            try:
                # Créer le fichier en base
                nouveau_fichier = Fichier(
                    nom=file.filename,
                    client_id=client.id
                )
                db.session.add(nouveau_fichier)
                db.session.commit()
                logger.info(f"Fichier créé avec ID: {nouveau_fichier.id} pour client {client.code}")

                # Utiliser le moteur d'import générique
                from import_engine import ImportEngine
                
                engine = ImportEngine(import_profile, filename=file.filename)
                parsed_records = engine.parse_content(content)
                
                if not parsed_records:
                    db.session.delete(nouveau_fichier)
                    db.session.commit()
                    return jsonify({"error": "Aucun enregistrement valide trouvé"}), 400
                
                # Créer les instances Donnee
                created_count = 0
                for record in parsed_records:
                    try:
                        nouvelle_donnee = engine.create_donnee_from_record(
                            record,
                            fichier_id=nouveau_fichier.id,
                            client_id=client.id,
                            date_butoir=date_butoir
                        )
                        db.session.add(nouvelle_donnee)
                        db.session.flush()
                        
                        # Créer DonneeEnqueteur si contestation
                        if record.get('typeDemande') == 'CON':
                            donnee_enqueteur = DonneeEnqueteur.query.filter_by(
                                donnee_id=nouvelle_donnee.id
                            ).first()

                            if not donnee_enqueteur:
                                donnee_enqueteur = DonneeEnqueteur(
                                    donnee_id=nouvelle_donnee.id,
                                    client_id=client.id
                                )

                                # Récupérer les données de l'enquêteur original (nom, résultats, mémo)
                                if nouvelle_donnee.enquete_originale_id:
                                    original_de = DonneeEnqueteur.query.filter_by(
                                        donnee_id=nouvelle_donnee.enquete_originale_id
                                    ).first()
                                    if original_de:
                                        # Copier le mémo personnel et les notes
                                        donnee_enqueteur.notes_personnelles = original_de.notes_personnelles
                                        donnee_enqueteur.memo1 = original_de.memo1
                                        donnee_enqueteur.memo2 = original_de.memo2
                                        donnee_enqueteur.memo3 = original_de.memo3
                                        donnee_enqueteur.memo4 = original_de.memo4
                                        donnee_enqueteur.memo5 = original_de.memo5
                                        logger.info(f"Contestation {nouvelle_donnee.numeroDossier}: mémos et notes copiés depuis l'enquête originale {nouvelle_donnee.enquete_originale_id}")

                                db.session.add(donnee_enqueteur)
                        
                        # Créer PartnerCaseRequest si PARTNER et demandes détectées
                        if hasattr(nouvelle_donnee, '_pending_requests') and nouvelle_donnee._pending_requests:
                            from models.partner_models import PartnerCaseRequest
                            for request_code in nouvelle_donnee._pending_requests:
                                case_request = PartnerCaseRequest(
                                    donnee_id=nouvelle_donnee.id,
                                    request_code=request_code,
                                    requested=True,
                                    found=False,
                                    status='NEG'  # Par défaut NEG, sera recalculé lors de l'update
                                )
                                db.session.add(case_request)
                            logger.info(f"✓ {len(nouvelle_donnee._pending_requests)} demandes créées pour {nouvelle_donnee.numeroDossier}")
                        
                        created_count += 1
                        
                    except Exception as e:
                        logger.error(f"Erreur création donnée: {e}")
                        continue
                
                db.session.commit()
                logger.info(f"{created_count} enregistrements créés avec succès")
                
                return jsonify({
                    "message": "Fichier traité avec succès",
                    "file_id": nouveau_fichier.id,
                    "client_code": client.code,
                    "records_processed": created_count
                })

            except Exception as e:
                if 'nouveau_fichier' in locals():
                    try:
                        db.session.delete(nouveau_fichier)
                        db.session.commit()
                    except:
                        db.session.rollback()
                
                logger.error(f"Erreur lors du traitement du contenu: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 400

        except Exception as e:
            logger.error(f"Erreur lors du traitement: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/replace-file', methods=['POST'])
    def replace_file():
        """Remplace un fichier existant (multi-client)"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # MULTI-CLIENT: Récupérer le client
            from client_utils import get_client_or_default
            
            client_id = request.form.get('client_id', type=int)
            client_code = request.form.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id, client_code=client_code)
            if not client:
                return jsonify({"error": "Client introuvable"}), 404

            # Récupérer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reçue pour remplacement: {date_butoir}")
                except ValueError:
                    logger.warning(f"Format de date butoir invalide: {date_butoir_str}")

            existing_file = Fichier.query.filter_by(
                nom=file.filename,
                client_id=client.id
            ).first()
            
            if existing_file:
                Donnee.query.filter_by(
                    fichier_id=existing_file.id,
                    client_id=client.id
                ).delete()
                db.session.delete(existing_file)
                db.session.commit()

            # Lire le contenu
            content = file.read()
            if not content:
                return jsonify({"error": "Fichier vide"}), 400

            # Déterminer le type de fichier (base)
            file_extension = file.filename.lower().split('.')[-1]
            base_file_type = 'EXCEL' if file_extension in ['xlsx', 'xls'] else 'TXT_FIXED'
            
            # Récupérer le profil d'import
            from client_utils import get_import_profile_for_client
            import_profile = None
            if base_file_type == 'EXCEL':
                import_profile = get_import_profile_for_client(client.id, 'EXCEL_VERTICAL')
                
            if not import_profile:
                import_profile = get_import_profile_for_client(client.id, base_file_type)
                
            if not import_profile:
                return jsonify({
                    "error": f"Aucun profil d'import configuré pour ce type de fichier ({file_extension})"
                }), 400

            # Créer le nouveau fichier
            nouveau_fichier = Fichier(
                nom=file.filename,
                client_id=client.id
            )
            db.session.add(nouveau_fichier)
            db.session.commit()
            
            # Utiliser le moteur d'import
            from import_engine import ImportEngine
            
            engine = ImportEngine(import_profile)
            parsed_records = engine.parse_content(content)
            
            if not parsed_records:
                db.session.delete(nouveau_fichier)
                db.session.commit()
                return jsonify({"error": "Aucun enregistrement valide trouvé"}), 400
            
            # Créer les instances Donnee
            created_count = 0
            for record in parsed_records:
                try:
                    nouvelle_donnee = engine.create_donnee_from_record(
                        record,
                        fichier_id=nouveau_fichier.id,
                        client_id=client.id,
                        date_butoir=date_butoir
                    )
                    db.session.add(nouvelle_donnee)
                    db.session.flush()
                    
                    # Créer DonneeEnqueteur si contestation
                    if record.get('typeDemande') == 'CON':
                        donnee_enqueteur = DonneeEnqueteur.query.filter_by(
                            donnee_id=nouvelle_donnee.id
                        ).first()

                        if not donnee_enqueteur:
                            donnee_enqueteur = DonneeEnqueteur(
                                donnee_id=nouvelle_donnee.id,
                                client_id=client.id
                            )

                            # Récupérer les données de l'enquêteur original (nom, résultats, mémo)
                            if nouvelle_donnee.enquete_originale_id:
                                original_de = DonneeEnqueteur.query.filter_by(
                                    donnee_id=nouvelle_donnee.enquete_originale_id
                                ).first()
                                if original_de:
                                    donnee_enqueteur.notes_personnelles = original_de.notes_personnelles
                                    donnee_enqueteur.memo1 = original_de.memo1
                                    donnee_enqueteur.memo2 = original_de.memo2
                                    donnee_enqueteur.memo3 = original_de.memo3
                                    donnee_enqueteur.memo4 = original_de.memo4
                                    donnee_enqueteur.memo5 = original_de.memo5
                                    logger.info(f"Contestation {nouvelle_donnee.numeroDossier}: mémos copiés depuis originale {nouvelle_donnee.enquete_originale_id}")

                            db.session.add(donnee_enqueteur)

                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur création donnée: {e}")
                    continue
            
            db.session.commit()

            return jsonify({
                "message": "Fichier remplacé avec succès",
                "file_id": nouveau_fichier.id,
                "client_code": client.code,
                "records_processed": created_count
            })

        except Exception as e:
            logger.error(f"Erreur lors du remplacement: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/files/<int:file_id>', methods=['DELETE'])
    def delete_file(file_id):
        """Supprime un fichier et ses données associées"""
        try:
            from models.tarifs import EnqueteFacturation
            
            fichier = Fichier.query.get_or_404(file_id)
            
            # Récupérer les IDs des donnees à supprimer
            donnee_ids = [d.id for d in Donnee.query.filter_by(fichier_id=file_id).all()]
            
            if donnee_ids:
                # 1. Supprimer d'abord les facturations liées
                EnqueteFacturation.query.filter(
                    EnqueteFacturation.donnee_id.in_(donnee_ids)
                ).delete(synchronize_session=False)
                
                # 2. Supprimer les données enquêteur liées
                DonneeEnqueteur.query.filter(
                    DonneeEnqueteur.donnee_id.in_(donnee_ids)
                ).delete(synchronize_session=False)
                
                # 3. Supprimer les données
                Donnee.query.filter_by(fichier_id=file_id).delete()
            
            # 4. Supprimer le fichier
            db.session.delete(fichier)
            db.session.commit()
            
            logger.info(f"Fichier {file_id} supprimé avec {len(donnee_ids)} enquêtes associées")
            return jsonify({"message": "Fichier supprimé avec succès"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/contestations/<int:enquete_id>', methods=['GET'])
    def get_contestation_details(enquete_id):
        """Récupère les détails d'une contestation"""
        try:
            donnee = Donnee.query.get_or_404(enquete_id)
            
            if donnee.typeDemande != 'CON':
                return jsonify({
                    'success': False,
                    'error': 'Cette enquête n\'est pas une contestation'
                }), 400
                
            enquete_originale = None
            if donnee.enquete_originale_id:
                enquete_originale = db.session.get(Donnee, donnee.enquete_originale_id)
                
            return jsonify({
                'success': True,
                'data': {
                    'contestation': donnee.to_dict(),
                    'enquete_originale': enquete_originale.to_dict() if enquete_originale else None,
                    'enqueteur_id': enquete_originale.enqueteurId if enquete_originale else None,
                    'motif_contestation': donnee.motifDeContestation
                }
            })
        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/fix-facturations', methods=['POST'])
    def fix_facturations():
        """Corrige les associations enquêteur-facturation"""
        try:
            from models.tarifs import EnqueteFacturation
            
            facturations = db.session.query(
                EnqueteFacturation, Donnee
            ).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                Donnee.enqueteurId.is_(None),
                EnqueteFacturation.resultat_enqueteur_montant > 0
            ).all()
            
            fixed_count = 0
            for facturation, donnee in facturations:
                donnee.enqueteurId = 1  # Assigner à l'enquêteur par défaut
                fixed_count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Corrections effectuées: {fixed_count} facturations',
                'count': fixed_count
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===========================
    # Routes pour les tarifs clients (PARTNER)
    # ===========================
    @app.route('/api/tarifs-client', methods=['GET'])
    def get_tarifs_client():
        """Récupère les tarifs pour un client spécifique"""
        try:
            from models.tarifs import TarifClient
            client_id = request.args.get('client_id', type=int)
            
            if not client_id:
                return jsonify({"success": False, "error": "client_id requis"}), 400
            
            tarifs = TarifClient.query.filter_by(
                client_id=client_id,
                actif=True
            ).order_by(TarifClient.code_lettre).all()
            
            return jsonify({
                "success": True,
                "tarifs": [tarif.to_dict() for tarif in tarifs]
            })
        except Exception as e:
            logger.error(f"Erreur get_tarifs_client: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/tarifs-client', methods=['POST'])
    def create_tarif_client():
        """Crée un nouveau tarif client"""
        try:
            from models.tarifs import TarifClient
            data = request.json
            
            # Vérifier si le tarif existe déjà
            existing = TarifClient.query.filter_by(
                client_id=data['client_id'],
                code_lettre=data['code_lettre'],
                actif=True
            ).first()
            
            if existing:
                return jsonify({
                    "success": False,
                    "error": f"Le tarif {data['code_lettre']} existe déjà pour ce client"
                }), 400
            
            tarif = TarifClient(
                client_id=data['client_id'],
                code_lettre=data['code_lettre'],
                description=data.get('description', ''),
                montant=data['montant'],
                date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date() if 'date_debut' in data else datetime.now().date(),
                actif=True
            )
            
            db.session.add(tarif)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "tarif": tarif.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur create_tarif_client: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/tarifs-client/<int:tarif_id>', methods=['PUT'])
    def update_tarif_client(tarif_id):
        """Met à jour un tarif client"""
        try:
            from models.tarifs import TarifClient
            tarif = TarifClient.query.get_or_404(tarif_id)
            data = request.json
            
            if 'montant' in data:
                tarif.montant = data['montant']
            if 'description' in data:
                tarif.description = data['description']
            if 'actif' in data:
                tarif.actif = data['actif']
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "tarif": tarif.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur update_tarif_client: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/tarifs-client/<int:tarif_id>', methods=['DELETE'])
    def delete_tarif_client(tarif_id):
        """Désactive un tarif client (soft delete)"""
        try:
            from models.tarifs import TarifClient
            tarif = TarifClient.query.get_or_404(tarif_id)
            
            tarif.actif = False
            tarif.date_fin = datetime.now().date()
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Tarif désactivé avec succès"
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur delete_tarif_client: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===========================
    # Routes pour les options de confirmation personnalisées
    # ===========================
    @app.route('/api/confirmation-options/<int:client_id>', methods=['GET'])
    def get_confirmation_options(client_id):
        """Récupère les options de confirmation pour un client"""
        try:
            from models.confirmation_options import ConfirmationOption
            
            # Options prédéfinies de base
            options_base = [
                'Confirmé par la mairie',
                'En proximité',
                'Confirmé par téléphone',
                'Confirmé par voisinage',
                'Confirmé par famille',
                "Confirmé par l'employeur",
                'Confirmé par courrier',
                'Confirmé sur place'
            ]
            
            # Options personnalisées du client (la table peut ne pas exister)
            options_custom_list = []
            try:
                options_custom = ConfirmationOption.query.filter_by(
                    client_id=client_id
                ).order_by(ConfirmationOption.usage_count.desc()).all()
                options_custom_list = [opt.option_text for opt in options_custom]
            except Exception:
                pass  # Table confirmation_options supprimée par migration, on continue avec les options de base

            return jsonify({
                "success": True,
                "options_base": options_base,
                "options_custom": options_custom_list,
                "all_options": options_base + options_custom_list
            })
        except Exception as e:
            logger.error(f"Erreur get_confirmation_options: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/confirmation-options', methods=['POST'])
    def save_confirmation_option():
        """Sauvegarde une nouvelle option de confirmation"""
        try:
            from models.confirmation_options import ConfirmationOption
            data = request.json
            
            client_id = data.get('client_id')
            option_text = data.get('option_text', '').strip()
            
            if not client_id or not option_text:
                return jsonify({
                    "success": False,
                    "error": "client_id et option_text requis"
                }), 400
            
            # Vérifier si l'option existe déjà
            existing = ConfirmationOption.query.filter_by(
                client_id=client_id,
                option_text=option_text
            ).first()
            
            if existing:
                # Incrémenter le compteur d'utilisation
                existing.usage_count += 1
                existing.updated_at = datetime.now()
                db.session.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Option existante, compteur incrémenté",
                    "option": existing.to_dict()
                })
            else:
                # Créer une nouvelle option
                new_option = ConfirmationOption(
                    client_id=client_id,
                    option_text=option_text,
                    usage_count=1
                )
                db.session.add(new_option)
                db.session.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Nouvelle option ajoutée",
                    "option": new_option.to_dict()
                })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur save_confirmation_option: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    logger.info("Routes legacy enregistrées")




    # ===========================
    # REMPLACER la route existante dans app.py par celle-ci:
    # ===========================

    @app.route('/api/export/sherlock', methods=['POST'])
    def export_sherlock():
        """Exporte les données Sherlock au format XLS vertical avec formatage"""
        try:
            from models import SherlockDonnee, Fichier
            from flask import send_file
            from datetime import datetime
            import xlwt
            import io
            import math
            
            data = request.json or {}
            client_id = data.get('client_id')
            
            # Construire la requête
            query = db.session.query(SherlockDonnee).join(
                Fichier, SherlockDonnee.fichier_id == Fichier.id
            )
            
            if client_id:
                query = query.filter(Fichier.client_id == client_id)
            
            # Récupérer les données triées par ID
            items = query.order_by(SherlockDonnee.id.asc()).all()
            
            if not items:
                return jsonify({"success": False, "error": "Aucune donnée à exporter"}), 404
            
            # Mapping des champs - 65 champs (sans les tarifs)
            FIELDS_MAPPING = [
                #('DossierId', 'dossier_id', ''),
                ('RéférenceInterne', 'reference_interne', ''),
                ('EC-Nom Usage', 'ec_nom_usage', ''),
                ('EC-Prénom', 'ec_prenom', ''),
                ('EC-Nom Naissance', 'ec_nom_naissance', ''),
                ('EC-Civilité', 'ec_civilite', ''),
                ('Demande', 'demande', ''),
                ('EC-Date Naissance', 'ec_date_naissance', ''),
                ('EC-Localité Naissance', 'ec_localite_naissance', ''),
                ('Naissance CP', 'naissance_cp', ''),
                ('Client-Commentaire', 'client_commentaire', ''),
                #('EC-Prénom2', 'ec_prenom2', ''),
                #('EC-Prénom3', 'ec_prenom3', ''),
                #('EC-Prénom4', 'ec_prenom4', ''),
                #('Naissance INSEE', 'naissance_insee', ''),
                #('EC-Pays Naissance', 'ec_pays_naissance', ''),
                ('AD-L1', 'ad_l1', ''),
                ('AD-L2', 'ad_l2', ''),
                ('AD-L3', 'ad_l3', ''),
                ('AD-L4 Numéro', 'ad_l4_numero', ''),
                ('AD-L4 Type', 'ad_l4_type', ''),
                ('AD-L4 Voie', 'ad_l4_voie', ''),
                ('AD-L5', 'ad_l5', ''),
                ('AD-L6 Cedex', 'ad_l6_cedex', ''),
                ('AD-L6 CP', 'ad_l6_cp', ''),
                ('AD-L6 INSEE', 'ad_l6_insee', ''),
                ('AD-L6 Localité', 'ad_l6_localite', ''),
                ('AD-L7 Pays', 'ad_l7_pays', ''),
                ('AD-Téléphone', 'ad_telephone', ''),
                ('AD-TéléphonePro', 'ad_telephone_pro', ''),
                ('AD-TéléphoneMobile', 'ad_telephone_mobile', ''),
                ('AD-Email', 'ad_email', ''),
                #('Résultat', 'resultat', ''),
                #('Montant HT', 'montant_ht', ''),
                # Champs de réponse enquêteur (Rép-)
                #('Rép-EC-Civilité', 'rep_ec_civilite', ''),
                #('Rép-EC-Prénom', 'rep_ec_prenom', ''),
                #('Rép-EC-Prénom2', 'rep_ec_prenom2', ''),
                #('Rép-EC-Prénom3', 'rep_ec_prenom3', ''),
                #('Rép-EC-Prénom4', 'rep_ec_prenom4', ''),
                #('Rép-EC-Nom Usage', 'rep_ec_nom_usage', ''),
                #('Rép-EC-Nom Naissance', 'rep_ec_nom_naissance', ''),
                #('Rép-EC-Date Naissance', 'rep_ec_date_naissance', ''),
                #('Rép-Naissance CP', 'rep_naissance_cp', ''),
                #('Rép-EC-Localité Naissance', 'rep_ec_localite_naissance', ''),
                #('Rép-Naissance INSEE', 'rep_naissance_insee', ''),
                #('Rép-EC-Pays Naissance', 'rep_ec_pays_naissance', ''),
                #('Rép-DCD-Date', 'rep_dcd_date', ''),
                #('Rép-DCD-Numéro_Acte', 'rep_dcd_numero_acte', ''),
                #('Rép-DCD-Localité', 'rep_dcd_localite', ''),
                #('Rép-DCD-CP', 'rep_dcd_cp', ''),
                #('Rép-DCD-INSEE', 'rep_dcd_insee', ''),
                #('Rép-DCD-Pays', 'rep_dcd_pays', ''),
                #('Rép-AD-L1', 'rep_ad_l1', ''),
                #('Rép-AD-L2', 'rep_ad_l2', ''),
                #('Rép-AD-L3', 'rep_ad_l3', ''),
                #('Rép-AD-L4 Numéro', 'rep_ad_l4_numero', ''),
                #('Rép-AD-L4 Type', 'rep_ad_l4_type', ''),
                #('Rép-AD-L4 Voie', 'rep_ad_l4_voie', ''),
                #('Rép-AD-L5', 'rep_ad_l5', ''),
                #('Rép-AD-L6 Cedex', 'rep_ad_l6_cedex', ''),
                #('Rép-AD-L6 CP', 'rep_ad_l6_cp', ''),
                #('Rép-AD-L6 INSEE', 'rep_ad_l6_insee', ''),
                #('Rép-AD-L6 Localité', 'rep_ad_l6_localite', ''),
                #('Rép-AD-L7 Pays', 'rep_ad_l7_pays', ''),
                #('Rép-AD-Téléphone', 'rep_ad_telephone', ''),
            ]
            
            def format_date(date_str):
                """Formate une date au format JJ/MM/AAAA"""
                if not date_str:
                    return ''
                date_str = str(date_str).strip()
                if date_str.lower() in ('nan', 'none', ''):
                    return ''
                
                # Si format AAAA-MM-JJ HH:MM:SS ou AAAA-MM-JJ
                if '-' in date_str:
                    try:
                        # Extraire juste la partie date
                        date_part = date_str.split(' ')[0]
                        parts = date_part.split('-')
                        if len(parts) == 3:
                            year, month, day = parts
                            return f"{day}/{month}/{year}"
                    except:
                        pass
                
                return date_str
            
            def remove_decimal_zero(val):
                """Enlève le .0 des nombres comme 35000.0 -> 35000"""
                if val is None or val == '':
                    return ''
                val_str = str(val).strip()
                if val_str.lower() in ('nan', 'none'):
                    return ''
                if val_str.endswith('.0'):
                    return val_str[:-2]
                return val_str
            
            def clean_value(val):
                """Nettoie une valeur pour l'export"""
                if val is None:
                    return ''
                if isinstance(val, float):
                    try:
                        if math.isnan(val):
                            return ''
                    except:
                        pass
                val_str = str(val).strip()
                if val_str.lower() in ('nan', 'none'):
                    return ''
                return val_str
            
            def get_field_value(item, attr_name, default_value):
                """Récupère la valeur d'un champ avec formatage spécial"""
                if not hasattr(item, attr_name):
                    return default_value
                
                val = getattr(item, attr_name)
                
                # Formater les dates
                if 'date_naissance' in attr_name.lower() or 'dcd_date' in attr_name.lower():
                    return format_date(val)
                
                # Enlever .0 des codes postaux et INSEE
                if any(x in attr_name.lower() for x in ['_cp', 'insee']):
                    return remove_decimal_zero(val)
                
                return clean_value(val)
            
            # Créer le Workbook
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('rg')
            
            # === STYLES ===
            # Style GRAS pour les noms de champs (colonne A)
            style_field_name = xlwt.XFStyle()
            font_bold = xlwt.Font()
            font_bold.bold = True
            font_bold.name = 'Arial'
            font_bold.height = 220  # 11 points
            style_field_name.font = font_bold
            
            # Style normal pour les valeurs (colonne B)
            style_value = xlwt.XFStyle()
            font_normal = xlwt.Font()
            font_normal.name = 'Arial'
            font_normal.height = 220  # 11 points
            style_value.font = font_normal
            
            # === LARGEURS DE COLONNES ===
            ws.col(0).width = 256 * 25  # Colonne A: 25 caractères
            ws.col(1).width = 256 * 50  # Colonne B: 50 caractères
            
            # === CONSTANTES ===
            ROWS_PER_RECORD = 75  # 65 champs + lignes de séparation
            FIELDS_COUNT = len(FIELDS_MAPPING)  # 65 champs (sans tarifs)
            ROW_HEIGHT = 300  # ~15 points
            
            # Ligne 0: En-tête vide
            ws.write(0, 0, ' ')
            ws.write(0, 1, ' ')
            ws.row(0).height_mismatch = True
            ws.row(0).height = ROW_HEIGHT
            
            # Pour chaque enregistrement
            for idx, item in enumerate(items):
                start_row = 1 + (idx * ROWS_PER_RECORD)
                
                # Écrire les 32 champs
                for field_idx, (field_name, attr_name, default_value) in enumerate(FIELDS_MAPPING):
                    row = start_row + field_idx
                    value = get_field_value(item, attr_name, default_value)
                    
                    # Nom du champ en GRAS
                    ws.write(row, 0, field_name, style_field_name)
                    # Valeur en normal
                    ws.write(row, 1, value, style_value)
                    
                    # Hauteur de ligne
                    ws.row(row).height_mismatch = True
                    ws.row(row).height = ROW_HEIGHT
                
                # Lignes vides de séparation
                for empty_idx in range(FIELDS_COUNT, ROWS_PER_RECORD - 1):
                    row = start_row + empty_idx
                    ws.write(row, 0, '')
                    ws.write(row, 1, '')
                    ws.row(row).height_mismatch = True
                    ws.row(row).height = ROW_HEIGHT
                
                # Ligne de séparation
                if idx < len(items) - 1:
                    separator_row = start_row + ROWS_PER_RECORD - 1
                    ws.write(separator_row, 0, ' ')
                    ws.write(separator_row, 1, ' ')
                    ws.row(separator_row).height_mismatch = True
                    ws.row(separator_row).height = ROW_HEIGHT
            
            # Sauvegarder
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            # Nom du fichier
            now = datetime.now()
            filename = f"rg_IDS-L_DANS_SHERLOCK__{now.strftime('%d%m%Y_%H%M%S')}_{now.strftime('%d_%m_%Y_%H_%M_%S')}.xls"
            
            logger.info(f"Export Sherlock: {len(items)} enregistrements exportés avec formatage")
            
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.ms-excel'
            )
            
        except Exception as e:
            logger.error(f"Erreur export Sherlock: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
