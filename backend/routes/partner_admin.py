"""
Routes d'administration PARTNER
Gestion des keywords, tarifs combinés et demandes par dossier
"""
import logging
from flask import Blueprint, request, jsonify
from extensions import db
from models.partner_models import PartnerRequestKeyword, PartnerTarifRule, PartnerCaseRequest
from models.client import Client
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from services.partner_request_calculator import PartnerRequestCalculator

logger = logging.getLogger(__name__)

partner_admin_bp = Blueprint('partner_admin', __name__)


# ═══════════════════════════════════════════════════════════════
# KEYWORDS (Mots-clés pour parsing RECHERCHE)
# ═══════════════════════════════════════════════════════════════

@partner_admin_bp.route('/api/partner/admin/keywords', methods=['GET'])
def get_keywords():
    """
    Récupère tous les mots-clés pour un client
    Query params: client_id (required)
    """
    try:
        client_id = request.args.get('client_id', type=int)
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id requis'}), 400
        
        keywords = PartnerRequestKeyword.query.filter_by(
            client_id=client_id
        ).order_by(
            PartnerRequestKeyword.request_code,
            PartnerRequestKeyword.priority.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'keywords': [kw.to_dict() for kw in keywords],
            'count': len(keywords)
        })
        
    except Exception as e:
        logger.error(f"Erreur get_keywords: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/keywords', methods=['POST'])
def create_keyword():
    """
    Crée un nouveau mot-clé
    Body: {client_id, request_code, pattern, is_regex?, priority?}
    """
    try:
        data = request.json
        
        # Validation
        required_fields = ['client_id', 'request_code', 'pattern']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} requis'}), 400
        
        # Vérifier que le client existe
        client = db.session.get(Client, data['client_id'])
        if not client:
            return jsonify({'success': False, 'error': 'Client introuvable'}), 404
        
        # Vérifier que request_code est valide
        valid_codes = ['ADDRESS', 'PHONE', 'EMPLOYER', 'BANK', 'BIRTH']
        if data['request_code'] not in valid_codes:
            return jsonify({
                'success': False,
                'error': f'request_code invalide. Valeurs autorisées: {valid_codes}'
            }), 400
        
        # Créer le keyword
        keyword = PartnerRequestKeyword(
            client_id=data['client_id'],
            request_code=data['request_code'],
            pattern=data['pattern'].strip(),
            is_regex=data.get('is_regex', False),
            priority=data.get('priority', 0)
        )
        
        db.session.add(keyword)
        db.session.commit()
        
        logger.info(f"Keyword créé: {keyword.request_code} - {keyword.pattern}")
        
        return jsonify({
            'success': True,
            'keyword': keyword.to_dict(),
            'message': 'Mot-clé créé avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur create_keyword: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/keywords/<int:keyword_id>', methods=['PUT'])
def update_keyword(keyword_id):
    """
    Met à jour un mot-clé
    Body: {pattern?, is_regex?, priority?}
    """
    try:
        keyword = db.session.get(PartnerRequestKeyword, keyword_id)
        if not keyword:
            return jsonify({'success': False, 'error': 'Mot-clé introuvable'}), 404
        
        data = request.json
        
        # Mise à jour des champs
        if 'pattern' in data:
            keyword.pattern = data['pattern'].strip()
        if 'is_regex' in data:
            keyword.is_regex = data['is_regex']
        if 'priority' in data:
            keyword.priority = data['priority']
        
        db.session.commit()
        
        logger.info(f"Keyword mis à jour: {keyword.id}")
        
        return jsonify({
            'success': True,
            'keyword': keyword.to_dict(),
            'message': 'Mot-clé mis à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur update_keyword: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/keywords/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    """Supprime un mot-clé"""
    try:
        keyword = db.session.get(PartnerRequestKeyword, keyword_id)
        if not keyword:
            return jsonify({'success': False, 'error': 'Mot-clé introuvable'}), 404
        
        db.session.delete(keyword)
        db.session.commit()
        
        logger.info(f"Keyword supprimé: {keyword_id}")
        
        return jsonify({
            'success': True,
            'message': 'Mot-clé supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur delete_keyword: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# TARIF RULES (Tarifs combinés)
# ═══════════════════════════════════════════════════════════════

@partner_admin_bp.route('/api/partner/admin/tarif-rules', methods=['GET'])
def get_tarif_rules():
    """
    Récupère toutes les règles de tarifs pour un client
    Query params: client_id (required), tarif_lettre? (optional filter)
    """
    try:
        client_id = request.args.get('client_id', type=int)
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id requis'}), 400
        
        query = PartnerTarifRule.query.filter_by(client_id=client_id)
        
        # Filtre optionnel par lettre
        tarif_lettre = request.args.get('tarif_lettre')
        if tarif_lettre:
            query = query.filter_by(tarif_lettre=tarif_lettre.strip().upper())
        
        rules = query.order_by(
            PartnerTarifRule.tarif_lettre,
            PartnerTarifRule.request_key
        ).all()
        
        return jsonify({
            'success': True,
            'rules': [rule.to_dict() for rule in rules],
            'count': len(rules)
        })
        
    except Exception as e:
        logger.error(f"Erreur get_tarif_rules: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/tarif-rules', methods=['POST'])
def create_tarif_rule():
    """
    Crée une nouvelle règle de tarif
    Body: {client_id, tarif_lettre, request_codes: [], amount}
    """
    try:
        data = request.json
        
        # Validation
        required_fields = ['client_id', 'tarif_lettre', 'request_codes', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} requis'}), 400
        
        # Vérifier que le client existe
        client = db.session.get(Client, data['client_id'])
        if not client:
            return jsonify({'success': False, 'error': 'Client introuvable'}), 404
        
        # Valider request_codes
        valid_codes = ['ADDRESS', 'PHONE', 'EMPLOYER', 'BANK', 'BIRTH']
        request_codes = data['request_codes']
        if not isinstance(request_codes, list) or not request_codes:
            return jsonify({'success': False, 'error': 'request_codes doit être une liste non vide'}), 400
        
        for code in request_codes:
            if code not in valid_codes:
                return jsonify({
                    'success': False,
                    'error': f'Code invalide: {code}. Valeurs autorisées: {valid_codes}'
                }), 400
        
        # Valider amount
        try:
            amount = float(data['amount'])
            if amount < 0:
                raise ValueError("Montant négatif")
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Montant invalide'}), 400
        
        # Construire request_key
        request_key = PartnerTarifRule.build_request_key(request_codes)
        
        # Vérifier si existe déjà
        lettre = data['tarif_lettre'].strip().upper()
        existing = PartnerTarifRule.query.filter_by(
            client_id=data['client_id'],
            tarif_lettre=lettre,
            request_key=request_key
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Une règle existe déjà pour {lettre} + {request_key}'
            }), 409
        
        # Créer la règle
        rule = PartnerTarifRule(
            client_id=data['client_id'],
            tarif_lettre=lettre,
            request_key=request_key,
            amount=amount
        )
        
        db.session.add(rule)
        db.session.commit()
        
        logger.info(f"Règle de tarif créée: {lettre} + {request_key} = {amount}€")
        
        return jsonify({
            'success': True,
            'rule': rule.to_dict(),
            'message': 'Règle de tarif créée avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur create_tarif_rule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/tarif-rules/<int:rule_id>', methods=['PUT'])
def update_tarif_rule(rule_id):
    """
    Met à jour une règle de tarif
    Body: {amount}
    """
    try:
        rule = db.session.get(PartnerTarifRule, rule_id)
        if not rule:
            return jsonify({'success': False, 'error': 'Règle introuvable'}), 404
        
        data = request.json
        
        # Mise à jour du montant uniquement
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount < 0:
                    raise ValueError("Montant négatif")
                rule.amount = amount
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Montant invalide'}), 400
        
        db.session.commit()
        
        logger.info(f"Règle de tarif mise à jour: {rule.id}")
        
        return jsonify({
            'success': True,
            'rule': rule.to_dict(),
            'message': 'Règle de tarif mise à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur update_tarif_rule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/admin/tarif-rules/<int:rule_id>', methods=['DELETE'])
def delete_tarif_rule(rule_id):
    """Supprime une règle de tarif"""
    try:
        rule = db.session.get(PartnerTarifRule, rule_id)
        if not rule:
            return jsonify({'success': False, 'error': 'Règle introuvable'}), 404
        
        db.session.delete(rule)
        db.session.commit()
        
        logger.info(f"Règle de tarif supprimée: {rule_id}")
        
        return jsonify({
            'success': True,
            'message': 'Règle de tarif supprimée avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur delete_tarif_rule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# CASE REQUESTS (Demandes par dossier)
# ═══════════════════════════════════════════════════════════════

@partner_admin_bp.route('/api/partner/case-requests/<int:donnee_id>', methods=['GET'])
def get_case_requests(donnee_id):
    """
    Récupère les demandes détectées pour un dossier
    """
    try:
        # Vérifier que le dossier existe
        donnee = db.session.get(Donnee, donnee_id)
        if not donnee:
            return jsonify({'success': False, 'error': 'Dossier introuvable'}), 404
        
        # Récupérer les demandes
        requests = PartnerCaseRequest.query.filter_by(
            donnee_id=donnee_id
        ).order_by(PartnerCaseRequest.request_code).all()
        
        return jsonify({
            'success': True,
            'requests': [req.to_dict() for req in requests],
            'count': len(requests)
        })
        
    except Exception as e:
        logger.error(f"Erreur get_case_requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@partner_admin_bp.route('/api/partner/case-requests/<int:donnee_id>/recalculate', methods=['POST'])
def recalculate_case_requests(donnee_id):
    """
    Recalcule les statuts POS/NEG pour toutes les demandes d'un dossier
    """
    try:
        # Vérifier que le dossier existe
        donnee = db.session.get(Donnee, donnee_id)
        if not donnee:
            return jsonify({'success': False, 'error': 'Dossier introuvable'}), 404
        
        # Utiliser la méthode statique de recalcul
        result = PartnerRequestCalculator.recalculate_all_requests(donnee_id)
        
        # Récupérer les demandes mises à jour
        requests = PartnerCaseRequest.query.filter_by(donnee_id=donnee_id).all()
        
        if not requests:
            return jsonify({'success': False, 'error': 'Aucune demande trouvée'}), 404
        
        logger.info(f"Recalcul terminé pour dossier {donnee_id}: {result['updated']} demandes mises à jour ({result['pos']} POS, {result['neg']} NEG)")
        
        return jsonify({
            'success': True,
            'requests': [req.to_dict() for req in requests],
            'updated_count': result['updated'],
            'pos_count': result['pos'],
            'neg_count': result['neg'],
            'message': f"{result['updated']} demande(s) recalculée(s) : {result['pos']} POS, {result['neg']} NEG"
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur recalculate_case_requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

@partner_admin_bp.route('/api/partner/admin/request-codes', methods=['GET'])
def get_request_codes():
    """Retourne la liste des codes de demandes valides"""
    return jsonify({
        'success': True,
        'codes': [
            {'code': 'ADDRESS', 'label': 'Adresse'},
            {'code': 'PHONE', 'label': 'Téléphone'},
            {'code': 'EMPLOYER', 'label': 'Employeur'},
            {'code': 'BANK', 'label': 'Banque'},
            {'code': 'BIRTH', 'label': 'Date et lieu de naissance'}
        ]
    })

