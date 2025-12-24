"""
Service de calcul du statut POS/NEG par demande pour PARTNER
Détermine si chaque demande a été trouvée ou non
"""
import logging
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.partner_models import PartnerCaseRequest
from extensions import db

logger = logging.getLogger(__name__)


class PartnerRequestCalculator:
    """Calcule le statut POS/NEG pour chaque demande"""
    
    @staticmethod
    def is_address_found(donnee_enqueteur):
        """
        Vérifie si l'adresse a été trouvée
        
        Args:
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            bool: True si adresse trouvée
        """
        if not donnee_enqueteur:
            return False
        
        # Adresse trouvée si au moins une ligne d'adresse OU (CP + Ville)
        has_address_lines = any([
            donnee_enqueteur.adresse1,
            donnee_enqueteur.adresse2,
            donnee_enqueteur.adresse3,
            donnee_enqueteur.adresse4
        ])
        
        has_cp_ville = bool(
            donnee_enqueteur.code_postal and 
            donnee_enqueteur.ville
        )
        
        return bool(has_address_lines or has_cp_ville)
    
    @staticmethod
    def is_phone_found(donnee_enqueteur):
        """
        Vérifie si le téléphone a été trouvé
        
        Args:
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            bool: True si téléphone trouvé
        """
        if not donnee_enqueteur:
            return False
        
        # Téléphone trouvé si non vide et différent de "0"
        tel = donnee_enqueteur.telephone_personnel
        return bool(tel and tel.strip() and tel.strip() != "0")
    
    @staticmethod
    def is_employer_found(donnee_enqueteur):
        """
        Vérifie si l'employeur a été trouvé
        
        Args:
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            bool: True si employeur trouvé
        """
        if not donnee_enqueteur:
            return False
        
        # Employeur trouvé si nom OU au moins une ligne d'adresse employeur
        has_nom = bool(donnee_enqueteur.nom_employeur and donnee_enqueteur.nom_employeur.strip())
        
        has_address = any([
            donnee_enqueteur.adresse1_employeur,
            donnee_enqueteur.adresse2_employeur,
            donnee_enqueteur.adresse3_employeur,
            donnee_enqueteur.adresse4_employeur
        ])
        
        return bool(has_nom or has_address)
    
    @staticmethod
    def is_bank_found(donnee_enqueteur):
        """
        Vérifie si la banque a été trouvée
        
        Args:
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            bool: True si banque trouvée
        """
        if not donnee_enqueteur:
            return False
        
        # Banque trouvée si nom banque OU codes banque/guichet
        has_nom = bool(donnee_enqueteur.banque_domiciliation and donnee_enqueteur.banque_domiciliation.strip())
        
        has_codes = bool(
            (donnee_enqueteur.code_banque and donnee_enqueteur.code_banque.strip()) or
            (donnee_enqueteur.code_guichet and donnee_enqueteur.code_guichet.strip())
        )
        
        return bool(has_nom or has_codes)
    
    @staticmethod
    def is_birth_found(donnee, donnee_enqueteur):
        """
        Vérifie si la date/lieu de naissance a été trouvé
        
        Args:
            donnee (Donnee): Données dossier
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            bool: True si naissance trouvée
        """
        # Vérifier dans donnee.dateNaissance_maj et lieuNaissance_maj
        has_date = bool(donnee and donnee.dateNaissance_maj)
        has_lieu = bool(donnee and donnee.lieuNaissance_maj and donnee.lieuNaissance_maj.strip())
        
        # POS si au moins date OU lieu
        return bool(has_date or has_lieu)
    
    @staticmethod
    def get_memo_for_request(request_code, donnee_enqueteur):
        """
        Récupère le mémo approprié pour une demande NEG
        
        Args:
            request_code (str): Code de demande
            donnee_enqueteur (DonneeEnqueteur): Données enquêteur
            
        Returns:
            str: Mémo ou None
        """
        if not donnee_enqueteur:
            return None
        
        if request_code == 'ADDRESS' or request_code == 'PHONE':
            return donnee_enqueteur.memo1  # Memo adresse/téléphone
        elif request_code == 'EMPLOYER':
            return donnee_enqueteur.memo3  # Memo employeur
        elif request_code == 'BANK':
            # Pas de memo banque spécifique, utiliser memo général si existe
            return None
        elif request_code == 'BIRTH':
            # Pas de memo naissance spécifique
            return None
        
        return None
    
    @staticmethod
    def calculate_request_status(donnee_id, request_code):
        """
        Calcule le statut (POS/NEG) d'une demande spécifique
        
        Args:
            donnee_id (int): ID du dossier
            request_code (str): Code de demande
            
        Returns:
            tuple: (found: bool, status: str, memo: str)
        """
        donnee = db.session.get(Donnee, donnee_id)
        if not donnee:
            return (False, 'NEG', 'Dossier introuvable')
        
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
        
        # Calculer si trouvé selon le type de demande
        found = False
        if request_code == 'ADDRESS':
            found = PartnerRequestCalculator.is_address_found(donnee_enqueteur)
        elif request_code == 'PHONE':
            found = PartnerRequestCalculator.is_phone_found(donnee_enqueteur)
        elif request_code == 'EMPLOYER':
            found = PartnerRequestCalculator.is_employer_found(donnee_enqueteur)
        elif request_code == 'BANK':
            found = PartnerRequestCalculator.is_bank_found(donnee_enqueteur)
        elif request_code == 'BIRTH':
            found = PartnerRequestCalculator.is_birth_found(donnee, donnee_enqueteur)
        
        # Déterminer le statut
        status = 'POS' if found else 'NEG'
        
        # Récupérer le mémo si NEG
        memo = None
        if not found:
            memo = PartnerRequestCalculator.get_memo_for_request(request_code, donnee_enqueteur)
        
        return (found, status, memo)
    
    @staticmethod
    def recalculate_all_requests(donnee_id):
        """
        Recalcule le statut de toutes les demandes d'un dossier
        
        Args:
            donnee_id (int): ID du dossier
            
        Returns:
            dict: Statistiques de recalcul
        """
        # Récupérer toutes les demandes du dossier
        requests = PartnerCaseRequest.query.filter_by(
            donnee_id=donnee_id,
            requested=True
        ).all()
        
        if not requests:
            logger.info(f"Aucune demande à recalculer pour donnee_id={donnee_id}")
            return {'updated': 0, 'pos': 0, 'neg': 0}
        
        updated_count = 0
        pos_count = 0
        neg_count = 0
        
        for request in requests:
            # Calculer le nouveau statut
            found, status, memo = PartnerRequestCalculator.calculate_request_status(
                donnee_id,
                request.request_code
            )
            
            # Mettre à jour si changé
            if request.found != found or request.status != status:
                request.found = found
                request.status = status
                request.memo = memo
                updated_count += 1
            
            if status == 'POS':
                pos_count += 1
            else:
                neg_count += 1
        
        db.session.commit()
        
        logger.info(f"Recalcul donnee_id={donnee_id}: {updated_count} mises à jour, {pos_count} POS, {neg_count} NEG")
        
        return {
            'updated': updated_count,
            'pos': pos_count,
            'neg': neg_count
        }
    
    @staticmethod
    def is_global_positive(donnee_id):
        """
        Détermine si le dossier est globalement positif
        Global POS si AU MOINS une demande demandée est POS
        
        Args:
            donnee_id (int): ID du dossier
            
        Returns:
            bool: True si global POS
        """
        # Compter les demandes POS demandées
        pos_count = PartnerCaseRequest.query.filter_by(
            donnee_id=donnee_id,
            requested=True,
            status='POS'
        ).count()
        
        return pos_count > 0

