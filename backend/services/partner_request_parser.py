"""
Service de parsing du champ RECHERCHE pour PARTNER
Détecte les demandes sans séparateurs en utilisant les mots-clés configurés
"""
import logging
import re
import unicodedata
from models.partner_models import PartnerRequestKeyword

logger = logging.getLogger(__name__)


class PartnerRequestParser:
    """Parse le champ RECHERCHE et détecte les demandes"""
    
    @staticmethod
    def normalize_text(text):
        """
        Normalise le texte pour la recherche
        - Uppercase
        - Trim
        - Enlever les accents
        
        Args:
            text (str): Texte à normaliser
            
        Returns:
            str: Texte normalisé
        """
        if not text:
            return ""
        
        # Uppercase + trim
        text = text.upper().strip()
        
        # Enlever les accents
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        
        return text
    
    @staticmethod
    def parse_recherche(recherche_text, client_id):
        """
        Parse le champ RECHERCHE et détecte les demandes
        
        Args:
            recherche_text (str): Texte du champ RECHERCHE
            client_id (int): ID du client
            
        Returns:
            set: Ensemble de codes de demandes détectées (ex: {'ADDRESS', 'EMPLOYER'})
        """
        if not recherche_text:
            return set()
        
        # Normaliser le texte
        normalized_text = PartnerRequestParser.normalize_text(recherche_text)
        logger.info(f"Parsing RECHERCHE: '{recherche_text}' → '{normalized_text}'")
        
        # Récupérer les mots-clés pour ce client (triés par priorité DESC)
        keywords = PartnerRequestKeyword.query.filter_by(
            client_id=client_id
        ).order_by(PartnerRequestKeyword.priority.desc()).all()
        
        if not keywords:
            logger.warning(f"Aucun mot-clé configuré pour client_id={client_id}")
            return set()
        
        detected_requests = set()
        
        # Parcourir les mots-clés par ordre de priorité
        for keyword in keywords:
            pattern_normalized = PartnerRequestParser.normalize_text(keyword.pattern)
            
            if keyword.is_regex:
                # Mode regex
                try:
                    if re.search(pattern_normalized, normalized_text):
                        detected_requests.add(keyword.request_code)
                        logger.info(f"  ✓ {keyword.request_code} détecté (regex: '{keyword.pattern}')")
                except re.error as e:
                    logger.error(f"Regex invalide '{keyword.pattern}': {e}")
            else:
                # Mode substring simple
                if pattern_normalized in normalized_text:
                    detected_requests.add(keyword.request_code)
                    logger.info(f"  ✓ {keyword.request_code} détecté (pattern: '{keyword.pattern}')")
        
        if not detected_requests:
            logger.warning(f"Aucune demande détectée dans: '{recherche_text}'")
        else:
            logger.info(f"Demandes détectées: {sorted(detected_requests)}")
        
        return detected_requests
    
    @staticmethod
    def get_request_label(request_code):
        """
        Retourne le libellé français d'un code de demande
        
        Args:
            request_code (str): Code de demande
            
        Returns:
            str: Libellé en français
        """
        labels = {
            'ADDRESS': 'Adresse',
            'PHONE': 'Téléphone',
            'EMPLOYER': 'Employeur',
            'BANK': 'Banque',
            'BIRTH': 'Date et lieu de naissance'
        }
        return labels.get(request_code, request_code)




