"""
Application Flask principale pour le systֳ¨me EOS
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
import re
import unicodedata

# Configuration de l'encodage par dֳ©faut pour Windows
if hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Factory pour crֳ©er l'application Flask"""
    # Valider que PostgreSQL est configurֳ©
    config_class.validate_database_url()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Mettre ֳ  jour l'URI avec la valeur validֳ©e
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.validate_database_url()
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Configuration CORS unifiֳ©e
    # En dֳ©veloppement, autoriser toutes les origines du rֳ©seau local
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # Autoriser toutes les origines (dֳ©veloppement)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": False  # Doit ֳ×tre False quand origins="*"
        }
    })
    
    # Crֳ©er les tables de la base de donnֳ©es via migrations
    with app.app_context():
        # Crֳ©er le dossier instance s'il n'existe pas (pour SQLite en dev)
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Importer tous les modèles pour s'assurer qu'ils sont enregistrés par Alembic
        from models.enquete_archive_file import EnqueteArchiveFile
        from models.export_batch import ExportBatch

        # Les migrations de schéma sont gérées par Alembic (flask db upgrade)
        logger.info("Modèles chargés — schéma géré par Alembic")
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Enregistrer les routes supplֳ©mentaires (legacy)
    register_legacy_routes(app)
    
    logger.info("Application Flask crֳ©ֳ©e avec succֳ¨s")
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
    
    # Enregistrer le blueprint donnees (s'il n'est pas dֳ©jֳ  enregistrֳ© ailleurs)
    
    logger.info("Blueprints enregistrֳ©s")


