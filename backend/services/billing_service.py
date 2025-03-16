"""
Service de facturation conforme au cahier des charges EOS France
Implémente les règles de calcul des 4 composantes du montant facturé:
- tarif appliqué
- cumul des montants précédemment facturés
- reprise de facturation
- remise éventuelle
"""

import logging
from datetime import datetime, timedelta
from models.models_enqueteur import DonneeEnqueteur

logger = logging.getLogger(__name__)

class BillingService:
    # Tarifs contractuels (à ajuster selon contrat réel)
    TARIFS = {
        'A': 8.0,  # Adresse seule
        'T': 14.0,  # Téléphone seul (rarement utilisé)
        'AT': 22.0,  # Adresse + téléphone
        'D': 10.0,  # Information décès
        'AB': 12.0,  # Adresse + banque
        'AE': 12.0,  # Adresse + employeur
        'AR': 12.0,  # Adresse + revenus
        'ATB': 24.0,  # Adresse + téléphone + banque
        'ATE': 24.0,  # Adresse + téléphone + employeur
        'ATR': 24.0,  # Adresse + téléphone + revenus
        'ATBE': 26.0,  # Adresse + téléphone + banque + employeur
        'ATBER': 28.0,  # Adresse + téléphone + banque + employeur + revenus
    }
    
    @staticmethod
    def calculate_tarif_applique(code_resultat, elements_retrouves):
        """
        Calcule le tarif appliqué selon les éléments retrouvés
        Renvoie 0 pour les codes résultat N, Z, I, Y (négatifs)
        Pour les codes P et H, renvoie le tarif selon les éléments retrouvés
        """
        if code_resultat not in ['P', 'H', 'D']:
            return 0.0
            
        # Pour un décès, utiliser le tarif spécifique
        if code_resultat == 'D' or elements_retrouves == 'D':
            return BillingService.TARIFS.get('D', 0.0)
            
        # Pour les autres cas positifs, utiliser le tarif correspondant aux éléments
        if elements_retrouves:
            # Trier les éléments pour s'assurer de la cohérence (ex: AT = TA)
            sorted_elements = ''.join(sorted(elements_retrouves))
            return BillingService.TARIFS.get(sorted_elements, 0.0)
            
        return 0.0
        
    @staticmethod
    def calculate_billing(donnee_enqueteur, previous_data=None, is_contestation=False):
        """
        Calcule les composantes de facturation selon les règles du cahier des charges
        
        Args:
            donnee_enqueteur: Instance de DonneeEnqueteur à mettre à jour
            previous_data: Données de facturation précédentes (pour les contestations)
            is_contestation: Booléen indiquant s'il s'agit d'une contestation
            
        Returns:
            dict: Les composantes de facturation calculées
        """
        code_resultat = donnee_enqueteur.code_resultat
        elements_retrouves = donnee_enqueteur.elements_retrouves
        
        # 1. Calcul du tarif appliqué
        tarif_applique = BillingService.calculate_tarif_applique(code_resultat, elements_retrouves)
        
        # 2. Cumul des montants précédemment facturés (toujours 0 pour les enquêtes initiales)
        cumul_montants_precedents = 0.0
        if is_contestation and previous_data:
            # Pour une contestation, il faut défacturer les montants précédents
            # Ce montant est toujours négatif (ou 0)
            cumul_montants_precedents = -1 * float(previous_data.get('cumul_montants_precedents', 0.0))
            
        # 3. Reprise de facturation
        # S'applique pour les contestations quand éléments étaient corrects dans les 15j
        reprise_facturation = 0.0
        
        # 4. Remise éventuelle (à implémenter selon les règles métier)
        remise_eventuelle = 0.0
        
        # Calcul du montant total facturé
        montant_facture = tarif_applique + cumul_montants_precedents + reprise_facturation + remise_eventuelle
        
        # Mise à jour de l'objet DonneeEnqueteur
        donnee_enqueteur.tarif_applique = tarif_applique
        donnee_enqueteur.cumul_montants_precedents = cumul_montants_precedents
        donnee_enqueteur.reprise_facturation = reprise_facturation
        donnee_enqueteur.remise_eventuelle = remise_eventuelle
        donnee_enqueteur.montant_facture = montant_facture
        
        # Générer un numéro de facture pour les résultats positifs
        if code_resultat in ['P', 'H', 'D'] and montant_facture > 0:
            # Format exemple: E{année}{mois}{numéro séquentiel}
            now = datetime.now()
            donnee_enqueteur.numero_facture = f"E{now.year}{now.month:02d}{donnee_enqueteur.id:04d}"
            donnee_enqueteur.date_facture = now.date()
            
        return {
            'tarif_applique': tarif_applique,
            'cumul_montants_precedents': cumul_montants_precedents,
            'reprise_facturation': reprise_facturation,
            'remise_eventuelle': remise_eventuelle,
            'montant_facture': montant_facture
        }
        
    @staticmethod
    def process_contestation(donnee_enqueteur, original_enquete, previous_billing_data):
        """
        Traitement spécifique pour les contestations selon le cahier des charges
        
        Args:
            donnee_enqueteur: Instance de DonneeEnqueteur actuelle (la contestation)
            original_enquete: Instance de DonneeEnqueteur originale (enquête contestée)
            previous_billing_data: Données de facturation précédentes
            
        Returns:
            dict: Les composantes de facturation calculées
        """
        try:
            code_resultat = donnee_enqueteur.code_resultat
            elements_retrouves = donnee_enqueteur.elements_retrouves
            
            # 1. Calcul du tarif appliqué selon les éléments retrouvés
            tarif_applique = BillingService.calculate_tarif_applique(code_resultat, elements_retrouves)
            
            # 2. Cumul des montants précédemment facturés (montant négatif)
            # Il s'agit de la somme négative de tous les montants facturés précédemment
            previous_montant = float(previous_billing_data.get('montant_facture', 0.0))
            cumul_montants_precedents = -previous_montant if previous_montant else 0.0
            
            # 3. Reprise de facturation
            reprise_facturation = 0.0
            
            # Si le code est H (confirmé), ou si certains éléments contestés s'avèrent corrects
            # dans les 15 jours suivant le retour de l'enquête
            if code_resultat == 'H' or (code_resultat == 'P' and original_enquete):
                # Vérifier si les éléments étaient corrects dans les 15 jours suivant l'enquête
                # Cette partie nécessite une logique métier spécifique
                # Pour l'exemple, nous supposerons que c'est le cas pour le code H
                if code_resultat == 'H':
                    reprise_facturation = previous_montant
            # Après avoir vérifié si code_resultat == 'H'
            if code_resultat == 'H' or (code_resultat == 'P' and original_enquete):
                # Vérifier le délai de 15 jours
                today = datetime.now().date()
                if original_enquete and original_enquete.date_retour:
                    delai = (today - original_enquete.date_retour).days
                    if delai <= 15:  # Si moins de 15 jours
                        reprise_facturation = previous_montant
            
            # 4. Remise éventuelle (à implémenter selon les règles métier)
            remise_eventuelle = 0.0
            
            # Calcul du montant total facturé
            montant_facture = tarif_applique + cumul_montants_precedents + reprise_facturation + remise_eventuelle
            
            # Mise à jour de l'objet DonneeEnqueteur
            donnee_enqueteur.tarif_applique = tarif_applique
            donnee_enqueteur.cumul_montants_precedents = cumul_montants_precedents
            donnee_enqueteur.reprise_facturation = reprise_facturation
            donnee_enqueteur.remise_eventuelle = remise_eventuelle
            donnee_enqueteur.montant_facture = montant_facture
            
            # Générer un numéro de facture uniquement si montant_facture > 0
            if montant_facture > 0:
                now = datetime.now()
                donnee_enqueteur.numero_facture = f"E{now.year}{now.month:02d}{donnee_enqueteur.id:04d}"
                donnee_enqueteur.date_facture = now.date()
            
            # Avant de retourner les résultats
            donnee_enqueteur.enquete_originale_reference = original_enquete.id if original_enquete else None
            return {
                'tarif_applique': tarif_applique,
                'cumul_montants_precedents': cumul_montants_precedents,
                'reprise_facturation': reprise_facturation,
                'remise_eventuelle': remise_eventuelle,
                'montant_facture': montant_facture
            }
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la contestation: {str(e)}")
            # Valeurs par défaut sécurisées
            tarif_applique = 0.0
            cumul_montants_precedents = 0.0
            reprise_facturation = 0.0
            remise_eventuelle = 0.0
            montant_facture = 0.0