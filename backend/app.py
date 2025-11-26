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

# Configuration de l'encodage par défaut pour Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Configuration CORS unifiée
    CORS(app, resources={
        r"/*": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }
    })
    
    # Créer les tables de la base de données
    with app.app_context():
        # Créer le dossier instance s'il n'existe pas
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        db.create_all()
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
    from routes.vpn_download import register_vpn_download_routes
    from routes.etat_civil import register_etat_civil_routes
    from routes.tarification import register_tarification_routes
    from routes.paiement import register_paiement_routes
    from routes.enquetes import register_enquetes_routes
    from routes.validation import register_validation_routes
    from routes.donnees import donnees_bp
    
    # Enregistrer les blueprints
    register_enqueteurs_routes(app)
    register_vpn_template_routes(app)
    register_export_routes(app)
    register_vpn_download_routes(app)
    register_etat_civil_routes(app)
    register_tarification_routes(app)
    register_paiement_routes(app)
    register_enquetes_routes(app)
    register_validation_routes(app)
    
    # Enregistrer le blueprint donnees (s'il n'est pas déjà enregistré ailleurs)
    # app.register_blueprint(donnees_bp)
    
    logger.info("Blueprints enregistrés")


def register_legacy_routes(app):
    """
    Enregistre les routes legacy qui n'ont pas encore été migrées vers des blueprints
    Ces routes devraient être progressivement déplacées vers des blueprints appropriés
    """
    from flask import request, jsonify, render_template_string
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
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 800px;
                    width: 100%;
                    padding: 40px;
                }
                h1 {
                    color: #667eea;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-align: center;
                }
                .subtitle {
                    color: #666;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                }
                .status {
                    background: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }
                .status-icon {
                    font-size: 2em;
                    margin-bottom: 10px;
                }
                .endpoints {
                    margin-top: 30px;
                }
                .endpoint-group {
                    margin-bottom: 25px;
                }
                .endpoint-group h3 {
                    color: #667eea;
                    margin-bottom: 10px;
                    font-size: 1.3em;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 5px;
                }
                .endpoint {
                    background: #f8f9fa;
                    padding: 12px 15px;
                    margin: 8px 0;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }
                .method {
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 10px;
                    font-size: 0.85em;
                }
                .get { background: #28a745; color: white; }
                .post { background: #007bff; color: white; }
                .put { background: #ffc107; color: black; }
                .delete { background: #dc3545; color: white; }
                .footer {
                    margin-top: 30px;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }
                a {
                    color: #667eea;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
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
        """Récupère les statistiques globales"""
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            total_fichiers = Fichier.query.count()
            total_donnees = Donnee.query.count()
            
            derniers_fichiers = (Fichier.query
                            .order_by(Fichier.date_upload.desc())
                            .limit(10)
                            .all())
            
            fichiers_info = [{
                "id": f.id,
                "nom": f.nom,
                "date_upload": f.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                "nombre_donnees": Donnee.query.filter_by(fichier_id=f.id).count()
            } for f in derniers_fichiers]
            
            return jsonify({
                "success": True,
                "total_fichiers": total_fichiers,
                "total_donnees": total_donnees,
                "derniers_fichiers": fichiers_info
            })
            
        except Exception as e:
            logger.error(f"Erreur dans get_stats: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/donnees', methods=['GET'])
    def get_donnees():
        """Récupère la liste des données avec pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 500, type=int)
            
            pagination = Donnee.query.paginate(page=page, per_page=per_page, error_out=False)
            donnees = pagination.items
            
            return jsonify({
                "success": True,
                "data": [donnee.to_dict() for donnee in donnees],
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page
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
                original = Donnee.query.get(donnee.enquete_originale_id)
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
            logger.error(f"Erreur lors de la suppression : {str(e)}")
            return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500

    @app.route('/api/donnees', methods=['POST'])
    def add_donnee():
        """Ajoute une nouvelle donnée"""
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
                elementObligatoires=data.get('elementObligatoires', 'A'),
                fichier_id=data.get('fichier_id', 1)  # Fichier par défaut
            )
            db.session.add(nouvelle_donnee)
            db.session.commit()
            
            # Créer automatiquement une entrée dans DonneeEnqueteur
            new_donnee_enqueteur = DonneeEnqueteur(donnee_id=nouvelle_donnee.id)
            db.session.add(new_donnee_enqueteur)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Données ajoutées avec succès',
                'data': nouvelle_donnee.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['GET'])
    def get_donnee_enqueteur(donnee_id):
        """Récupère les données enquêteur pour une donnée"""
        try:
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
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees-complete', methods=['GET'])
    def get_donnees_complete():
        """Récupère les données complètes avec jointure"""
        try:
            donnees = db.session.query(Donnee).options(
                db.joinedload(Donnee.donnee_enqueteur)
            ).all()
            
            result = []
            for donnee in donnees:
                donnee_dict = donnee.to_dict()
                if donnee.donnee_enqueteur:
                    for k, v in donnee.donnee_enqueteur.to_dict().items():
                        if k not in ['id', 'donnee_id']:
                            donnee_dict[k] = v
                
                # Ajouter les informations de l'enquêteur assigné
                if donnee.enqueteurId:
                    enqueteur = Enqueteur.query.get(donnee.enqueteurId)
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
                
            return jsonify({"success": True, "data": result})
        except Exception as e:
            logger.error(f"Erreur dans get_donnees_complete: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['POST'])
    def update_donnee_enqueteur(donnee_id):
        """Met à jour les données enquêteur"""
        try:
            data = request.get_json()
            logger.info(f"Données reçues pour mise à jour: {data}")
            
            # Récupérer ou créer l'entrée
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            if not donnee_enqueteur:
                donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee_id)
                db.session.add(donnee_enqueteur)
            
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
            donnee_enqueteur.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Si le code résultat est positif, calculer la facturation
            if donnee_enqueteur.code_resultat in ['P', 'H']:
                try:
                    from services.tarification_service import TarificationService
                    from models.tarifs import EnqueteFacturation
                    
                    existing = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
                    if existing:
                        existing.paye = False
                        if not existing.resultat_enqueteur_montant or existing.resultat_enqueteur_montant <= 0:
                            existing.resultat_enqueteur_montant = 10.0
                        db.session.commit()
                        logger.info(f"Facturation existante mise à jour: {existing.id}")
                    else:
                        facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
                        if facturation:
                            if not facturation.resultat_enqueteur_montant or facturation.resultat_enqueteur_montant <= 0:
                                facturation.resultat_enqueteur_montant = 10.0
                                db.session.commit()
                            logger.info(f"Facturation créée: {facturation.id}")
                except Exception as e:
                    logger.error(f"Erreur lors du calcul de la facturation: {str(e)}")
                                    
            return jsonify({
                'success': True, 
                'message': 'Données mises à jour avec succès',
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 400

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
                enqueteur = Enqueteur.query.get(enqueteur_id)
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
        """Parse et importe un fichier de données"""
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

            # Récupérer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reçue: {date_butoir}")
                except ValueError:
                    logger.warning(f"Format de date butoir invalide: {date_butoir_str}")

            content = file.read()
            if not content:
                return jsonify({"error": "Fichier vide"}), 400

            try:
                nouveau_fichier = Fichier(nom=file.filename)
                db.session.add(nouveau_fichier)
                db.session.commit()
                logger.info(f"Fichier créé avec ID: {nouveau_fichier.id}")

                from utils import process_file_content
                processed_records = process_file_content(content, nouveau_fichier.id, date_butoir)
                
                if processed_records:
                    return jsonify({
                        "message": "Fichier traité avec succès",
                        "file_id": nouveau_fichier.id,
                        "records_processed": len(processed_records)
                    })
                else:
                    db.session.delete(nouveau_fichier)
                    db.session.commit()
                    return jsonify({"error": "Aucun enregistrement valide trouvé"}), 400

            except Exception as e:
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
        """Remplace un fichier existant"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # Récupérer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reçue pour remplacement: {date_butoir}")
                except ValueError:
                    logger.warning(f"Format de date butoir invalide: {date_butoir_str}")

            existing_file = Fichier.query.filter_by(nom=file.filename).first()
            if existing_file:
                Donnee.query.filter_by(fichier_id=existing_file.id).delete()
                db.session.delete(existing_file)
                db.session.commit()

            nouveau_fichier = Fichier(nom=file.filename)
            db.session.add(nouveau_fichier)
            db.session.commit()
            
            content = file.read()
            from utils import process_file_content
            processed_records = process_file_content(content, nouveau_fichier.id, date_butoir)

            return jsonify({
                "message": "Fichier remplacé avec succès",
                "file_id": nouveau_fichier.id,
                "records_processed": len(processed_records)
            })

        except Exception as e:
            logger.error(f"Erreur lors du remplacement: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/files/<int:file_id>', methods=['DELETE'])
    def delete_file(file_id):
        """Supprime un fichier et ses données associées"""
        try:
            fichier = Fichier.query.get_or_404(file_id)
            Donnee.query.filter_by(fichier_id=file_id).delete()
            db.session.delete(fichier)
            db.session.commit()
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
                enquete_originale = Donnee.query.get(donnee.enquete_originale_id)
                
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

    logger.info("Routes legacy enregistrées")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