def register_legacy_routes(app):
    """
    Enregistre les routes legacy qui n'ont pas encore ֳ©tֳ© migrֳ©es vers des blueprints
    Ces routes devraient ֳ×tre progressivement dֳ©placֳ©es vers des blueprints appropriֳ©s
    """
    from flask import request, jsonify, render_template_string
    
    # ===========================
    # MULTI-CLIENT: Route pour rֳ©cupֳ©rer les clients actifs
    # ===========================
    @app.route('/api/clients', methods=['GET'])
    def get_clients():
        """Rֳ©cupֳ¨re la liste des clients actifs"""
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

    ARCHIVED_STATUSES = ('archive', 'archivee', 'valide', 'validee')
    DONNEE_ENQUETEUR_COPY_EXCLUDED_FIELDS = {'id', 'client_id', 'donnee_id', 'created_at', 'updated_at'}
    URGENCY_MARKERS = {'URGENT', 'URGENTE', 'URGENTS', 'URGENTES', 'URGENCE', 'URG'}

    def _normalize_token(value):
        if value is None:
            return ''
        text = str(value).strip()
        if not text:
            return ''
        text = ''.join(
            ch for ch in unicodedata.normalize('NFD', text)
            if unicodedata.category(ch) != 'Mn'
        )
        return re.sub(r'[^A-Z0-9]', '', text.upper())

    def _is_urgency_marker(value):
        return _normalize_token(value) in URGENCY_MARKERS

    def _normalize_contestation_identity(nom_value, prenom_value, type_demande=None):
        nom = (nom_value or '').strip()
        prenom = (prenom_value or '').strip()

        if type_demande == 'CON' and _is_urgency_marker(prenom):
            parts = [part for part in nom.split() if part]
            if len(parts) >= 2:
                return parts[0], ' '.join(parts[1:])
            return nom, ''

        return nom, prenom

    def _extract_name_parts(nom_value, prenom_value):
        nom, prenom = _normalize_contestation_identity(nom_value, prenom_value, 'CON')
        nom_parts = [part for part in nom.split() if part]

        # Build a normalized full name when nom/prenom are split across fields.
        if len(nom_parts) >= 2:
            full_name = nom
        elif prenom and prenom.upper() not in nom.upper():
            full_name = f"{nom} {prenom}".strip()
        else:
            full_name = nom or prenom

        parts = [part for part in full_name.split() if part]
        if len(parts) >= 2:
            return parts[0], ' '.join(parts[1:]), full_name

        return nom, prenom, full_name

    def _build_name_filters(nom_part, prenom_part, full_name):
        filters = []

        if nom_part and prenom_part:
            filters.append(
                db.and_(
                    Donnee.nom.ilike(f"%{nom_part}%"),
                    Donnee.prenom.ilike(f"%{prenom_part}%")
                )
            )
            filters.append(
                db.and_(
                    Donnee.nom.ilike(f"%{prenom_part}%"),
                    Donnee.prenom.ilike(f"%{nom_part}%")
                )
            )

        if full_name:
            filters.append(Donnee.nom.ilike(f"%{full_name}%"))
            filters.append(Donnee.prenom.ilike(f"%{full_name}%"))

        if nom_part:
            filters.append(Donnee.nom.ilike(f"%{nom_part}%"))
        if prenom_part:
            filters.append(Donnee.prenom.ilike(f"%{prenom_part}%"))

        return filters

    def _same_person(contestation_donnee, candidate):
        if not candidate:
            return False

        nom_part, prenom_part, full_name = _extract_name_parts(contestation_donnee.nom, contestation_donnee.prenom)
        nom_token = _normalize_token(nom_part)
        prenom_token = _normalize_token(prenom_part)
        if not nom_token or not prenom_token:
            return False

        candidate_nom_token = _normalize_token(candidate.nom)
        candidate_prenom_token = _normalize_token(candidate.prenom)
        return candidate_nom_token == nom_token and candidate_prenom_token == prenom_token

    def _find_original_candidates(contestation_donnee, archived_only=True, limit=5):
        nom_part, prenom_part, _ = _extract_name_parts(contestation_donnee.nom, contestation_donnee.prenom)
        nom_token = _normalize_token(nom_part)
        prenom_token = _normalize_token(prenom_part)
        if not nom_token or not prenom_token:
            return []

        query = Donnee.query.filter(
            Donnee.client_id == contestation_donnee.client_id,
            Donnee.est_contestation == False
        )

        if archived_only:
            query = query.filter(Donnee.statut_validation.in_(ARCHIVED_STATUSES))

        candidates = query.order_by(Donnee.updated_at.desc()).all()
        strict_matches = []
        for candidate in candidates:
            if _normalize_token(candidate.nom) != nom_token:
                continue
            if _normalize_token(candidate.prenom) != prenom_token:
                continue
            strict_matches.append(candidate)
            if len(strict_matches) >= limit:
                break

        return strict_matches

    def _select_best_original_candidate(contestation_donnee, candidates):
        if not candidates:
            return None

        exact_matches = [candidate for candidate in candidates if _same_person(contestation_donnee, candidate)]
        if exact_matches:
            exact_matches.sort(key=lambda item: item.updated_at or datetime.min, reverse=True)
            return exact_matches[0]

        return candidates[0]

    def _copy_donnee_enqueteur_fields(source_de, target_de):
        if not source_de or not target_de:
            return

        for column in DonneeEnqueteur.__table__.columns:
            field_name = column.name
            if field_name in DONNEE_ENQUETEUR_COPY_EXCLUDED_FIELDS:
                continue
            setattr(target_de, field_name, getattr(source_de, field_name))

    def _merge_donnee_enqueteur_missing_values(current_data, fallback_data):
        merged = dict(current_data or {})
        if not fallback_data:
            return merged

        for key, value in fallback_data.items():
            if key in DONNEE_ENQUETEUR_COPY_EXCLUDED_FIELDS:
                continue
            current_value = merged.get(key)
            if current_value is None or (isinstance(current_value, str) and not current_value.strip()):
                merged[key] = value

        return merged

    def _build_enquete_originale_payload(original_donnee, source):
        if not original_donnee:
            return None

        enqueteur_data = None
        enqueteur_nom = "Non assignֳ©"
        if original_donnee.enqueteurId:
            from models.enqueteur import Enqueteur
            enqueteur = db.session.get(Enqueteur, original_donnee.enqueteurId)
            if enqueteur:
                enqueteur_data = {
                    'id': enqueteur.id,
                    'nom': enqueteur.nom,
                    'prenom': enqueteur.prenom,
                    'email': enqueteur.email
                }
                enqueteur_nom = (
                    f"{enqueteur.prenom} {enqueteur.nom}".strip()
                    if enqueteur.prenom else enqueteur.nom
                )
            else:
                enqueteur_nom = f"ID {original_donnee.enqueteurId}"

        donnee_enqueteur_data = None
        if original_donnee.donnee_enqueteur:
            donnee_enqueteur_data = original_donnee.donnee_enqueteur.to_dict()

        return {
            **original_donnee.to_dict(),
            'enqueteur': enqueteur_data,
            'enqueteurNom': enqueteur_nom,
            'donnee_enqueteur': donnee_enqueteur_data,
            'historique': original_donnee.get_history(),
            'source': source
        }

    def _build_archive_enquete_item(enq):
        return {
            'id': enq.id,
            'numeroDossier': enq.numeroDossier,
            'nom': enq.nom,
            'prenom': enq.prenom,
            'typeDemande': enq.typeDemande,
            'statut_validation': enq.statut_validation,
            'updated_at': enq.updated_at.strftime('%Y-%m-%d %H:%M:%S') if enq.updated_at else None,
            'historique': enq.get_history()
        }

    def _resolve_original_enquete_for_contestation(donnee):
        enquete_originale = None
        archives_enquete_originale = []
        original_candidate_same_client = None

        if donnee.enquete_originale_id:
            original = db.session.get(Donnee, donnee.enquete_originale_id)
            if original and original.client_id == donnee.client_id:
                original_candidate_same_client = original
            elif original:
                logger.warning(
                    f"Lien enquete_originale_id={donnee.enquete_originale_id} invalide "
                    f"(client different) pour contestation {donnee.id}."
                )

        # Priorite: si un lien direct existe et appartient au meme client, on l'utilise.
        if original_candidate_same_client:
            has_name_in_contestation = bool((donnee.nom or '').strip() or (donnee.prenom or '').strip())
            if has_name_in_contestation and not _same_person(donnee, original_candidate_same_client):
                logger.warning(
                    f"Contestation {donnee.id}: lien direct conserve (ID {original_candidate_same_client.id}) "
                    f"malgre un mismatch nom/prenom."
                )
            enquete_originale = _build_enquete_originale_payload(original_candidate_same_client, 'lien_direct')
        else:
            archived_candidates = _find_original_candidates(donnee, archived_only=True, limit=5)
            if archived_candidates:
                best_archived_candidate = _select_best_original_candidate(donnee, archived_candidates)
                for enq in archived_candidates:
                    archives_enquete_originale.append(_build_archive_enquete_item(enq))
                enquete_originale = _build_enquete_originale_payload(best_archived_candidate, 'recherche_archives')

            if not enquete_originale:
                all_candidates = _find_original_candidates(donnee, archived_only=False, limit=5)
                if all_candidates:
                    best_candidate = _select_best_original_candidate(donnee, all_candidates)
                    known_ids = {item['id'] for item in archives_enquete_originale}
                    for enq in all_candidates:
                        if enq.id not in known_ids:
                            archives_enquete_originale.append(_build_archive_enquete_item(enq))
                    enquete_originale = _build_enquete_originale_payload(best_candidate, 'recherche_table_donnees')

        return enquete_originale, archives_enquete_originale

    def _format_history_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        return str(value)

    def _is_filled_value(value):
        if value is None:
            return False
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned or cleaned.lower() in {'nan', 'none'}:
                return False
        return True

    def _extract_filled_enqueteur_fields(donnee_enqueteur):
        if not donnee_enqueteur:
            return {}

        excluded_fields = {'id', 'donnee_id', 'created_at', 'updated_at'}
        raw_data = donnee_enqueteur.to_dict()
        filled_data = {}

        for key, value in raw_data.items():
            if key in excluded_fields:
                continue
            if _is_filled_value(value):
                filled_data[key] = value

        return filled_data

    def _clean_text_value(value):
        if value is None:
            return ''
        text = str(value).strip()
        if not text or text.lower() in {'nan', 'none'}:
            return ''
        return text

    def _compute_elements_letters_from_payload(payload):
        if not isinstance(payload, dict):
            return ''

        has_adresse = any(_is_filled_value(payload.get(field)) for field in [
            'adresse1', 'adresse2', 'adresse3', 'adresse4',
            'code_postal', 'ville', 'pays_residence'
        ])
        has_telephone = any(_is_filled_value(payload.get(field)) for field in [
            'telephone_personnel', 'telephone_chez_employeur'
        ])
        has_banque = any(_is_filled_value(payload.get(field)) for field in [
            'banque_domiciliation', 'libelle_guichet', 'titulaire_compte',
            'code_banque', 'code_guichet'
        ])
        has_employeur = any(_is_filled_value(payload.get(field)) for field in [
            'nom_employeur', 'telephone_employeur', 'telecopie_employeur',
            'adresse1_employeur', 'adresse2_employeur', 'adresse3_employeur',
            'adresse4_employeur', 'code_postal_employeur', 'ville_employeur',
            'pays_employeur'
        ])
        has_revenus = any(_is_filled_value(payload.get(field)) for field in [
            'commentaires_revenus', 'montant_salaire',
            'nature_revenu1', 'montant_revenu1',
            'nature_revenu2', 'montant_revenu2',
            'nature_revenu3', 'montant_revenu3'
        ])
        has_deces = any(_is_filled_value(payload.get(field)) for field in [
            'date_deces', 'numero_acte_deces', 'code_insee_deces',
            'code_postal_deces', 'localite_deces'
        ])

        if has_deces:
            return 'D'

        letters = []
        if has_adresse:
            letters.append('A')
        if has_telephone:
            letters.append('T')
        if has_banque:
            letters.append('B')
        if has_employeur:
            letters.append('E')
        if has_revenus:
            letters.append('R')

        return ''.join(letters)

    def _infer_element_demandes_from_recherche_text(recherche_value):
        recherche_text = _clean_text_value(recherche_value)
        if not recherche_text:
            return ''

        token = _normalize_token(recherche_text)
        if not token:
            return ''

        markers = {
            'A': ('ADRESSE', 'DOMICILE', 'ADR'),
            'T': ('TELEPHONE', 'TEL', 'MOBILE', 'PORTABLE'),
            'B': ('BANQUE', 'RIB', 'IBAN', 'COMPTE', 'GUICHET'),
            'E': ('EMPLOYEUR', 'TRAVAIL', 'SOCIETE'),
            'R': ('REVENU', 'SALAIRE', 'PAIE'),
            'D': ('DECES', 'DECEDE', 'MORT')
        }

        if any(_normalize_token(marker) in token for marker in markers['D']):
            return 'D'

        letters = []
        for letter in ['A', 'T', 'B', 'E', 'R']:
            if any(_normalize_token(marker) in token for marker in markers[letter]):
                letters.append(letter)

        return ''.join(letters)

    def _extract_first_non_empty(record, candidate_keys):
        if not isinstance(record, dict):
            return ''

        for key in candidate_keys:
            if key in record:
                value = _clean_text_value(record.get(key))
                if value:
                    return value

        lower_key_map = {str(k).strip().lower(): k for k in record.keys()}
        for key in candidate_keys:
            mapped_key = lower_key_map.get(str(key).strip().lower())
            if mapped_key is None:
                continue
            value = _clean_text_value(record.get(mapped_key))
            if value:
                return value

        return ''

    def _hydrate_imported_contestation_fields(donnee, donnee_enqueteur, record):
        if not donnee:
            return

        if not _clean_text_value(donnee.elementDemandes):
            inferred_demandes = _infer_element_demandes_from_recherche_text(getattr(donnee, 'recherche', None))
            if inferred_demandes:
                donnee.elementDemandes = inferred_demandes

        if not donnee_enqueteur:
            return

        imported_elements_retrouves = _extract_first_non_empty(record, [
            'elements_retrouves', 'element_retrouve', 'elem_trouve', 'elem trouve', 'elemtrouve'
        ])
        if not imported_elements_retrouves:
            imported_elements_retrouves = _compute_elements_letters_from_payload(record)

        imported_proximite = _extract_first_non_empty(record, [
            'proximite', 'confirme_par', 'confirme par', 'confirmepar'
        ])

        if not _clean_text_value(donnee_enqueteur.elements_retrouves) and imported_elements_retrouves:
            donnee_enqueteur.elements_retrouves = imported_elements_retrouves[:10]

        if not _clean_text_value(donnee_enqueteur.proximite) and imported_proximite:
            donnee_enqueteur.proximite = imported_proximite

    def _build_same_nom_history_rows(donnee):
        """
        Retourne toutes les enquêtes du même client avec le même NOM+PRENOM normalisés.
        """
        from sqlalchemy.orm import joinedload

        nom_reference, prenom_reference, _ = _extract_name_parts(donnee.nom, donnee.prenom)
        nom_token = _normalize_token(nom_reference)
        prenom_token = _normalize_token(prenom_reference)
        if not nom_token or not prenom_token:
            return []

        candidats = Donnee.query.options(
            joinedload(Donnee.donnee_enqueteur),
            joinedload(Donnee.enqueteur)
        ).filter(
            Donnee.client_id == donnee.client_id,
            Donnee.id != donnee.id,
            Donnee.statut_validation.in_(ARCHIVED_STATUSES),
            Donnee.nom.isnot(None),
            db.or_(
                Donnee.nom.ilike(f"%{nom_reference}%"),
                Donnee.prenom.ilike(f"%{nom_reference}%")
            )
        ).all()

        rows = []
        for item in candidats:
            item_nom, item_prenom, _ = _extract_name_parts(item.nom, item.prenom)
            if _normalize_token(item_nom) != nom_token:
                continue
            if _normalize_token(item_prenom) != prenom_token:
                continue

            donnee_enqueteur = item.donnee_enqueteur
            element_demandes_value = _clean_text_value(item.elementDemandes)
            if not element_demandes_value:
                element_demandes_value = _infer_element_demandes_from_recherche_text(getattr(item, 'recherche', None))

            elements_retrouves_value = ''
            proximite_value = ''
            if donnee_enqueteur:
                elements_retrouves_value = _clean_text_value(donnee_enqueteur.elements_retrouves)
                proximite_value = _clean_text_value(donnee_enqueteur.proximite)
                if not elements_retrouves_value:
                    elements_retrouves_value = _compute_elements_letters_from_payload(donnee_enqueteur.to_dict())

            if donnee_enqueteur and donnee_enqueteur.date_retour:
                date_value = donnee_enqueteur.date_retour
            elif item.date_contestation:
                date_value = item.date_contestation
            elif item.updated_at:
                date_value = item.updated_at
            else:
                date_value = item.created_at

            if isinstance(date_value, datetime):
                sort_value = date_value
            elif date_value and hasattr(date_value, 'year'):
                sort_value = datetime.combine(date_value, datetime.min.time())
            else:
                sort_value = item.updated_at or item.created_at or datetime.min

            rows.append((
                sort_value,
                {
                    'id': item.id,
                    'numeroDossier': item.numeroDossier,
                    'typeDemande': item.typeDemande,
                    'est_contestation': item.est_contestation,
                    'statut_validation': item.statut_validation,
                    'nom': item.nom,
                    'prenom': item.prenom,
                    'dateNaissance': item.dateNaissance.strftime('%Y-%m-%d') if item.dateNaissance else None,
                    'date': _format_history_date(date_value),
                    'element_demandes': element_demandes_value or None,
                    'code_resultat': donnee_enqueteur.code_resultat if donnee_enqueteur else None,
                    'elements_retrouves': elements_retrouves_value or None,
                    'proximite': proximite_value or None,
                    'memo_personnel': donnee_enqueteur.notes_personnelles if donnee_enqueteur else None,
                    'enqueteur': item.enqueteur.to_dict() if item.enqueteur else None,
                    'donnee_enqueteur_saisie': _extract_filled_enqueteur_fields(donnee_enqueteur)
                }
            ))

        rows.sort(key=lambda pair: pair[0], reverse=True)
        return [payload for _, payload in rows]
    
    @app.route('/')
    def index():
        """Page d'accueil de l'API"""
        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API EOS - Systֳ¨me de Gestion d'Enquֳ×tes</title>
            <link rel="stylesheet" href="/static/api.css">
        </head>
        <body>
            <div class="container">
                <h1>נ€ API EOS</h1>
                <p class="subtitle">Systֳ¨me de Gestion d'Enquֳ×tes</p>
                
                <div class="status">
                    <div class="status-icon">ג…</div>
                    <strong>Serveur opֳ©rationnel</strong><br>
                    L'API est en ligne et prֳ×te ֳ  recevoir des requֳ×tes
                </div>

                <div class="endpoints">
                    <div class="endpoint-group">
                        <h3>נ“ Routes Principales</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/stats</span> - Statistiques globales
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/donnees</span> - Liste des donnֳ©es
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enqueteurs</span> - Liste des enquֳ×teurs
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>נ” Enquֳ×tes</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enquetes/pending</span> - Enquֳ×tes en attente
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/enquetes/completed</span> - Enquֳ×tes terminֳ©es
                        </div>
                        <div class="endpoint">
                            <span class="method post">POST</span>
                            <span>/api/assign-enquete</span> - Assigner une enquֳ×te
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>נ’° Tarification & Paiements</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/tarifs/eos</span> - Tarifs EOS
                        </div>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/paiement/enqueteurs-a-payer</span> - Enquֳ×teurs ֳ  payer
                        </div>
                    </div>

                    <div class="endpoint-group">
                        <h3>נ§× Test</h3>
                        <div class="endpoint">
                            <span class="method get">GET</span>
                            <span>/api/test-cors</span> - Test de configuration CORS
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>Pour accֳ©der ֳ  l'interface frontend, ouvrez : 
                        <a href="http://localhost:5173" target="_blank">http://localhost:5173</a>
                    </p>
                    <p style="margin-top: 10px;">
                        Documentation complֳ¨te disponible dans le projet
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
            "description": "Systֳ¨me de Gestion d'Enquֳ×tes",
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
            "documentation": "Voir la page d'accueil ֳ  http://localhost:5000/"
        })
    
    @app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
    def test_cors():
        """Route de test pour vֳ©rifier la configuration CORS"""
        if request.method == 'OPTIONS':
            return '', 200
        return jsonify({"status": "ok", "message": "CORS fonctionne correctement"})

    @app.route('/api/stats', methods=['GET', 'OPTIONS'])
    def get_stats():
        """Rֳ©cupֳ¨re les statistiques globales et dֳ©taillֳ©es par client"""
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
                # Nombre total importֳ© pour ce client
                imported = Donnee.query.filter_by(client_id=client.id).count()
                
                # Nombre traitֳ© (ayant une rֳ©ponse d'enquֳ×teur)
                treated = (db.session.query(func.count(Donnee.id))
                          .join(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id)
                          .filter(Donnee.client_id == client.id)
                          .scalar())
                
                # Nombre archivֳ© (validֳ©)
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
        """Rֳ©cupֳ¨re la liste des donnֳ©es avec pagination (multi-client)"""
        try:
            # MULTI-CLIENT: Rֳ©cupֳ©rer le client
            from client_utils import get_client_or_default
            
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 500, type=int)
            
            # Logique spֳ©cifique pour Sherlock
            if client.code == 'RG_SHERLOCK':
                from models import SherlockDonnee
                pagination = SherlockDonnee.query.filter_by(fichier_id=Fichier.id).join(Fichier).filter(Fichier.client_id == client.id).paginate(
                    page=page, per_page=per_page, error_out=False
                )
                # Alternative simplifiֳ©e si on n'a pas besoin de jointure complexe (fichier_id est FK)
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
                    # Champs manquants pour ֳ©viter les erreurs prop-types
                    item_dict['enqueteurId'] = None 
                    data.append(item_dict)
            else:
                # Comportement standard ג€” exclure les enquֳ×tes archivֳ©es/validֳ©es
                pagination = Donnee.query.filter(
                    Donnee.client_id == client.id,
                    Donnee.statut_validation.notin_(['valide', 'validee', 'archive', 'archivee'])
                ).paginate(
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
        """Rֳ©cupֳ¨re les enquetes ayant le meme nom pour l'affichage Historique."""
        try:
            donnee = Donnee.query.get_or_404(donnee_id)
            display_nom, display_prenom = _normalize_contestation_identity(
                donnee.nom,
                donnee.prenom,
                donnee.typeDemande
            )
            enquetes_meme_nom = _build_same_nom_history_rows(donnee)
            contestation_header = (
                f"Contestation {donnee.numeroDossier or ''}".strip()
                if donnee.typeDemande == 'CON' or donnee.est_contestation
                else f"Dossier {donnee.numeroDossier or ''}".strip()
            )

            data = {
                'nom': display_nom,
                'prenom': display_prenom,
                'donnee_id': donnee.id,
                'numero_dossier': donnee.numeroDossier,
                'type_demande': donnee.typeDemande,
                'est_contestation': donnee.est_contestation,
                'contestation_header': contestation_header,
                'element_demandes_source': donnee.elementDemandes,
                'enquetes_meme_nom': enquetes_meme_nom,
                'count': len(enquetes_meme_nom)
            }
            
            return jsonify({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration de l'historique: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/historique-enquete/<string:numero_dossier>', methods=['GET'])
    def get_historique_enquete_par_numero(numero_dossier):
        """
        Rֳ©cupֳ¨re l'historique complet d'une enquֳ×te contestation par son numeroDossier
        Utilisֳ© spֳ©cifiquement pour les contestations PARTNER
        Cherche aussi dans les archives si l'enquֳ×te originale n'est pas trouvֳ©e
        IMPORTANT: Cherche PRIORITAIREMENT les contestations (est_contestation=True)
        """
        try:
            from models.enquete_archive import EnqueteArchive

            donnee = None

            # Permet de dֳ©sambiguֳ¯ser quand numeroDossier n'est pas unique.
            donnee_id_param = request.args.get('donnee_id', type=int)
            if donnee_id_param:
                donnee = db.session.get(Donnee, donnee_id_param)
                if donnee and donnee.numeroDossier and donnee.numeroDossier != numero_dossier:
                    logger.warning(
                        f"Historique demandֳ© avec numero_dossier={numero_dossier} "
                        f"mais donnee_id={donnee_id_param} a numeroDossier={donnee.numeroDossier}"
                    )
            
            # Chercher PRIORITAIREMENT une contestation par numeroDossier
            # Car les numeroDossier ne sont pas uniques dans PARTNER
            if not donnee:
                donnee = Donnee.query.filter_by(
                    numeroDossier=numero_dossier,
                    est_contestation=True
                ).order_by(Donnee.updated_at.desc()).first()
            
            # Si pas de contestation trouvֳ©e, chercher dans toutes les enquֳ×tes
            if not donnee:
                donnee = Donnee.query.filter_by(numeroDossier=numero_dossier).order_by(Donnee.updated_at.desc()).first()
            
            if not donnee:
                return jsonify({
                    'success': False,
                    'error': f'Aucune enquֳ×te trouvֳ©e avec le numֳ©ro de dossier {numero_dossier}'
                }), 404

            display_nom, display_prenom = _normalize_contestation_identity(
                donnee.nom,
                donnee.prenom,
                donnee.typeDemande
            )
            
            # Rֳ©cupֳ©rer l'historique
            history = donnee.get_history()
            
            # Rֳ©cupֳ©rer les contestations liֳ©es
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
            
            # Si c'est une contestation, chercher l'enquֳ×te originale
            enquete_originale = None
            archives_enquete_originale = []
            
            if donnee.est_contestation:
                enquete_originale, archives_enquete_originale = _resolve_original_enquete_for_contestation(donnee)
            
            # Rֳ©cupֳ©rer l'historique des modifications
            modifications = []
            if donnee.donnee_enqueteur:
                modifications = [{
                    'date': donnee.donnee_enqueteur.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'code_resultat': donnee.donnee_enqueteur.code_resultat,
                    'elements_retrouves': donnee.donnee_enqueteur.elements_retrouves
                }]
            
            # Informations complֳ¨tes pour le frontend
            data = {
                'historique': history,
                'contestations': contestations,
                'enquete_originale': enquete_originale,
                'archives_enquete_originale': archives_enquete_originale,  # Nouvelles archives
                'modifications': modifications,
                'est_contestation': donnee.est_contestation,
                'numero_dossier': donnee.numeroDossier,
                'type_demande': donnee.typeDemande,
                'created_at': donnee.created_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.created_at else None,
                'updated_at': donnee.updated_at.strftime('%Y-%m-%d %H:%M:%S') if donnee.updated_at else None,
                'nom': display_nom,
                'prenom': display_prenom,
                'date_contestation': donnee.date_contestation.strftime('%Y-%m-%d') if donnee.date_contestation else None,
                'motif_contestation_code': donnee.motif_contestation_code,
                'motif_contestation_detail': donnee.motif_contestation_detail,
                'statut_validation': donnee.statut_validation
            }
            
            logger.info(f"Historique rֳ©cupֳ©rֳ© pour contestation {numero_dossier}")
            
            return jsonify({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration de l'historique par numero_dossier: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/archives-enquetes/<int:donnee_id>', methods=['GET'])
    def get_archives_enquetes(donnee_id):
        """
        Rֳ©cupֳ¨re toutes les archives (snapshots) d'une enquֳ×te dans EnqueteArchive
        """
        try:
            from models.enquete_archive import EnqueteArchive
            
            # Chercher toutes les archives pour cette enquֳ×te (le champ est enquete_id pas donnee_id)
            archives = EnqueteArchive.query.filter_by(enquete_id=donnee_id).order_by(
                EnqueteArchive.date_export.desc()
            ).all()
            
            result = []
            for archive in archives:
                result.append({
                    'id': archive.id,
                    'enquete_id': archive.enquete_id,
                    'date_export': archive.date_export.strftime('%Y-%m-%d %H:%M:%S') if archive.date_export else None,
                    'nom_fichier': archive.nom_fichier,
                    'utilisateur': archive.utilisateur
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'count': len(result)
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration des archives enquֳ×tes: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/archives-enqueteurs/<int:donnee_id>', methods=['GET'])
    def get_archives_enqueteurs(donnee_id):
        """
        Rֳ©cupֳ¨re toutes les archives (snapshots) des donnֳ©es enquֳ×teur
        Note: EnqueteArchive ne stocke pas directement les donnֳ©es enquֳ×teur
        Cette route retourne un tableau vide pour le moment
        """
        try:
            # Pour le moment, retourner un tableau vide car EnqueteArchive
            # ne contient pas de snapshot_data avec les donnֳ©es enquֳ×teur
            result = []
            
            return jsonify({
                'success': True,
                'data': result,
                'count': len(result)
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration des archives enquֳ×teurs: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees-complete/<int:donnee_id>', methods=['GET'])
    def get_donnee_complete(donnee_id):
        """
        Rֳ©cupֳ¨re une donnֳ©e complֳ¨te avec toutes ses informations (motifs de contestation, etc.)
        """
        try:
            donnee = Donnee.query.get_or_404(donnee_id)
            donnee_dict = donnee.to_dict()
            
            # Ajouter les donnֳ©es enquֳ×teur
            if donnee.donnee_enqueteur:
                donnee_dict['donnee_enqueteur'] = donnee.donnee_enqueteur.to_dict()
            
            # Ajouter les informations de l'enquֳ×teur
            if donnee.enqueteurId:
                from models.enqueteur import Enqueteur
                enqueteur = db.session.get(Enqueteur, donnee.enqueteurId)
                if enqueteur:
                    donnee_dict['enqueteur'] = {
                        'id': enqueteur.id,
                        'nom': enqueteur.nom,
                        'prenom': enqueteur.prenom
                    }
            
            # Ajouter les informations du client
            from models.client import Client
            client = db.session.get(Client, donnee.client_id)
            if client:
                donnee_dict['client'] = {
                    'id': client.id,
                    'code': client.code,
                    'nom': client.nom
                }
            
            # Si c'est une contestation, ajouter l'enquֳ×te originale
            if donnee.est_contestation and donnee.enquete_originale_id:
                original = db.session.get(Donnee, donnee.enquete_originale_id)
                if original:
                    donnee_dict['enquete_originale'] = {
                        'id': original.id,
                        'numeroDossier': original.numeroDossier,
                        'nom': original.nom,
                        'prenom': original.prenom,
                        'typeDemande': original.typeDemande
                    }
            
            return jsonify({
                'success': True,
                'data': donnee_dict
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration de la donnֳ©e complֳ¨te: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees/<int:id>', methods=['GET'])
    def get_donnee(id):
        """Rֳ©cupֳ¨re une donnֳ©e spֳ©cifique avec les informations du client et enquֳ×te originale"""
        try:
            donnee = Donnee.query.get_or_404(id)
            donnee_dict = donnee.to_dict()
            display_nom, display_prenom = _normalize_contestation_identity(
                donnee.nom,
                donnee.prenom,
                donnee.typeDemande
            )
            donnee_dict['nom'] = display_nom
            donnee_dict['prenom'] = display_prenom
            
            # Ajouter les informations du client
            from models.client import Client
            client = db.session.get(Client, donnee.client_id)
            if client:
                donnee_dict['client'] = {
                    'id': client.id,
                    'code': client.code,
                    'nom': client.nom
                }
            
            # Si c'est une contestation, ajouter l'enquֳ×te originale COMPLֳˆTE
            if donnee.est_contestation:
                original_payload, _ = _resolve_original_enquete_for_contestation(donnee)
                if original_payload:
                    enqueteur_data = original_payload.get('enqueteur')
                    donnee_dict['enqueteOriginale'] = {
                        **original_payload,
                        'enqueteurNom': f"{enqueteur_data['prenom']} {enqueteur_data['nom']}" if enqueteur_data and enqueteur_data.get('prenom') else (enqueteur_data['nom'] if enqueteur_data else "Non assignֳ©")
                    }
            
            return jsonify({'success': True, 'data': donnee_dict}), 200
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration de la donnֳ©e: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/donnees/<int:id>', methods=['DELETE'])
    def delete_donnee(id):
        """Supprime une donnֳ©e"""
        try:
            donnee = Donnee.query.get_or_404(id)
            db.session.delete(donnee)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Enregistrement supprimֳ© avec succֳ¨s'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            
            # Message d'erreur plus clair pour les violations de contraintes
            error_message = 'Erreur lors de la suppression'
            if 'ForeignKeyViolation' in str(e) or 'foreign key constraint' in str(e).lower():
                error_message = 'Impossible de supprimer ce dossier car il contient des donnֳ©es enquֳ×teur. Exֳ©cutez CORRIGER_CASCADE_SUPPRESSION.bat pour rֳ©soudre ce problֳ¨me.'
            
            return jsonify({'success': False, 'error': error_message}), 500

    @app.route('/api/donnees', methods=['POST'])
    def add_donnee():
        """Ajoute une nouvelle donnֳ©e avec assignation d'enquֳ×teur (multi-client)"""
        try:
            data = request.json
            
            # MULTI-CLIENT: Rֳ©cupֳ©rer le client
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
                enqueteurId=data.get('enqueteurId'),  # Assignation d'enquֳ×teur
                fichier_id=data.get('fichier_id', 1)  # Fichier par dֳ©faut
            )
            db.session.add(nouvelle_donnee)
            db.session.commit()
            
            # Crֳ©er automatiquement une entrֳ©e dans DonneeEnqueteur
            new_donnee_enqueteur = DonneeEnqueteur(
                donnee_id=nouvelle_donnee.id,
                client_id=client.id  # MULTI-CLIENT
            )
            db.session.add(new_donnee_enqueteur)
            db.session.commit()
            
            logger.info(f"Nouvelle enquֳ×te crֳ©ֳ©e (ID: {nouvelle_donnee.id}) avec enquֳ×teur ID: {nouvelle_donnee.enqueteurId}")
            
            return jsonify({
                'success': True,
                'message': 'Donnֳ©es ajoutֳ©es avec succֳ¨s',
                'data': nouvelle_donnee.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/donnees/<int:id>', methods=['PUT'])
    def update_donnee(id):
        """Met ֳ  jour une donnֳ©e existante (y compris l'enquֳ×teur assignֳ©)"""
        try:
            donnee = Donnee.query.get_or_404(id)
            data = request.json
            
            # Rֳ©cupֳ©rer le client pour vֳ©rifier les permissions
            from models.client import Client
            client = db.session.get(Client, donnee.client_id)
            is_client_x = client and client.code != 'EOS'
            
            # Mettre ֳ  jour les champs fournis
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
            
            # Assignation/Modification d'enquֳ×teur
            if 'enqueteurId' in data:
                donnee.enqueteurId = data['enqueteurId']
                logger.info(f"Enquֳ×te {id} : Enquֳ×teur changֳ© -> ID {donnee.enqueteurId}")
            
            donnee.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Donnֳ©es modifiֳ©es avec succֳ¨s',
                'data': donnee.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la modification: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees-enqueteur/<int:donnee_id>', methods=['GET'])
    def get_donnee_enqueteur(donnee_id):
        """Rֳ©cupֳ¨re les donnֳ©es enquֳ×teur pour une donnֳ©e (crֳ©e automatiquement si inexistant pour PARTNER)"""
        try:
            donnee = db.session.get(Donnee, donnee_id)
            if not donnee:
                return jsonify({
                    'success': False,
                    'error': 'Dossier introuvable'
                }), 404

            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            
            if not donnee_enqueteur:
                # Pour PARTNER : crֳ©er automatiquement un DonneeEnqueteur vide
                from models.client import Client
                client = db.session.get(Client, donnee.client_id)
                is_partner = client and client.code == 'PARTNER'
                
                if is_partner:
                    # Crֳ©er un DonneeEnqueteur vide pour PARTNER
                    donnee_enqueteur = DonneeEnqueteur(
                        donnee_id=donnee_id,
                        client_id=donnee.client_id
                    )
                    db.session.add(donnee_enqueteur)
                    db.session.commit()
                    logger.info(f"DonneeEnqueteur crֳ©ֳ© automatiquement pour dossier PARTNER {donnee_id}")
                else:
                    # Pour EOS : retourner 404 (comportement normal)
                    return jsonify({
                        'success': False, 
                        'error': 'Aucune donnֳ©e enquֳ×teur trouvֳ©e pour cet ID'
                    }), 404

            response_data = donnee_enqueteur.to_dict()
                
            return jsonify({
                'success': True, 
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration des donnֳ©es enquֳ×teur: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/donnees/non-exportees/count', methods=['GET'])
    def get_non_exportees_count():
        """Compte le nombre d'enquֳ×tes non encore exportֳ©es (filtrֳ© par client)"""
        try:
            # MULTI-CLIENT: Rֳ©cupֳ©rer le client (par dֳ©faut EOS)
            from client_utils import get_client_or_default
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404

            count = Donnee.query.filter(
                Donnee.client_id == client.id,  # Filtrer par client
                Donnee.statut_validation.notin_(['valide', 'validee', 'archive', 'archivee']),
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
        """Rֳ©cupֳ¨re les donnֳ©es complֳ¨tes avec jointure, pagination et filtres (multi-client)"""
        try:
            # MULTI-CLIENT: Rֳ©cupֳ©rer le client (par dֳ©faut EOS)
            from client_utils import get_client_or_default
            
            client_id_param = request.args.get('client_id', type=int)
            client_code_param = request.args.get('client_code', type=str)
            
            # Si aucun client spֳ©cifiֳ©, utiliser EOS par dֳ©faut
            client = get_client_or_default(client_id=client_id_param, client_code=client_code_param)
            if not client:
                return jsonify({"success": False, "error": "Client introuvable"}), 404
            
            logger.info(f"Liste des donnֳ©es pour client: {client.code} (ID: {client.id})")
            
            # Paramֳ¨tres de pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 500, type=int)
            # Limiter per_page ֳ  1000 max pour ֳ©viter les surcharges
            per_page = min(per_page, 1000)
            
            # LOGIQUE SPֳ‰CIFIQUE SHERLOCK
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
                
                # 4. Construction de la rֳ©ponse
                result = []
                for item in pagination.items:
                    d = item.to_dict()
                    
                    # Mapping vers le schֳ©ma standard Donnee pour le frontend
                    frontend_item = {
                        'id': item.id,
                        'numeroDossier': item.dossier_id,
                        'nom': item.ec_nom_usage,
                        'prenom': item.ec_prenom,
                        'typeDemande': item.demande or 'ENQ',
                        
                        # Mapping Rֳ©sultat -> Statut/Code Resultat
                        'code_resultat': item.resultat if item.resultat else None,
                        
                        # Infos Enquֳ×teur (Non applicable)
                        'enqueteurId': None,
                        'enqueteur_nom': None,
                        'enqueteur_prenom': None,
                        'has_response': True if item.resultat else False,
                        'can_validate': False,
                        'statut_validation': 'en_cours',
                        
                        # Dates
                        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None,
                        # Pas de date butoir rֳ©elle, on met null ou une valeur par dֳ©faut
                        'date_butoir': None,
                        
                        # Autres champs pour compatibilitֳ©
                        'elements_retrouves': None, # Pourrait ֳ×tre mappֳ© depuis les colonnes AD-...
                    }
                    
                    # Fusionner avec les donnֳ©es brutes d'abord
                    final_item = d.copy()
                    final_item.update(frontend_item)
                    
                    # Nettoyage des donnֳ©es (NaN -> None, "nan" -> None)
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
            # Construire la requֳ×te de base AVEC FILTRAGE CLIENT
            query = db.session.query(Donnee).options(
                db.joinedload(Donnee.donnee_enqueteur)
            ).filter(
                Donnee.client_id == client.id,  # MULTI-CLIENT: Filtre par client
                Donnee.statut_validation.notin_(['valide', 'validee', 'archive', 'archivee'])
            )
            
            # === FILTRES Cֳ”Tֳ‰ SERVEUR ===
            
            # Filtre par statut de validation
            statut = request.args.get('statut_validation')
            if statut:
                query = query.filter(Donnee.statut_validation == statut)
            
            # Filtre par type de demande
            type_demande = request.args.get('typeDemande')
            if type_demande:
                query = query.filter(Donnee.typeDemande == type_demande)
            
            # Filtre par enquֳ×teur assignֳ©
            enqueteur_id = request.args.get('enqueteurId')
            if enqueteur_id:
                if enqueteur_id == 'unassigned':
                    query = query.filter(Donnee.enqueteurId.is_(None))
                else:
                    query = query.filter(Donnee.enqueteurId == int(enqueteur_id))
            
            # Filtre par code rֳ©sultat
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
            
            # Filtre par date de rֳ©ception (range)
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
            
            # Filtre enquֳ×tes exportֳ©es/non exportֳ©es
            exported = request.args.get('exported')
            if exported:
                query = query.filter(Donnee.exported == (exported.lower() == 'true'))
            
            # Tri (par dֳ©faut : date de crֳ©ation dֳ©croissante)
            sort_by = request.args.get('sort_by', 'created_at')
            sort_order = request.args.get('sort_order', 'desc')
            
            if hasattr(Donnee, sort_by):
                sort_column = getattr(Donnee, sort_by)
                if sort_order == 'asc':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                # Par dֳ©faut
                query = query.order_by(Donnee.created_at.desc())
            
            # === PAGINATION ===
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            donnees = pagination.items
            
            # Construire les rֳ©sultats avec donnֳ©es enrichies
            result = []
            for donnee in donnees:
                donnee_dict = donnee.to_dict()
                
                # PRֳ‰SERVER les adresses originales du fichier importֳ©
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
                
                # Indicateur si l'enquֳ×te a une rֳ©ponse d'enquֳ×teur
                has_response = False
                if donnee.donnee_enqueteur:
                    for k, v in donnee.donnee_enqueteur.to_dict().items():
                        if k not in ['id', 'donnee_id']:
                            donnee_dict[k] = v
                    # Vֳ©rifier si l'enquֳ×te a une rֳ©ponse complֳ¨te
                    has_response = (
                        donnee.donnee_enqueteur.code_resultat is not None and
                        donnee.donnee_enqueteur.code_resultat != ''
                    )
                
                # Ajouter les donnֳ©es originales (ne seront pas ֳ©crasֳ©es)
                donnee_dict.update(adresses_originales)
                
                # Ajouter les indicateurs pour la validation
                donnee_dict['has_response'] = has_response
                # Les enquֳ×tes avec statut 'confirmee' peuvent ֳ×tre validֳ©es par l'admin
                donnee_dict['can_validate'] = has_response and donnee.statut_validation == 'confirmee'
                
                # Ajouter les informations de l'enquֳ×teur assignֳ©
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
            
            # Rֳ©ponse paginֳ©e
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
        """Met ֳ  jour les donnֳ©es enquֳ×teur"""
        try:
            data = request.get_json()
            logger.info(f"Donnֳ©es reֳ§ues pour mise ֳ  jour: {data}")
            
            # Rֳ©cupֳ©rer la Donnee parent pour obtenir le client_id
            donnee_parent = Donnee.query.get(donnee_id)
            if not donnee_parent:
                return jsonify({'success': False, 'error': 'Enquֳ×te introuvable'}), 404
            
            # Vֳ©rifier le type de client pour assouplir les validations
            from models.client import Client
            client = db.session.get(Client, donnee_parent.client_id)
            is_client_x = client and client.code != 'EOS'
            is_partner = client and client.code == 'PARTNER'

            def _has_value(value):
                if value is None:
                    return False
                if isinstance(value, str):
                    return bool(value.strip())
                return True

            def _compute_elements_retrouves(payload):
                if not isinstance(payload, dict):
                    return ''

                has_adresse = any(_has_value(payload.get(field)) for field in [
                    'adresse1', 'adresse2', 'adresse3', 'adresse4',
                    'code_postal', 'ville', 'pays_residence'
                ])
                has_telephone = any(_has_value(payload.get(field)) for field in [
                    'telephone_personnel', 'telephone_chez_employeur'
                ])
                has_banque = any(_has_value(payload.get(field)) for field in [
                    'banque_domiciliation', 'libelle_guichet', 'titulaire_compte',
                    'code_banque', 'code_guichet'
                ])
                has_employeur = any(_has_value(payload.get(field)) for field in [
                    'nom_employeur', 'telephone_employeur', 'telecopie_employeur',
                    'adresse1_employeur', 'adresse2_employeur', 'adresse3_employeur',
                    'adresse4_employeur', 'code_postal_employeur', 'ville_employeur',
                    'pays_employeur'
                ])
                has_revenus = any(_has_value(payload.get(field)) for field in [
                    'commentaires_revenus', 'montant_salaire',
                    'nature_revenu1', 'montant_revenu1',
                    'nature_revenu2', 'montant_revenu2',
                    'nature_revenu3', 'montant_revenu3'
                ])
                has_deces = any(_has_value(payload.get(field)) for field in [
                    'date_deces', 'numero_acte_deces', 'code_insee_deces',
                    'code_postal_deces', 'localite_deces'
                ])

                if has_deces:
                    return 'D'

                letters = []
                if has_adresse:
                    letters.append('A')
                if has_telephone:
                    letters.append('T')
                if has_banque:
                    letters.append('B')
                if has_employeur:
                    letters.append('E')
                if has_revenus:
                    letters.append('R')

                return ''.join(letters)
            
            # Rֳ©cupֳ©rer ou crֳ©er l'entrֳ©e
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
            if not donnee_enqueteur:
                donnee_enqueteur = DonneeEnqueteur(
                    donnee_id=donnee_id,
                    client_id=donnee_parent.client_id  # AJOUT du client_id
                )
                db.session.add(donnee_enqueteur)
                # Flush pour obtenir l'ID avant de continuer
                db.session.flush()
            
            # Mettre ֳ  jour les champs
            for field in ['code_resultat', 'elements_retrouves', 'proximite', 'flag_etat_civil_errone',
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

            # PARTNER: proximite = "confirme par", elements_retrouves = elements trouves.
            if is_partner:
                proximite_value = data.get('proximite') if 'proximite' in data else data.get('elements_retrouves')
                if isinstance(proximite_value, str):
                    proximite_value = proximite_value.strip()
                donnee_enqueteur.proximite = proximite_value or None

                elements_detectes = _compute_elements_retrouves(data)
                donnee_enqueteur.elements_retrouves = elements_detectes or None
            elif 'proximite' in data:
                proximite_value = data.get('proximite')
                if isinstance(proximite_value, str):
                    proximite_value = proximite_value.strip()
                donnee_enqueteur.proximite = proximite_value or None
            
            # Mise ֳ  jour de la date de modification
            donnee_enqueteur.updated_at = datetime.now()
            
            # Pour PARTNER (CLIENT_X), mettre ֳ  jour dateNaissance_maj et lieuNaissance_maj dans Donnee
            if is_client_x:
                if 'dateNaissance_maj' in data:
                    if data.get('dateNaissance_maj'):
                        try:
                            donnee_parent.dateNaissance_maj = datetime.strptime(data.get('dateNaissance_maj'), '%Y-%m-%d').date()
                            logger.info(f"Date de naissance (MAJ) mise ֳ  jour pour enquֳ×te {donnee_id}: {donnee_parent.dateNaissance_maj}")
                        except ValueError as e:
                            logger.error(f"Format de date invalide: {data.get('dateNaissance_maj')} - {e}")
                            raise ValueError(f"Format de date invalide: {data.get('dateNaissance_maj')}. Attendu: YYYY-MM-DD")
                    else:
                        donnee_parent.dateNaissance_maj = None
                
                if 'lieuNaissance_maj' in data:
                    donnee_parent.lieuNaissance_maj = data.get('lieuNaissance_maj')
                    logger.info(f"Lieu de naissance (MAJ) mis ֳ  jour pour enquֳ×te {donnee_id}: {donnee_parent.lieuNaissance_maj}")
                
                donnee_parent.updated_at = datetime.now()
            
            # Si le code rֳ©sultat est positif, prֳ©parer la facturation
            # Pour CLIENT_X, ne pas exiger de validation stricte
            if donnee_enqueteur.code_resultat in ['P', 'H']:
                try:
                    from services.tarification_service import TarificationService
                    from models.tarifs import EnqueteFacturation
                    
                    # Pour CLIENT_X, utiliser le tarif_lettre de la donnֳ©e parent si disponible
                    if is_client_x and not is_partner and donnee_parent.tarif_lettre and not donnee_enqueteur.elements_retrouves:
                        donnee_enqueteur.elements_retrouves = donnee_parent.tarif_lettre
                    
                    existing = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
                    if existing:
                        existing.paye = False
                        if not existing.resultat_enqueteur_montant or existing.resultat_enqueteur_montant <= 0:
                            existing.resultat_enqueteur_montant = 10.0
                        logger.info(f"Facturation existante mise ֳ  jour: {existing.id}")
                    else:
                        facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
                        if facturation:
                            if not facturation.resultat_enqueteur_montant or facturation.resultat_enqueteur_montant <= 0:
                                facturation.resultat_enqueteur_montant = 10.0
                            logger.info(f"Facturation crֳ©ֳ©e: {facturation.id}")
                except Exception as e:
                    logger.error(f"Erreur lors du calcul de la facturation: {str(e)}")
                    # Pour CLIENT_X, ne pas bloquer si la facturation ֳ©choue
                    if not is_client_x:
                        raise
                
                # Mettre ֳ  jour le statut_validation automatiquement pour PARTNER
                # Quand un code rֳ©sultat positif est saisi, l'enquֳ×te passe directement ֳ  'validee'
                if is_client_x and donnee_parent.statut_validation == 'en_attente':
                    donnee_parent.statut_validation = 'validee'
                    donnee_parent.exported = False  # Marquer comme non exportֳ©e pour qu'elle apparaisse dans Export
                    logger.info(f"Statut mis ֳ  jour automatiquement: enquֳ×te {donnee_id} -> validee")
            
            # Si le code rֳ©sultat est nֳ©gatif (N, Z, I, Y), marquer comme validֳ©e aussi
            elif donnee_enqueteur.code_resultat in ['N', 'Z', 'I', 'Y']:
                if is_client_x and donnee_parent.statut_validation == 'en_attente':
                    donnee_parent.statut_validation = 'validee'
                    donnee_parent.exported = False
                    logger.info(f"Statut mis ֳ  jour automatiquement: enquֳ×te {donnee_id} (nֳ©gative) -> validee")
            
            # UN SEUL COMMIT ֳ  la fin pour ֳ©viter les conflits
            db.session.commit()
            
            # Pour PARTNER : Recalculer automatiquement les demandes aprֳ¨s la sauvegarde
            if is_client_x:
                try:
                    from services.partner_request_calculator import PartnerRequestCalculator
                    result = PartnerRequestCalculator.recalculate_all_requests(donnee_id)
                    logger.info(f"Recalcul automatique PARTNER pour donnee_id={donnee_id}: {result['pos']} POS, {result['neg']} NEG")
                except Exception as e:
                    logger.error(f"Erreur lors du recalcul automatique PARTNER: {str(e)}")
                    # Ne pas bloquer l'enregistrement si le recalcul ֳ©choue
                                    
            return jsonify({
                'success': True, 
                'message': 'Donnֳ©es mises ֳ  jour avec succֳ¨s',
                'data': donnee_enqueteur.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise ֳ  jour: {str(e)}")
            
            # Message plus clair si l'enquֳ×te a ֳ©tֳ© supprimֳ©e
            error_msg = str(e)
            if "has been deleted" in error_msg or "is otherwise not present" in error_msg:
                error_msg = "Cette enquֳ×te a ֳ©tֳ© supprimֳ©e. Veuillez rafraֳ®chir la page (F5)."
            
            return jsonify({'success': False, 'error': error_msg}), 400

    @app.route('/api/assign-enquete', methods=['POST'])
    def assign_enquete():
        """Assigne une enquֳ×te ֳ  un enquֳ×teur"""
        try:
            data = request.json
            logger.info(f"Donnֳ©es reֳ§ues pour l'assignation: {data}")
            
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
                return jsonify({'success': False, 'error': 'Enquֳ×te not found'}), 404
                
            if enqueteur_id:
                enqueteur = db.session.get(Enqueteur, enqueteur_id)
                if not enqueteur:
                    return jsonify({'success': False, 'error': 'Enquֳ×teur not found'}), 404
            
            enquete.enqueteurId = enqueteur_id if enqueteur_id != '' else None
            db.session.commit()
            
            # Recalculer la facturation si nֳ©cessaire
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
        """Obtenir des statistiques sur les enquֳ×teurs"""
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
            logger.error(f"Erreur lors de la rֳ©cupֳ©ration des statistiques: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/parse', methods=['POST'])
    def parse_file():
        """Parse et importe un fichier de donnֳ©es (multi-client)"""
        logger.info("Dֳ©but du traitement de la requֳ×te d'import")
        try:
            if 'file' not in request.files:
                return jsonify({"error": "Aucun fichier fourni"}), 400
                
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "Nom de fichier invalide"}), 400

            # MULTI-CLIENT: Rֳ©cupֳ©rer le client (par dֳ©faut EOS)
            from client_utils import get_client_or_default, get_import_profile_for_client
            
            client_id = request.form.get('client_id', type=int)
            client_code = request.form.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id, client_code=client_code)
            if not client:
                return jsonify({"error": "Client introuvable"}), 404
            
            logger.info(f"Import pour le client: {client.code} (ID: {client.id})")

            # Vֳ©rifier si le fichier existe dֳ©jֳ  pour ce client
            existing_file = Fichier.query.filter_by(
                nom=file.filename,
                client_id=client.id
            ).first()
            
            if existing_file:
                logger.warning(f"Fichier dֳ©jֳ  existant dֳ©tectֳ©: '{existing_file.nom}' (ID: {existing_file.id}, date: {existing_file.date_upload})")
                return jsonify({
                    "status": "file_exists",
                    "message": "Ce fichier existe dֳ©jֳ  pour ce client. Voulez-vous le remplacer ?",
                    "existing_file_info": {
                        "nom": existing_file.nom,
                        "date_upload": existing_file.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                        "nombre_donnees": Donnee.query.filter_by(
                            fichier_id=existing_file.id,
                            client_id=client.id
                        ).count()
                    }
                }), 409

            # Rֳ©cupֳ©rer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reֳ§ue: {date_butoir}")
                except ValueError:
                    logger.warning(f"Format de date butoir invalide: {date_butoir_str}")

            # Lire le contenu du fichier
            content = file.read()
            if not content:
                return jsonify({"error": "Fichier vide"}), 400

            # Dֳ©terminer le type de fichier (base)
            file_extension = file.filename.lower().split('.')[-1]
            base_file_type = 'EXCEL' if file_extension in ['xlsx', 'xls'] else 'TXT_FIXED'
            excel_sheet_names = None

            if base_file_type == 'EXCEL':
                try:
                    excel_sheet_names = pd.ExcelFile(io.BytesIO(content)).sheet_names
                    logger.info(f"Feuilles Excel dֳ©tectֳ©es: {excel_sheet_names}")
                except Exception as sheet_err:
                    logger.warning(
                        f"Impossible d'inspecter les feuilles Excel pour le choix du profil: {sheet_err}"
                    )
                    excel_sheet_names = None

            # Rֳ©cupֳ©rer le profil d'import pour ce client
            # MULTI-CLIENT: On cherche d'abord s'il y a un profil spֳ©cifique comme EXCEL_VERTICAL
            import_profile = None
            if base_file_type == 'EXCEL':
                import_profile = get_import_profile_for_client(
                    client.id,
                    'EXCEL_VERTICAL',
                    filename=file.filename,
                    sheet_names=excel_sheet_names
                )
            
            # Sinon on prend le profil standard
            if not import_profile:
                import_profile = get_import_profile_for_client(
                    client.id,
                    base_file_type,
                    filename=file.filename,
                    sheet_names=excel_sheet_names
                )

            if not import_profile:
                logger.error(f"Aucun profil d'import trouvֳ© pour le client {client.code} (Extension: {file_extension})")
                return jsonify({
                    "error": f"Aucun profil d'import configurֳ© pour ce type de fichier ({file_extension})"
                }), 400

            try:
                # Crֳ©er le fichier en base
                nouveau_fichier = Fichier(
                    nom=file.filename,
                    client_id=client.id
                )
                db.session.add(nouveau_fichier)
                db.session.commit()
                logger.info(f"Fichier crֳ©ֳ© avec ID: {nouveau_fichier.id} pour client {client.code}")

                # Utiliser le moteur d'import gֳ©nֳ©rique
                from import_engine import ImportEngine
                
                engine = ImportEngine(import_profile, filename=file.filename)
                parsed_records = engine.parse_content(content)
                
                if not parsed_records:
                    db.session.delete(nouveau_fichier)
                    db.session.commit()
                    return jsonify({"error": "Aucun enregistrement valide trouvֳ©"}), 400
                
                # Crֳ©er les instances Donnee
                created_count = 0
                contestation_identity_matches = []
                for record in parsed_records:
                    try:
                        nouvelle_donnee = engine.create_donnee_from_record(
                            record,
                            fichier_id=nouveau_fichier.id,
                            client_id=client.id,
                            date_butoir=date_butoir
                        )
                        if not _clean_text_value(nouvelle_donnee.elementDemandes):
                            inferred_demandes = _infer_element_demandes_from_recherche_text(
                                getattr(nouvelle_donnee, 'recherche', None)
                            )
                            if inferred_demandes:
                                nouvelle_donnee.elementDemandes = inferred_demandes
                        db.session.add(nouvelle_donnee)
                        db.session.flush()

                        if nouvelle_donnee.typeDemande == 'CON':
                            contestation_identity = getattr(nouvelle_donnee, '_matching_identity', None) or {}
                            contestation_matches = getattr(nouvelle_donnee, '_matching_enquetes', []) or []
                            contestation_identity_matches.append({
                                'contestation_id': nouvelle_donnee.id,
                                'contestation_numeroDossier': nouvelle_donnee.numeroDossier,
                                'identity': contestation_identity,
                                'matches_count': len(contestation_matches),
                                'matches': contestation_matches
                            })
                        
                        # Crֳ©er DonneeEnqueteur vide si contestation (sans recopier l'original depuis donnees_enqueteur)
                        if nouvelle_donnee.typeDemande == 'CON':
                            donnee_enqueteur = DonneeEnqueteur.query.filter_by(
                                donnee_id=nouvelle_donnee.id
                            ).first()

                            if not donnee_enqueteur:
                                donnee_enqueteur = DonneeEnqueteur(
                                    donnee_id=nouvelle_donnee.id,
                                    client_id=client.id
                                )
                                db.session.add(donnee_enqueteur)
                            _hydrate_imported_contestation_fields(nouvelle_donnee, donnee_enqueteur, record)
                        
                        # Crֳ©er PartnerCaseRequest si PARTNER et demandes dֳ©tectֳ©es
                        if hasattr(nouvelle_donnee, '_pending_requests') and nouvelle_donnee._pending_requests:
                            from models.partner_models import PartnerCaseRequest
                            for request_code in nouvelle_donnee._pending_requests:
                                case_request = PartnerCaseRequest(
                                    donnee_id=nouvelle_donnee.id,
                                    request_code=request_code,
                                    requested=True,
                                    found=False,
                                    status='NEG'  # Par dֳ©faut NEG, sera recalculֳ© lors de l'update
                                )
                                db.session.add(case_request)
                            logger.info(f"ג“ {len(nouvelle_donnee._pending_requests)} demandes crֳ©ֳ©es pour {nouvelle_donnee.numeroDossier}")
                        
                        created_count += 1
                        
                    except Exception as e:
                        logger.error(f"Erreur crֳ©ation donnֳ©e: {e}")
                        continue
                
                db.session.commit()
                logger.info(f"{created_count} enregistrements crֳ©ֳ©s avec succֳ¨s")
                total_identity_matches = sum(
                    item.get('matches_count', 0) for item in contestation_identity_matches
                )
                
                return jsonify({
                    "message": "Fichier traitֳ© avec succֳ¨s",
                    "file_id": nouveau_fichier.id,
                    "client_code": client.code,
                    "records_processed": created_count,
                    "contestation_identity_matches": contestation_identity_matches,
                    "contestation_identity_matches_count": total_identity_matches
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

            # MULTI-CLIENT: Rֳ©cupֳ©rer le client
            from client_utils import get_client_or_default
            
            client_id = request.form.get('client_id', type=int)
            client_code = request.form.get('client_code', type=str)
            
            client = get_client_or_default(client_id=client_id, client_code=client_code)
            if not client:
                return jsonify({"error": "Client introuvable"}), 404

            # Rֳ©cupֳ©rer la date butoir si fournie
            date_butoir_str = request.form.get('date_butoir')
            date_butoir = None
            if date_butoir_str:
                try:
                    date_butoir = datetime.strptime(date_butoir_str, '%Y-%m-%d').date()
                    logger.info(f"Date butoir reֳ§ue pour remplacement: {date_butoir}")
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

            # Dֳ©terminer le type de fichier (base)
            file_extension = file.filename.lower().split('.')[-1]
            base_file_type = 'EXCEL' if file_extension in ['xlsx', 'xls'] else 'TXT_FIXED'
            excel_sheet_names = None

            if base_file_type == 'EXCEL':
                try:
                    excel_sheet_names = pd.ExcelFile(io.BytesIO(content)).sheet_names
                    logger.info(f"Feuilles Excel dֳ©tectֳ©es (remplacement): {excel_sheet_names}")
                except Exception as sheet_err:
                    logger.warning(
                        f"Impossible d'inspecter les feuilles Excel (remplacement): {sheet_err}"
                    )
                    excel_sheet_names = None
            
            # Rֳ©cupֳ©rer le profil d'import
            from client_utils import get_import_profile_for_client
            import_profile = None
            if base_file_type == 'EXCEL':
                import_profile = get_import_profile_for_client(
                    client.id,
                    'EXCEL_VERTICAL',
                    filename=file.filename,
                    sheet_names=excel_sheet_names
                )
                
            if not import_profile:
                import_profile = get_import_profile_for_client(
                    client.id,
                    base_file_type,
                    filename=file.filename,
                    sheet_names=excel_sheet_names
                )
                
            if not import_profile:
                return jsonify({
                    "error": f"Aucun profil d'import configurֳ© pour ce type de fichier ({file_extension})"
                }), 400

            # Crֳ©er le nouveau fichier
            nouveau_fichier = Fichier(
                nom=file.filename,
                client_id=client.id
            )
            db.session.add(nouveau_fichier)
            db.session.commit()
            
            # Utiliser le moteur d'import
            from import_engine import ImportEngine
            
            engine = ImportEngine(import_profile, filename=file.filename)
            parsed_records = engine.parse_content(content)
            
            if not parsed_records:
                db.session.delete(nouveau_fichier)
                db.session.commit()
                return jsonify({"error": "Aucun enregistrement valide trouvֳ©"}), 400
            
            # Crֳ©er les instances Donnee
            created_count = 0
            contestation_identity_matches = []
            for record in parsed_records:
                try:
                    nouvelle_donnee = engine.create_donnee_from_record(
                        record,
                        fichier_id=nouveau_fichier.id,
                        client_id=client.id,
                        date_butoir=date_butoir
                    )
                    if not _clean_text_value(nouvelle_donnee.elementDemandes):
                        inferred_demandes = _infer_element_demandes_from_recherche_text(
                            getattr(nouvelle_donnee, 'recherche', None)
                        )
                        if inferred_demandes:
                            nouvelle_donnee.elementDemandes = inferred_demandes
                    db.session.add(nouvelle_donnee)
                    db.session.flush()

                    if nouvelle_donnee.typeDemande == 'CON':
                        contestation_identity = getattr(nouvelle_donnee, '_matching_identity', None) or {}
                        contestation_matches = getattr(nouvelle_donnee, '_matching_enquetes', []) or []
                        contestation_identity_matches.append({
                            'contestation_id': nouvelle_donnee.id,
                            'contestation_numeroDossier': nouvelle_donnee.numeroDossier,
                            'identity': contestation_identity,
                            'matches_count': len(contestation_matches),
                            'matches': contestation_matches
                        })
                    
                    # Crֳ©er DonneeEnqueteur vide si contestation (sans recopier l'original depuis donnees_enqueteur)
                    if nouvelle_donnee.typeDemande == 'CON':
                        donnee_enqueteur = DonneeEnqueteur.query.filter_by(
                            donnee_id=nouvelle_donnee.id
                        ).first()

                        if not donnee_enqueteur:
                            donnee_enqueteur = DonneeEnqueteur(
                                donnee_id=nouvelle_donnee.id,
                                client_id=client.id
                            )
                            db.session.add(donnee_enqueteur)
                        _hydrate_imported_contestation_fields(nouvelle_donnee, donnee_enqueteur, record)

                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur crֳ©ation donnֳ©e: {e}")
                    continue
            
            db.session.commit()
            total_identity_matches = sum(
                item.get('matches_count', 0) for item in contestation_identity_matches
            )

            return jsonify({
                "message": "Fichier remplacֳ© avec succֳ¨s",
                "file_id": nouveau_fichier.id,
                "client_code": client.code,
                "records_processed": created_count,
                "contestation_identity_matches": contestation_identity_matches,
                "contestation_identity_matches_count": total_identity_matches
            })

        except Exception as e:
            logger.error(f"Erreur lors du remplacement: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/files/<int:file_id>', methods=['DELETE'])
    def delete_file(file_id):
        """Supprime un fichier et ses donnֳ©es associֳ©es"""
        try:
            from models.tarifs import EnqueteFacturation
            
            fichier = Fichier.query.get_or_404(file_id)
            
            # Rֳ©cupֳ©rer les IDs des donnees ֳ  supprimer
            donnee_ids = [d.id for d in Donnee.query.filter_by(fichier_id=file_id).all()]
            
            if donnee_ids:
                # 1. Supprimer d'abord les facturations liֳ©es
                EnqueteFacturation.query.filter(
                    EnqueteFacturation.donnee_id.in_(donnee_ids)
                ).delete(synchronize_session=False)
                
                # 2. Supprimer les donnֳ©es enquֳ×teur liֳ©es
                DonneeEnqueteur.query.filter(
                    DonneeEnqueteur.donnee_id.in_(donnee_ids)
                ).delete(synchronize_session=False)
                
                # 3. Supprimer les donnֳ©es
                Donnee.query.filter_by(fichier_id=file_id).delete()
            
            # 4. Supprimer le fichier
            db.session.delete(fichier)
            db.session.commit()
            
            logger.info(f"Fichier {file_id} supprimֳ© avec {len(donnee_ids)} enquֳ×tes associֳ©es")
            return jsonify({"message": "Fichier supprimֳ© avec succֳ¨s"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/search-forget-yoann', methods=['GET'])
    def search_forget_yoann():
        """Route temporaire pour chercher FORGET YOANN"""
        try:
            from models.enqueteur import Enqueteur
            
            # Chercher toutes les enquֳ×tes avec FORGET ou YOANN
            enquetes = Donnee.query.filter(
                db.or_(
                    Donnee.nom.ilike('%FORGET%'),
                    Donnee.prenom.ilike('%YOANN%'),
                    Donnee.nom.ilike('%YOANN%')
                )
            ).order_by(Donnee.id.desc()).all()
            
            results = []
            for enq in enquetes:
                enqueteur_info = "Non assignֳ©"
                if enq.enqueteurId:
                    enqueteur = db.session.get(Enqueteur, enq.enqueteurId)
                    if enqueteur:
                        enqueteur_info = f"{enqueteur.prenom} {enqueteur.nom}"
                
                enquete_originale_info = None
                if enq.est_contestation and enq.enquete_originale_id:
                    original = db.session.get(Donnee, enq.enquete_originale_id)
                    if original:
                        enq_orig_nom = "Non assignֳ©"
                        if original.enqueteurId:
                            enq_orig = db.session.get(Enqueteur, original.enqueteurId)
                            if enq_orig:
                                enq_orig_nom = f"{enq_orig.prenom} {enq_orig.nom}"
                        
                        enquete_originale_info = {
                            'id': original.id,
                            'numeroDossier': original.numeroDossier,
                            'nom': original.nom,
                            'prenom': original.prenom,
                            'enqueteur': enq_orig_nom,
                            'adresse': original.adresse1,
                            'ville': original.ville
                        }
                
                results.append({
                    'id': enq.id,
                    'numeroDossier': enq.numeroDossier,
                    'nom': enq.nom,
                    'prenom': enq.prenom,
                    'typeDemande': enq.typeDemande,
                    'est_contestation': enq.est_contestation,
                    'enqueteur': enqueteur_info,
                    'statut': enq.statut_validation,
                    'client_id': enq.client_id,
                    'adresse': enq.adresse1,
                    'ville': enq.ville,
                    'enquete_originale': enquete_originale_info
                })
            
            return jsonify({
                'success': True,
                'count': len(results),
                'data': results
            })
        except Exception as e:
            logger.error(f"Erreur recherche FORGET YOANN: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/fix-missing-numerodossier', methods=['POST'])
    def fix_missing_numerodossier():
        """Route temporaire pour corriger les numeroDossier manquants"""
        try:
            # Trouver toutes les contestations SANS numeroDossier
            contestations_sans_numero = Donnee.query.filter(
                Donnee.est_contestation == True,
                db.or_(
                    Donnee.numeroDossier == None,
                    Donnee.numeroDossier == '',
                    Donnee.numeroDossier == 'None'
                )
            ).all()
            
            if not contestations_sans_numero:
                return jsonify({
                    'success': True,
                    'message': 'Toutes les contestations ont dֳ©jֳ  un numeroDossier',
                    'count': 0
                })
            
            fixed = []
            for contestation in contestations_sans_numero:
                nouveau_numero = f"CON-{contestation.id}"
                ancien = contestation.numeroDossier
                contestation.numeroDossier = nouveau_numero
                fixed.append({
                    'id': contestation.id,
                    'nom': contestation.nom,
                    'prenom': contestation.prenom,
                    'ancien': ancien,
                    'nouveau': nouveau_numero
                })
            
            db.session.commit()
            logger.info(f"ג“ {len(fixed)} numeroDossier assignֳ©s")
            
            return jsonify({
                'success': True,
                'message': f'{len(fixed)} numeroDossier assignֳ©s avec succֳ¨s',
                'count': len(fixed),
                'fixed': fixed
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la correction des numeroDossier: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/compare-excel-imports', methods=['GET'])
    def compare_excel_imports():
        """Compare les imports Excel avec la base de donnees"""
        try:
            from models.models_enqueteur import DonneeEnqueteur
            
            # 1. Nombre total d'enquetes PARTNER archivees dans la base
            partner_client = db.session.execute(
                db.text("SELECT id FROM clients WHERE code = 'PARTNER'")
            ).fetchone()
            
            if not partner_client:
                return jsonify({'error': 'Client PARTNER non trouve'}), 404
            
            client_id = partner_client[0]
            
            # Total enquetes archivees
            total_archives = Donnee.query.filter_by(
                client_id=client_id,
                est_contestation=False,
                statut_validation='archive'
            ).count()
            
            # Enquetes avec donnees enqueteur
            archives_avec_results = db.session.query(Donnee).join(
                DonneeEnqueteur,
                Donnee.id == DonneeEnqueteur.donnee_id
            ).filter(
                Donnee.client_id == client_id,
                Donnee.est_contestation == False,
                Donnee.statut_validation == 'archive',
                DonneeEnqueteur.code_resultat.isnot(None)
            ).count()
            
            # Enquetes SANS donnees enqueteur
            archives_sans_results = total_archives - archives_avec_results
            
            # Valeur connue des fichiers Excel
            excel_count = 17838
            
            return jsonify({
                'success': True,
                'excel': {
                    'total_enquetes': excel_count,
                    'description': 'Nombre total dans les fichiers CR backup'
                },
                'database': {
                    'total_archives': total_archives,
                    'avec_resultats': archives_avec_results,
                    'sans_resultats': archives_sans_results
                },
                'difference': {
                    'manquantes': excel_count - total_archives,
                    'pourcentage_importe': round((total_archives / excel_count) * 100, 2) if excel_count > 0 else 0,
                    'pourcentage_avec_resultats': round((archives_avec_results / total_archives) * 100, 2) if total_archives > 0 else 0
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/import-missing-cr', methods=['POST'])
    def import_missing_cr():
        """Importe les enquetes CR manquantes depuis le backup"""
        try:
            from models.models_enqueteur import DonneeEnqueteur
            from datetime import datetime as dt
            
            CR_FOLDER = r"d:\EOS\reponses_cr backup"
            
            # Get PARTNER client
            partner_client = db.session.execute(
                db.text("SELECT id FROM clients WHERE code = 'PARTNER'")
            ).fetchone()
            
            if not partner_client:
                return jsonify({'error': 'Client PARTNER non trouve'}), 404
            
            client_id = partner_client[0]
            
            # Creer ou recuperer le fichier d'import pour ces enquetes
            fichier_import = db.session.execute(db.text("""
                SELECT id FROM fichiers 
                WHERE nom = 'Import CR Backup' 
                AND client_id = :client_id
            """), {'client_id': client_id}).fetchone()
            
            if not fichier_import:
                result_fichier = db.session.execute(db.text("""
                    INSERT INTO fichiers (nom, client_id, date_upload)
                    VALUES ('Import CR Backup', :client_id, NOW())
                    RETURNING id
                """), {'client_id': client_id})
                fichier_id = result_fichier.fetchone()[0]
                db.session.commit()
                logger.info(f"Fichier d'import cree: ID {fichier_id}")
            else:
                fichier_id = fichier_import[0]
                logger.info(f"Fichier d'import existant: ID {fichier_id}")
            
            # IMPORTANT: Pour PARTNER, l'identifiant unique est nom+prenom+dateNaissance
            # PAS le numeroDossier qui se repete dans chaque fichier Excel
            result = db.session.execute(db.text("""
                SELECT DISTINCT 
                    UPPER(TRIM(nom)) || '|' || UPPER(TRIM(prenom)) || '|' || COALESCE("dateNaissance"::text, '')
                FROM donnees 
                WHERE client_id = :client_id 
                AND est_contestation = false
                AND statut_validation = 'archive'
            """), {'client_id': client_id})
            # IMPORTANT: Pour PARTNER, l'identifiant unique est nom+prenom+dateNaissance
            # PAS le numeroDossier qui se repete dans chaque fichier Excel
            result = db.session.execute(db.text("""
                SELECT DISTINCT 
                    UPPER(TRIM(nom)) || '|' || UPPER(TRIM(prenom)) || '|' || COALESCE("dateNaissance"::text, '')
                FROM donnees 
                WHERE client_id = :client_id 
                AND est_contestation = false
                AND statut_validation = 'archive'
            """), {'client_id': client_id})
            
            personnes_existantes = {row[0] for row in result.fetchall()}
            logger.info(f"Personnes deja en base: {len(personnes_existantes)}")
            
            # Parcourir les fichiers Excel
            enquetes_a_importer = []
            fichiers_traites = 0
            
            for filename in sorted(os.listdir(CR_FOLDER)):
                if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
                    continue
                
                filepath = os.path.join(CR_FOLDER, filename)
                
                try:
                    df = pd.read_excel(filepath)
                    
                    if 'NUM' not in df.columns:
                        continue
                    
                    fichiers_traites += 1
                    
                    for idx, row in df.iterrows():
                        # Convertir dates
                        def conv_date(val):
                            if pd.isna(val):
                                return None
                            if isinstance(val, str):
                                for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
                                    try:
                                        return dt.strptime(val, fmt).date()
                                    except:
                                        continue
                            elif hasattr(val, 'date'):
                                return val.date()
                            return None
                        
                        nom = str(row.get('NOM', '')).strip().upper() if pd.notna(row.get('NOM')) else ''
                        prenom = str(row.get('PRENOM', '')).strip().upper() if pd.notna(row.get('PRENOM')) else ''
                        date_naissance = conv_date(row.get('DATE NAISSANCE'))
                        
                        if not nom:
                            continue
                        
                        # Crֳ©er la clֳ© unique
                        personne_key = f"{nom}|{prenom}|{date_naissance if date_naissance else ''}"
                        
                        if personne_key in personnes_existantes:
                            continue
                        
                        # Convertir code resultat (POS -> P, NEG -> N, etc.)
                        code_res_raw = str(row.get('Resultat', 'P'))[:10] if pd.notna(row.get('Resultat')) else 'P'
                        # Mapper les codes longs vers codes courts
                        code_resultat_map = {
                            'POS': 'P', 'POSITIF': 'P',
                            'NEG': 'N', 'NEGATIF': 'N',
                            'HOM': 'H', 'HOMONYME': 'H',
                            'IMP': 'I', 'IMPOSSIBLE': 'I',
                            'DEC': 'Z', 'DECES': 'Z',
                            'PART': 'Y', 'PARTIEL': 'Y'
                        }
                        code_resultat = code_resultat_map.get(code_res_raw.upper(), code_res_raw[0] if code_res_raw else 'P')
                        
                        enquete = {
                            'numeroDossier': str(row.get('NUM', '')) if pd.notna(row.get('NUM')) else None,
                            'nom': nom,
                            'prenom': prenom,
                            'dateNaissance': date_naissance,
                            'lieuNaissance': str(row.get('LIEU NAISSANCE', '')).strip().upper() if pd.notna(row.get('LIEU NAISSANCE')) else '',
                            'adresse1': str(row.get('ADR1', ''))[:255] if pd.notna(row.get('ADR1')) else None,
                            'adresse2': str(row.get('ADR2', ''))[:255] if pd.notna(row.get('ADR2')) else None,
                            'adresse3': str(row.get('ADR3', ''))[:255] if pd.notna(row.get('ADR3')) else None,
                            'codePostal': str(row.get('CP', ''))[:20] if pd.notna(row.get('CP')) else None,
                            'ville': str(row.get('VILLE', '')).strip().upper() if pd.notna(row.get('VILLE')) else '',
                            'paysResidence': str(row.get('PAYS', 'FRANCE')).strip().upper(),
                            'telephonePersonnel': str(row.get('TEL', ''))[:50] if pd.notna(row.get('TEL')) else None,
                            'typeDemande': str(row.get('TD', 'REL'))[:3] if pd.notna(row.get('TD')) else 'REL',
                            'elementDemandes': str(row.get('Elem', 'A'))[:50] if pd.notna(row.get('Elem')) else 'A',
                            'code_resultat': code_resultat,
                            'elements_retrouves': str(row.get('Elem trouvֳ©', ''))[:255] if pd.notna(row.get('Elem trouvֳ©')) else None,
                            'date_retour': conv_date(row.get('Dat retour')),
                            'nom_employeur': str(row.get('Employeur', ''))[:255] if pd.notna(row.get('Employeur')) else None,
                            'adresse1_employeur': str(row.get('ADR EMPL1', ''))[:255] if pd.notna(row.get('ADR EMPL1')) else None,
                            'adresse2_employeur': str(row.get('ADR EMPL2', ''))[:255] if pd.notna(row.get('ADR EMPL2')) else None,
                            'adresse3_employeur': str(row.get('ADR EMPL3', ''))[:255] if pd.notna(row.get('ADR EMPL3')) else None,
                            'code_postal_employeur': str(row.get('CP EMPL', ''))[:20] if pd.notna(row.get('CP EMPL')) else None,
                            'ville_employeur': str(row.get('VIL EMPL', ''))[:255] if pd.notna(row.get('VIL EMPL')) else None,
                            'telephone_employeur': str(row.get('TEL EMPL', ''))[:50] if pd.notna(row.get('TEL EMPL')) else None,
                            'banque_domiciliation': str(row.get('Banque', ''))[:255] if pd.notna(row.get('Banque')) else None,
                            'code_banque': str(row.get('CB', ''))[:20] if pd.notna(row.get('CB')) else None,
                            'code_guichet': str(row.get('CG', ''))[:20] if pd.notna(row.get('CG')) else None,
                            'libelle_guichet': str(row.get('Lib Guichet', ''))[:255] if pd.notna(row.get('Lib Guichet')) else None,
                            'titulaire_compte': str(row.get('Tit. compte', ''))[:255] if pd.notna(row.get('Tit. compte')) else None,
                            'memo1': str(row.get('MEMO1', ''))[:1000] if pd.notna(row.get('MEMO1')) else None,
                            'memo2': str(row.get('MEMO2', ''))[:1000] if pd.notna(row.get('MEMO2')) else None,
                            'memo3': str(row.get('MEMO3', ''))[:1000] if pd.notna(row.get('MEMO3')) else None,
                            'memo4': str(row.get('MEMO4', ''))[:1000] if pd.notna(row.get('MEMO4')) else None,
                            'memo5': str(row.get('MEMO5', ''))[:1000] if pd.notna(row.get('MEMO5')) else None,
                        }
                        
                        enquetes_a_importer.append(enquete)
                        personnes_existantes.add(personne_key)
                
                except Exception as e:
                    logger.warning(f"Erreur fichier {filename}: {e}")
                    continue
            
            logger.info(f"Fichiers traites: {fichiers_traites}, enquetes a importer: {len(enquetes_a_importer)}")
            
            if len(enquetes_a_importer) == 0:
                return jsonify({
                    'success': True,
                    'message': 'Toutes les enquetes sont deja en base',
                    'count': 0
                })
            
            # Import par lots
            batch_size = 50
            imported_count = 0
            errors = []
            
            for i in range(0, len(enquetes_a_importer), batch_size):
                batch = enquetes_a_importer[i:i+batch_size]
                
                try:
                    for enq in batch:
                        # Inserer donnee
                        nouvelle_donnee = Donnee(
                            client_id=client_id,
                            fichier_id=fichier_id,
                            numeroDossier=enq['numeroDossier'],
                            nom=enq['nom'],
                            prenom=enq['prenom'],
                            dateNaissance=enq['dateNaissance'],
                            lieuNaissance=enq['lieuNaissance'],
                            adresse1=enq['adresse1'],
                            adresse2=enq['adresse2'],
                            adresse3=enq['adresse3'],
                            codePostal=enq['codePostal'],
                            ville=enq['ville'],
                            paysResidence=enq['paysResidence'],
                            telephonePersonnel=enq['telephonePersonnel'],
                            typeDemande=enq['typeDemande'],
                            elementDemandes=enq['elementDemandes'],
                            est_contestation=False,
                            statut_validation='archive'
                        )
                        db.session.add(nouvelle_donnee)
                        db.session.flush()
                        
                        # Inserer donnee enqueteur
                        nouvelle_donnee_enq = DonneeEnqueteur(
                            client_id=client_id,
                            donnee_id=nouvelle_donnee.id,
                            code_resultat=enq['code_resultat'],
                            elements_retrouves=enq['elements_retrouves'],
                            date_retour=enq['date_retour'],
                            nom_employeur=enq['nom_employeur'],
                            adresse1_employeur=enq['adresse1_employeur'],
                            adresse2_employeur=enq['adresse2_employeur'],
                            adresse3_employeur=enq['adresse3_employeur'],
                            code_postal_employeur=enq['code_postal_employeur'],
                            ville_employeur=enq['ville_employeur'],
                            telephone_employeur=enq['telephone_employeur'],
                            banque_domiciliation=enq['banque_domiciliation'],
                            code_banque=enq['code_banque'],
                            code_guichet=enq['code_guichet'],
                            libelle_guichet=enq['libelle_guichet'],
                            titulaire_compte=enq['titulaire_compte'],
                            memo1=enq['memo1'],
                            memo2=enq['memo2'],
                            memo3=enq['memo3'],
                            memo4=enq['memo4'],
                            memo5=enq['memo5']
                        )
                        db.session.add(nouvelle_donnee_enq)
                        imported_count += 1
                    
                    db.session.commit()
                    logger.info(f"Lot {i//batch_size + 1}: {len(batch)} enquetes importees")
                
                except Exception as e:
                    db.session.rollback()
                    error_msg = f"Erreur lot {i//batch_size + 1}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            return jsonify({
                'success': True,
                'message': f'{imported_count} enquetes importees avec succes',
                'count': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur import CR: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/analyze-imports', methods=['GET'])
    def analyze_imports():
        """Analyse la structure des imports en base"""
        try:
            # Sample from database
            result = db.session.execute(db.text("""
                SELECT 
                    d.id,
                    d."numeroDossier",
                    d.nom,
                    d.prenom,
                    d."typeDemande",
                    d.statut_validation,
                    d.est_contestation,
                    c.code as client_code
                FROM donnees d
                JOIN clients c ON d.client_id = c.id
                WHERE c.code = 'PARTNER'
                AND d.est_contestation = false
                AND d.statut_validation = 'archive'
                ORDER BY d.id
                LIMIT 20
            """))
            
            samples = []
            for row in result.fetchall():
                samples.append({
                    'id': row[0],
                    'numeroDossier': row[1],
                    'nom': row[2],
                    'prenom': row[3],
                    'typeDemande': row[4],
                    'statut': row[5],
                    'contestation': row[6],
                    'client': row[7]
                })
            
            return jsonify({
                'success': True,
                'count': len(samples),
                'samples': samples
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/clean-all-donnees', methods=['POST'])
    def clean_all_donnees():
        """DANGER: Vide toutes les donnees de la table donnees"""
        try:
            # Compter avant suppression
            count_donnees = db.session.execute(db.text("SELECT COUNT(*) FROM donnees")).scalar()
            count_enqueteur = db.session.execute(db.text("SELECT COUNT(*) FROM donnees_enqueteur")).scalar()
            count_facturation = db.session.execute(db.text("SELECT COUNT(*) FROM enquete_facturation")).scalar()
            
            logger.warning(f"SUPPRESSION EN COURS: {count_donnees} donnees, {count_enqueteur} donnees_enqueteur, {count_facturation} facturations")
            
            # Supprimer dans l'ordre (contraintes FK)
            db.session.execute(db.text("DELETE FROM enquete_facturation"))
            db.session.execute(db.text("DELETE FROM donnees_enqueteur"))
            db.session.execute(db.text("DELETE FROM enquete_archives"))
            db.session.execute(db.text("DELETE FROM donnees"))
            
            db.session.commit()
            
            logger.warning(f"SUPPRESSION TERMINEE: {count_donnees} donnees supprimees")
            
            return jsonify({
                'success': True,
                'message': 'Toutes les donnees ont ete supprimees',
                'deleted': {
                    'donnees': count_donnees,
                    'donnees_enqueteur': count_enqueteur,
                    'facturations': count_facturation
                }
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur suppression: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/verify-import', methods=['GET'])
    def verify_import():
        """Verifie l'import par client"""
        try:
            # Compter par client
            result = db.session.execute(db.text("""
                SELECT 
                    c.id as client_id,
                    c.code as client_code,
                    c.nom as client_nom,
                    COUNT(d.id) as nb_enquetes,
                    COUNT(de.id) as nb_donnees_enqueteur
                FROM clients c
                LEFT JOIN donnees d ON d.client_id = c.id
                LEFT JOIN donnees_enqueteur de ON de.donnee_id = d.id
                GROUP BY c.id, c.code, c.nom
                ORDER BY nb_enquetes DESC
            """))
            
            clients = []
            for row in result.fetchall():
                clients.append({
                    'client_id': row[0],
                    'code': row[1],
                    'nom': row[2],
                    'nb_enquetes': row[3],
                    'nb_donnees_enqueteur': row[4]
                })
            
            # Exemple d'enquete
            sample = db.session.execute(db.text("""
                SELECT id, client_id, "numeroDossier", nom, prenom, ville, "codePostal"
                FROM donnees
                ORDER BY id
                LIMIT 5
            """)).fetchall()
            
            samples = []
            for row in sample:
                samples.append({
                    'id': row[0],
                    'client_id': row[1],
                    'numeroDossier': row[2],
                    'nom': row[3],
                    'prenom': row[4],
                    'ville': row[5],
                    'codePostal': row[6]
                })
            
            return jsonify({
                'success': True,
                'clients': clients,
                'samples': samples
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/analyze-enquete/<int:enquete_id>', methods=['GET'])
    def analyze_enquete(enquete_id):
        """Analyse complete d'une enquete avec toutes ses donnees"""
        try:
            result = db.session.execute(db.text("""
                SELECT 
                    d.id, d.client_id, d.fichier_id, d."numeroDossier",
                    d.nom, d.prenom, d."dateNaissance", d."lieuNaissance",
                    d.adresse1, d.adresse2, d.adresse3, d."codePostal", d.ville,
                    d."paysResidence", d."telephonePersonnel", d."typeDemande",
                    d."elementDemandes", d.statut_validation, d.est_contestation,
                    de.code_resultat, de.elements_retrouves, de.date_retour,
                    de.nom_employeur, de.adresse1_employeur, de.code_postal_employeur,
                    de.ville_employeur, de.telephone_employeur, de.banque_domiciliation,
                    de.code_banque, de.code_guichet, de.libelle_guichet,
                    de.titulaire_compte, de.memo1, de.memo2, de.memo3, de.memo4, de.memo5
                FROM donnees d
                LEFT JOIN donnees_enqueteur de ON de.donnee_id = d.id
                WHERE d.id = :enquete_id
            """), {'enquete_id': enquete_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'success': False, 'error': 'Enquete non trouvee'}), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'table_donnees': {
                        'id': row[0], 'client_id': row[1], 'fichier_id': row[2], 'numeroDossier': row[3],
                        'nom': row[4], 'prenom': row[5], 'dateNaissance': str(row[6]) if row[6] else None,
                        'lieuNaissance': row[7], 'adresse1': row[8], 'adresse2': row[9], 'adresse3': row[10],
                        'codePostal': row[11], 'ville': row[12], 'paysResidence': row[13],
                        'telephonePersonnel': row[14], 'typeDemande': row[15], 'elementDemandes': row[16],
                        'statut_validation': row[17], 'est_contestation': row[18]
                    },
                    'table_donnees_enqueteur': {
                        'code_resultat': row[19], 'elements_retrouves': row[20],
                        'date_retour': str(row[21]) if row[21] else None, 'nom_employeur': row[22],
                        'adresse1_employeur': row[23], 'code_postal_employeur': row[24],
                        'ville_employeur': row[25], 'telephone_employeur': row[26],
                        'banque_domiciliation': row[27], 'code_banque': row[28], 'code_guichet': row[29],
                        'libelle_guichet': row[30], 'titulaire_compte': row[31],
                        'memo1': row[32], 'memo2': row[33], 'memo3': row[34], 'memo4': row[35], 'memo5': row[36]
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/contestations/<int:enquete_id>', methods=['GET'])
    def get_contestation_details(enquete_id):
        """Rֳ©cupֳ¨re les dֳ©tails d'une contestation"""
        try:
            donnee = Donnee.query.get_or_404(enquete_id)
            
            if donnee.typeDemande != 'CON':
                return jsonify({
                    'success': False,
                    'error': 'Cette enquֳ×te n\'est pas une contestation'
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
        """Corrige les associations enquֳ×teur-facturation"""
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
                donnee.enqueteurId = 1  # Assigner ֳ  l'enquֳ×teur par dֳ©faut
                fixed_count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Corrections effectuֳ©es: {fixed_count} facturations',
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
        """Rֳ©cupֳ¨re les tarifs pour un client spֳ©cifique"""
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
        """Crֳ©e un nouveau tarif client"""
        try:
            from models.tarifs import TarifClient
            data = request.json
            
            # Vֳ©rifier si le tarif existe dֳ©jֳ 
            existing = TarifClient.query.filter_by(
                client_id=data['client_id'],
                code_lettre=data['code_lettre'],
                actif=True
            ).first()
            
            if existing:
                return jsonify({
                    "success": False,
                    "error": f"Le tarif {data['code_lettre']} existe dֳ©jֳ  pour ce client"
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
        """Met ֳ  jour un tarif client"""
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
        """Dֳ©sactive un tarif client (soft delete)"""
        try:
            from models.tarifs import TarifClient
            tarif = TarifClient.query.get_or_404(tarif_id)
            
            tarif.actif = False
            tarif.date_fin = datetime.now().date()
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Tarif dֳ©sactivֳ© avec succֳ¨s"
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur delete_tarif_client: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===========================
    # Routes pour les options de confirmation personnalisֳ©es
    # ===========================
    @app.route('/api/confirmation-options/<int:client_id>', methods=['GET'])
    def get_confirmation_options(client_id):
        """Rֳ©cupֳ¨re les options de confirmation pour un client"""
        try:
            from models.confirmation_options import ConfirmationOption
            
            # Options prֳ©dֳ©finies de base
            options_base = [
                'Confirmֳ© par la mairie',
                'En proximitֳ©',
                'Confirmֳ© par tֳ©lֳ©phone',
                'Confirmֳ© par voisinage',
                'Confirmֳ© par famille',
                "Confirmֳ© par l'employeur",
                'Confirmֳ© par courrier',
                'Confirmֳ© sur place'
            ]
            
            # Options personnalisֳ©es du client (la table peut ne pas exister)
            options_custom_list = []
            try:
                options_custom = ConfirmationOption.query.filter_by(
                    client_id=client_id
                ).order_by(ConfirmationOption.usage_count.desc()).all()
                options_custom_list = [opt.option_text for opt in options_custom]
            except Exception:
                pass  # Table confirmation_options supprimֳ©e par migration, on continue avec les options de base

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
            
            # Vֳ©rifier si l'option existe dֳ©jֳ 
            existing = ConfirmationOption.query.filter_by(
                client_id=client_id,
                option_text=option_text
            ).first()
            
            if existing:
                # Incrֳ©menter le compteur d'utilisation
                existing.usage_count += 1
                existing.updated_at = datetime.now()
                db.session.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Option existante, compteur incrֳ©mentֳ©",
                    "option": existing.to_dict()
                })
            else:
                # Crֳ©er une nouvelle option
                new_option = ConfirmationOption(
                    client_id=client_id,
                    option_text=option_text,
                    usage_count=1
                )
                db.session.add(new_option)
                db.session.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Nouvelle option ajoutֳ©e",
                    "option": new_option.to_dict()
                })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur save_confirmation_option: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    logger.info("Routes legacy enregistrֳ©es")




    # ===========================
    # REMPLACER la route existante dans app.py par celle-ci:
    # ===========================

    @app.route('/api/export/sherlock', methods=['POST'])
    def export_sherlock():
        """Exporte les donnֳ©es Sherlock au format XLS vertical avec formatage"""
        try:
            from models import SherlockDonnee, Fichier
            from flask import send_file
            from datetime import datetime
            import xlwt
            import io
            import math
            
            data = request.json or {}
            client_id = data.get('client_id')
            
            # Construire la requֳ×te
            query = db.session.query(SherlockDonnee).join(
                Fichier, SherlockDonnee.fichier_id == Fichier.id
            )
            
            if client_id:
                query = query.filter(Fichier.client_id == client_id)
            
            # Rֳ©cupֳ©rer les donnֳ©es triֳ©es par ID
            items = query.order_by(SherlockDonnee.id.asc()).all()
            
            if not items:
                return jsonify({"success": False, "error": "Aucune donnֳ©e ֳ  exporter"}), 404
            
            # Mapping des champs - 65 champs (sans les tarifs)
            FIELDS_MAPPING = [
                #('DossierId', 'dossier_id', ''),
                ('Rֳ©fֳ©renceInterne', 'reference_interne', ''),
                ('EC-Nom Usage', 'ec_nom_usage', ''),
                ('EC-Prֳ©nom', 'ec_prenom', ''),
                ('EC-Nom Naissance', 'ec_nom_naissance', ''),
                ('EC-Civilitֳ©', 'ec_civilite', ''),
                ('Demande', 'demande', ''),
                ('EC-Date Naissance', 'ec_date_naissance', ''),
                ('EC-Localitֳ© Naissance', 'ec_localite_naissance', ''),
                ('Naissance CP', 'naissance_cp', ''),
                ('Client-Commentaire', 'client_commentaire', ''),
                #('EC-Prֳ©nom2', 'ec_prenom2', ''),
                #('EC-Prֳ©nom3', 'ec_prenom3', ''),
                #('EC-Prֳ©nom4', 'ec_prenom4', ''),
                #('Naissance INSEE', 'naissance_insee', ''),
                #('EC-Pays Naissance', 'ec_pays_naissance', ''),
                ('AD-L1', 'ad_l1', ''),
                ('AD-L2', 'ad_l2', ''),
                ('AD-L3', 'ad_l3', ''),
                ('AD-L4 Numֳ©ro', 'ad_l4_numero', ''),
                ('AD-L4 Type', 'ad_l4_type', ''),
                ('AD-L4 Voie', 'ad_l4_voie', ''),
                ('AD-L5', 'ad_l5', ''),
                ('AD-L6 Cedex', 'ad_l6_cedex', ''),
                ('AD-L6 CP', 'ad_l6_cp', ''),
                ('AD-L6 INSEE', 'ad_l6_insee', ''),
                ('AD-L6 Localitֳ©', 'ad_l6_localite', ''),
                ('AD-L7 Pays', 'ad_l7_pays', ''),
                ('AD-Tֳ©lֳ©phone', 'ad_telephone', ''),
                ('AD-Tֳ©lֳ©phonePro', 'ad_telephone_pro', ''),
                ('AD-Tֳ©lֳ©phoneMobile', 'ad_telephone_mobile', ''),
                ('AD-Email', 'ad_email', ''),
                #('Rֳ©sultat', 'resultat', ''),
                #('Montant HT', 'montant_ht', ''),
                # Champs de rֳ©ponse enquֳ×teur (Rֳ©p-)
                #('Rֳ©p-EC-Civilitֳ©', 'rep_ec_civilite', ''),
                #('Rֳ©p-EC-Prֳ©nom', 'rep_ec_prenom', ''),
                #('Rֳ©p-EC-Prֳ©nom2', 'rep_ec_prenom2', ''),
                #('Rֳ©p-EC-Prֳ©nom3', 'rep_ec_prenom3', ''),
                #('Rֳ©p-EC-Prֳ©nom4', 'rep_ec_prenom4', ''),
                #('Rֳ©p-EC-Nom Usage', 'rep_ec_nom_usage', ''),
                #('Rֳ©p-EC-Nom Naissance', 'rep_ec_nom_naissance', ''),
                #('Rֳ©p-EC-Date Naissance', 'rep_ec_date_naissance', ''),
                #('Rֳ©p-Naissance CP', 'rep_naissance_cp', ''),
                #('Rֳ©p-EC-Localitֳ© Naissance', 'rep_ec_localite_naissance', ''),
                #('Rֳ©p-Naissance INSEE', 'rep_naissance_insee', ''),
                #('Rֳ©p-EC-Pays Naissance', 'rep_ec_pays_naissance', ''),
                #('Rֳ©p-DCD-Date', 'rep_dcd_date', ''),
                #('Rֳ©p-DCD-Numֳ©ro_Acte', 'rep_dcd_numero_acte', ''),
                #('Rֳ©p-DCD-Localitֳ©', 'rep_dcd_localite', ''),
                #('Rֳ©p-DCD-CP', 'rep_dcd_cp', ''),
                #('Rֳ©p-DCD-INSEE', 'rep_dcd_insee', ''),
                #('Rֳ©p-DCD-Pays', 'rep_dcd_pays', ''),
                #('Rֳ©p-AD-L1', 'rep_ad_l1', ''),
                #('Rֳ©p-AD-L2', 'rep_ad_l2', ''),
                #('Rֳ©p-AD-L3', 'rep_ad_l3', ''),
                #('Rֳ©p-AD-L4 Numֳ©ro', 'rep_ad_l4_numero', ''),
                #('Rֳ©p-AD-L4 Type', 'rep_ad_l4_type', ''),
                #('Rֳ©p-AD-L4 Voie', 'rep_ad_l4_voie', ''),
                #('Rֳ©p-AD-L5', 'rep_ad_l5', ''),
                #('Rֳ©p-AD-L6 Cedex', 'rep_ad_l6_cedex', ''),
                #('Rֳ©p-AD-L6 CP', 'rep_ad_l6_cp', ''),
                #('Rֳ©p-AD-L6 INSEE', 'rep_ad_l6_insee', ''),
                #('Rֳ©p-AD-L6 Localitֳ©', 'rep_ad_l6_localite', ''),
                #('Rֳ©p-AD-L7 Pays', 'rep_ad_l7_pays', ''),
                #('Rֳ©p-AD-Tֳ©lֳ©phone', 'rep_ad_telephone', ''),
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
                """Enlֳ¨ve le .0 des nombres comme 35000.0 -> 35000"""
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
                """Rֳ©cupֳ¨re la valeur d'un champ avec formatage spֳ©cial"""
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
            
            # Crֳ©er le Workbook
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
            ws.col(0).width = 256 * 25  # Colonne A: 25 caractֳ¨res
            ws.col(1).width = 256 * 50  # Colonne B: 50 caractֳ¨res
            
            # === CONSTANTES ===
            ROWS_PER_RECORD = 75  # 65 champs + lignes de sֳ©paration
            FIELDS_COUNT = len(FIELDS_MAPPING)  # 65 champs (sans tarifs)
            ROW_HEIGHT = 300  # ~15 points
            
            # Ligne 0: En-tֳ×te vide
            ws.write(0, 0, ' ')
            ws.write(0, 1, ' ')
            ws.row(0).height_mismatch = True
            ws.row(0).height = ROW_HEIGHT
            
            # Pour chaque enregistrement
            for idx, item in enumerate(items):
                start_row = 1 + (idx * ROWS_PER_RECORD)
                
                # ֳ‰crire les 32 champs
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
                
                # Lignes vides de sֳ©paration
                for empty_idx in range(FIELDS_COUNT, ROWS_PER_RECORD - 1):
                    row = start_row + empty_idx
                    ws.write(row, 0, '')
                    ws.write(row, 1, '')
                    ws.row(row).height_mismatch = True
                    ws.row(row).height = ROW_HEIGHT
                
                # Ligne de sֳ©paration
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
            
            logger.info(f"Export Sherlock: {len(items)} enregistrements exportֳ©s avec formatage")
            
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
