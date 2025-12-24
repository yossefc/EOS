"""
Service de résolution des tarifs PARTNER (lettre + combinaisons de demandes)
"""
import logging
from models.partner_models import PartnerTarifRule, PartnerCaseRequest
from extensions import db

logger = logging.getLogger(__name__)


class PartnerTarifResolver:
    """Résout le tarif selon la lettre et les demandes"""
    
    @staticmethod
    def resolve_tarif(client_id, tarif_lettre, donnee_id):
        """
        Résout le tarif pour un dossier
        
        Args:
            client_id (int): ID du client
            tarif_lettre (str): Lettre de tarif (A, B, C, etc.)
            donnee_id (int): ID du dossier
            
        Returns:
            float or None: Montant du tarif, ou None si non trouvé
        """
        # Normaliser la lettre
        lettre = (tarif_lettre or "").strip().upper()
        if not lettre:
            logger.warning(f"Lettre de tarif vide pour donnee_id={donnee_id}")
            return None
        
        # Récupérer les demandes POS pour ce dossier
        pos_requests = PartnerCaseRequest.query.filter_by(
            donnee_id=donnee_id,
            requested=True,
            status='POS'
        ).all()
        
        if not pos_requests:
            logger.warning(f"Aucune demande POS pour donnee_id={donnee_id}, tarif=0")
            return 0.0  # Aucune demande POS = tarif 0
        
        # Construire la clé de demandes (triée)
        request_codes = [req.request_code for req in pos_requests]
        request_key = PartnerTarifRule.build_request_key(request_codes)
        
        logger.info(f"Résolution tarif: lettre={lettre}, demandes={request_key}, donnee_id={donnee_id}")
        
        # 1. Chercher une règle exacte (lettre + combinaison)
        exact_rule = PartnerTarifRule.query.filter_by(
            client_id=client_id,
            tarif_lettre=lettre,
            request_key=request_key
        ).first()
        
        if exact_rule:
            logger.info(f"  ✓ Règle exacte trouvée: {exact_rule.amount}€")
            return float(exact_rule.amount)
        
        # 2. Fallback: somme des règles unitaires
        logger.info(f"  ℹ Pas de règle exacte, calcul par somme unitaire")
        total_amount = 0.0
        found_any = False
        
        for request_code in request_codes:
            unit_rule = PartnerTarifRule.query.filter_by(
                client_id=client_id,
                tarif_lettre=lettre,
                request_key=request_code
            ).first()
            
            if unit_rule:
                total_amount += float(unit_rule.amount)
                found_any = True
                logger.info(f"    + {request_code}: {unit_rule.amount}€")
            else:
                logger.warning(f"    ⚠ Pas de règle unitaire pour {lettre} + {request_code}")
        
        if found_any:
            logger.info(f"  ✓ Total calculé: {total_amount}€")
            return total_amount
        
        # 3. Aucune règle trouvée
        logger.warning(f"  ❌ Aucune règle trouvée pour {lettre} + {request_key}")
        return None  # JAMAIS 0 silencieux
    
    @staticmethod
    def get_tarif_display(client_id, tarif_lettre, donnee_id):
        """
        Retourne le montant du tarif formaté pour l'affichage
        
        Args:
            client_id (int): ID du client
            tarif_lettre (str): Lettre de tarif
            donnee_id (int): ID du dossier
            
        Returns:
            str: Montant formaté (ex: "120.00€") ou "N/A"
        """
        amount = PartnerTarifResolver.resolve_tarif(client_id, tarif_lettre, donnee_id)
        
        if amount is None:
            return "N/A"
        
        return f"{amount:.2f}€"
    
    @staticmethod
    def get_all_tarif_rules(client_id, tarif_lettre=None):
        """
        Récupère toutes les règles de tarifs pour un client
        
        Args:
            client_id (int): ID du client
            tarif_lettre (str, optional): Filtrer par lettre
            
        Returns:
            list: Liste de PartnerTarifRule
        """
        query = PartnerTarifRule.query.filter_by(client_id=client_id)
        
        if tarif_lettre:
            lettre = tarif_lettre.strip().upper()
            query = query.filter_by(tarif_lettre=lettre)
        
        return query.order_by(
            PartnerTarifRule.tarif_lettre,
            PartnerTarifRule.request_key
        ).all()
    
    @staticmethod
    def create_or_update_rule(client_id, tarif_lettre, request_codes, amount):
        """
        Crée ou met à jour une règle de tarif
        
        Args:
            client_id (int): ID du client
            tarif_lettre (str): Lettre de tarif
            request_codes (list): Liste de codes de demandes
            amount (float): Montant
            
        Returns:
            PartnerTarifRule: Règle créée ou mise à jour
        """
        lettre = (tarif_lettre or "").strip().upper()
        if not lettre:
            raise ValueError("Lettre de tarif obligatoire")
        
        if not request_codes:
            raise ValueError("Au moins une demande requise")
        
        if amount is None or amount < 0:
            raise ValueError("Montant invalide")
        
        # Construire la clé
        request_key = PartnerTarifRule.build_request_key(request_codes)
        
        # Chercher si existe
        existing = PartnerTarifRule.query.filter_by(
            client_id=client_id,
            tarif_lettre=lettre,
            request_key=request_key
        ).first()
        
        if existing:
            # Mettre à jour
            existing.amount = amount
            db.session.commit()
            logger.info(f"Règle mise à jour: {lettre} + {request_key} = {amount}€")
            return existing
        else:
            # Créer
            rule = PartnerTarifRule(
                client_id=client_id,
                tarif_lettre=lettre,
                request_key=request_key,
                amount=amount
            )
            db.session.add(rule)
            db.session.commit()
            logger.info(f"Règle créée: {lettre} + {request_key} = {amount}€")
            return rule
    
    @staticmethod
    def delete_rule(rule_id):
        """
        Supprime une règle de tarif
        
        Args:
            rule_id (int): ID de la règle
            
        Returns:
            bool: True si supprimée
        """
        rule = db.session.get(PartnerTarifRule, rule_id)
        if not rule:
            return False
        
        logger.info(f"Suppression règle: {rule.tarif_lettre} + {rule.request_key}")
        db.session.delete(rule)
        db.session.commit()
        return True

