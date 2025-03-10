# backend/services/tarification_service.py

import logging
from datetime import datetime
from models.tarifs import TarifEOS, TarifEnqueteur, EnqueteFacturation
from models.models_enqueteur import DonneeEnqueteur
from models.models import Donnee
from extensions import db

logger = logging.getLogger(__name__)

class TarificationService:
    """Service pour gérer la tarification des enquêtes et le calcul des rémunérations"""
    
    @staticmethod
    def get_tarif_eos(code_elements, date=None):
        """Récupère le tarif EOS pour un code d'éléments donné à une date donnée"""
        if not date:
            date = datetime.utcnow().date()
            
        tarif = TarifEOS.query.filter(
            TarifEOS.code == code_elements,
            TarifEOS.date_debut <= date,
            (TarifEOS.date_fin >= date) | (TarifEOS.date_fin.is_(None)),
            TarifEOS.actif == True
        ).order_by(TarifEOS.date_debut.desc()).first()
        
        return tarif
    
    @staticmethod
    def get_tarif_enqueteur(code_elements, enqueteur_id=None, date=None):
        """
        Récupère le tarif enquêteur pour un code d'éléments donné
        Vérifie d'abord s'il existe un tarif spécifique pour cet enquêteur,
        sinon utilise le tarif par défaut
        """
        if not date:
            date = datetime.utcnow().date()
            
        # Chercher un tarif spécifique pour cet enquêteur
        if enqueteur_id:
            tarif = TarifEnqueteur.query.filter(
                TarifEnqueteur.code == code_elements,
                TarifEnqueteur.enqueteur_id == enqueteur_id,
                TarifEnqueteur.date_debut <= date,
                (TarifEnqueteur.date_fin >= date) | (TarifEnqueteur.date_fin.is_(None)),
                TarifEnqueteur.actif == True
            ).order_by(TarifEnqueteur.date_debut.desc()).first()
            
            if tarif:
                return tarif
        
        # Si aucun tarif spécifique, utiliser le tarif par défaut
        tarif = TarifEnqueteur.query.filter(
            TarifEnqueteur.code == code_elements,
            TarifEnqueteur.enqueteur_id.is_(None),
            TarifEnqueteur.date_debut <= date,
            (TarifEnqueteur.date_fin >= date) | (TarifEnqueteur.date_fin.is_(None)),
            TarifEnqueteur.actif == True
        ).order_by(TarifEnqueteur.date_debut.desc()).first()
        
        return tarif
    
    @staticmethod
    def calculate_tarif_for_enquete(donnee_enqueteur_id):
        """
        Calcule les tarifs (EOS et enquêteur) pour une enquête spécifique
        et enregistre les résultats dans la table EnqueteFacturation
        """
        try:
            # Récupérer les données de l'enquête
            donnee_enqueteur = DonneeEnqueteur.query.get(donnee_enqueteur_id)
            if not donnee_enqueteur:
                logger.error(f"DonneeEnqueteur {donnee_enqueteur_id} non trouvée")
                return None
                
            donnee = Donnee.query.get(donnee_enqueteur.donnee_id)
            if not donnee:
                logger.error(f"Donnee {donnee_enqueteur.donnee_id} non trouvée")
                return None
                
            # Vérifier si une facturation existe déjà
            facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur_id).first()
            if not facturation:
                facturation = EnqueteFacturation(
                    donnee_id=donnee.id,
                    donnee_enqueteur_id=donnee_enqueteur.id
                )
                db.session.add(facturation)
            
            # Si le résultat est positif (P) ou confirmé (H) et des éléments ont été retrouvés
            if donnee_enqueteur.code_resultat in ['P', 'H'] and donnee_enqueteur.elements_retrouves:
                elements_code = donnee_enqueteur.elements_retrouves
                
                # Récupérer les tarifs
                tarif_eos = TarificationService.get_tarif_eos(elements_code)
                tarif_enqueteur = TarificationService.get_tarif_enqueteur(
                    elements_code, 
                    donnee.enqueteurId
                )
                
                # Mettre à jour la facturation
                if tarif_eos:
                    facturation.tarif_eos_code = elements_code
                    facturation.tarif_eos_montant = tarif_eos.montant
                    facturation.resultat_eos_montant = tarif_eos.montant  # Simplifié, dans un cas réel il faudrait prendre en compte les ajustements
                
                if tarif_enqueteur:
                    facturation.tarif_enqueteur_code = elements_code
                    facturation.tarif_enqueteur_montant = tarif_enqueteur.montant
                    facturation.resultat_enqueteur_montant = tarif_enqueteur.montant  # Simplifié
            else:
                # Si le résultat est négatif, tout mettre à zéro
                facturation.tarif_eos_code = None
                facturation.tarif_eos_montant = 0
                facturation.resultat_eos_montant = 0
                facturation.tarif_enqueteur_code = None
                facturation.tarif_enqueteur_montant = 0
                facturation.resultat_enqueteur_montant = 0
            
            db.session.commit()
            return facturation
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul des tarifs: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_enqueteur_earnings(enqueteur_id, month=None, year=None):
        """
        Calcule les gains d'un enquêteur pour un mois et une année donnés
        Si month et year ne sont pas fournis, retourne les gains totaux
        """
        try:
            query = db.session.query(
                EnqueteFacturation
            ).join(
                Donnee, Donnee.id == EnqueteFacturation.donnee_id
            ).filter(
                Donnee.enqueteurId == enqueteur_id,
                EnqueteFacturation.resultat_enqueteur_montant > 0
            )
            
            if month and year:
                # Filtrer par mois et année
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                    
                query = query.filter(
                    EnqueteFacturation.created_at >= start_date,
                    EnqueteFacturation.created_at < end_date
                )
            
            # Récupérer toutes les facturations correspondantes
            facturations = query.all()
            
            # Calculer le total
            total_gagne = sum(float(f.resultat_enqueteur_montant) for f in facturations)
            total_paye = sum(float(f.resultat_enqueteur_montant) for f in facturations if f.paye)
            total_a_payer = total_gagne - total_paye
            
            # Détail par statut de paiement
            details = {
                'facturations': [f.to_dict() for f in facturations],
                'total_gagne': total_gagne,
                'total_paye': total_paye,
                'total_a_payer': total_a_payer,
                'nombre_enquetes': len(facturations)
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des gains: {str(e)}")
            return None
    
    @staticmethod
    def marquer_comme_paye(facturation_ids, reference_paiement=None):
        """Marque un ensemble de facturations comme payées"""
        try:
            date_paiement = datetime.utcnow().date()
            
            # Mettre à jour toutes les facturations en une seule requête
            updated = EnqueteFacturation.query.filter(
                EnqueteFacturation.id.in_(facturation_ids),
                EnqueteFacturation.paye == False
            ).update({
                'paye': True,
                'date_paiement': date_paiement,
                'reference_paiement': reference_paiement
            }, synchronize_session=False)
            
            db.session.commit()
            return updated
            
        except Exception as e:
            logger.error(f"Erreur lors du marquage des paiements: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def initialiser_tarifs_par_defaut():
        """
        Initialise les tarifs par défaut dans la base de données 
        si aucun tarif n'existe
        """
        try:
            # Vérifier si des tarifs existent déjà
            if TarifEOS.query.count() == 0:
                # Tarifs EOS (basés sur le cahier des charges)
                tarifs_eos = [
                    {'code': 'A', 'description': 'Adresse seule', 'montant': 8.0},
                    {'code': 'T', 'description': 'Téléphone seul', 'montant': 14.0},
                    {'code': 'AT', 'description': 'Adresse et téléphone', 'montant': 22.0},
                    {'code': 'D', 'description': 'Décès', 'montant': 10.0},
                    {'code': 'AB', 'description': 'Adresse et banque', 'montant': 12.0},
                    {'code': 'AE', 'description': 'Adresse et employeur', 'montant': 12.0},
                    {'code': 'AR', 'description': 'Adresse et revenus', 'montant': 12.0},
                    {'code': 'ATB', 'description': 'Adresse, téléphone et banque', 'montant': 24.0},
                    {'code': 'ATE', 'description': 'Adresse, téléphone et employeur', 'montant': 24.0},
                    {'code': 'ATR', 'description': 'Adresse, téléphone et revenus', 'montant': 24.0},
                    {'code': 'ATBE', 'description': 'Adresse, téléphone, banque et employeur', 'montant': 26.0},
                    {'code': 'ATBER', 'description': 'Adresse, téléphone, banque, employeur et revenus', 'montant': 28.0}
                ]
                
                for tarif_data in tarifs_eos:
                    tarif = TarifEOS(
                        code=tarif_data['code'],
                        description=tarif_data['description'],
                        montant=tarif_data['montant'],
                        date_debut=datetime.utcnow().date(),
                        actif=True
                    )
                    db.session.add(tarif)
                
            # Vérifier si des tarifs enquêteur existent déjà
            if TarifEnqueteur.query.count() == 0:
                # Tarifs Enquêteur par défaut (70% des tarifs EOS)
                tarifs_enqueteur = [
                    {'code': 'A', 'description': 'Adresse seule', 'montant': 5.6},
                    {'code': 'T', 'description': 'Téléphone seul', 'montant': 9.8},
                    {'code': 'AT', 'description': 'Adresse et téléphone', 'montant': 15.4},
                    {'code': 'D', 'description': 'Décès', 'montant': 7.0},
                    {'code': 'AB', 'description': 'Adresse et banque', 'montant': 8.4},
                    {'code': 'AE', 'description': 'Adresse et employeur', 'montant': 8.4},
                    {'code': 'AR', 'description': 'Adresse et revenus', 'montant': 8.4},
                    {'code': 'ATB', 'description': 'Adresse, téléphone et banque', 'montant': 16.8},
                    {'code': 'ATE', 'description': 'Adresse, téléphone et employeur', 'montant': 16.8},
                    {'code': 'ATR', 'description': 'Adresse, téléphone et revenus', 'montant': 16.8},
                    {'code': 'ATBE', 'description': 'Adresse, téléphone, banque et employeur', 'montant': 18.2},
                    {'code': 'ATBER', 'description': 'Adresse, téléphone, banque, employeur et revenus', 'montant': 19.6}
                ]
                
                for tarif_data in tarifs_enqueteur:
                    tarif = TarifEnqueteur(
                        code=tarif_data['code'],
                        description=tarif_data['description'],
                        montant=tarif_data['montant'],
                        enqueteur_id=None,  # Tarif par défaut
                        date_debut=datetime.utcnow().date(),
                        actif=True
                    )
                    db.session.add(tarif)
                
            db.session.commit()
            logger.info("Tarifs par défaut initialisés avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des tarifs: {str(e)}")
            db.session.rollback()
            return False