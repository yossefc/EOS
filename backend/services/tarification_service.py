import logging
from datetime import datetime
from models.tarifs import TarifEOS, TarifEnqueteur, EnqueteFacturation
from models.models_enqueteur import DonneeEnqueteur
from models.models import Donnee
from extensions import db
from services.billing_service import BillingService

logger = logging.getLogger(__name__)

class TarificationService:
    """Service pour gérer la tarification des enquêtes et le calcul des rémunérations"""
    
    @staticmethod
    def get_tarif_eos(code_elements, date=None):
        """Récupère le tarif EOS pour un code d'éléments donné à une date donnée"""
        if not date:
            date = datetime.now().date()
            
        # Imprimer les informations de recherche de tarif
        logger.info(f"Recherche de tarif EOS pour code: {code_elements}, date: {date}")
        
        # Afficher tous les tarifs disponibles en DEBUG
        all_tarifs = TarifEOS.query.filter(TarifEOS.actif == True).all()
        logger.info(f"Tarifs EOS disponibles: {[(t.code, t.montant) for t in all_tarifs]}")
        
        # Recherche du tarif spécifique
        tarif = TarifEOS.query.filter(
            TarifEOS.code == code_elements,
            TarifEOS.date_debut <= date,
            (TarifEOS.date_fin >= date) | (TarifEOS.date_fin.is_(None)),
            TarifEOS.actif == True
        ).order_by(TarifEOS.date_debut.desc()).first()
        
        if not tarif:
            logger.warning(f"Aucun tarif EOS trouvé pour le code {code_elements}")
        else:
            logger.info(f"Tarif EOS trouvé: {tarif.code} - {tarif.montant}€")
        
        return tarif
    
    @staticmethod
    def get_tarif_enqueteur(code_elements, enqueteur_id=None, date=None):
        """
        Récupère le tarif enquêteur pour un code d'éléments donné
        Vérifie d'abord s'il existe un tarif spécifique pour cet enquêteur,
        sinon utilise le tarif par défaut
        """
        if not date:
            date = datetime.now().date()
            
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
        Calcule les tarifs applicables pour une enquête ou une contestation
        et crée ou met à jour une facturation correspondante.
        """
        try:
            # 1. Récupérer donnee_enqueteur
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(id=donnee_enqueteur_id).first()
            if not donnee_enqueteur:
                logger.error(f"DonneeEnqueteur {donnee_enqueteur_id} non trouvé")
                return None

            # 2. Récupérer la donnée associée
            donnee = db.session.get(Donnee, donnee_enqueteur.donnee_id)
            if not donnee:
                logger.error(f"Donnee {donnee_enqueteur.donnee_id} non trouvé")
                return None

            # 3. Vérifier si c'est une contestation
            is_contestation = donnee.est_contestation and donnee.enquete_originale_id
            logger.info(f"Traitement de {donnee.id}: est_contestation={is_contestation}, code_resultat={donnee_enqueteur.code_resultat}")
            
            # Vérifier si un enquêteur est assigné
            if not donnee.enqueteurId:
                if is_contestation:
                    # Pour une contestation, assigner automatiquement l'enquêteur de l'originale
                    enquete_originale = db.session.get(Donnee, donnee.enquete_originale_id)
                    if enquete_originale and enquete_originale.enqueteurId:
                        donnee.enqueteurId = enquete_originale.enqueteurId
                        db.session.commit()
                        logger.info(f"Enquêteur {donnee.enqueteurId} assigné automatiquement depuis l'enquête originale")
                    else:
                        # MODIFICATION: Assigner un enquêteur par défaut si non trouvé
                        # Récupérer le premier enquêteur disponible
                        from models.enqueteur import Enqueteur
                        default_enqueteur = Enqueteur.query.first()
                        if default_enqueteur:
                            donnee.enqueteurId = default_enqueteur.id
                            db.session.commit()
                            logger.info(f"Enquêteur par défaut {default_enqueteur.id} assigné à la contestation")
                        else:
                            logger.error(f"Impossible d'assigner un enquêteur à la contestation {donnee.id}")
                            return None
                else:
                    logger.error(f"No enqueteur assigned to donnee {donnee.id}, cannot calculate payment")
                    return None
            
            # Récupérer ou créer la facturation
            facturation = TarificationService._get_or_create_facturation(donnee, donnee_enqueteur)
            
            # Si c'est une contestation, traiter avec la logique spécifique
            if is_contestation:
                TarificationService._handle_contestation_facturation(facturation, donnee, donnee_enqueteur)
            else:
                # Cas standard (non contestation)
                TarificationService._handle_standard_facturation(facturation, donnee, donnee_enqueteur)
            
            # Vérification finale pour s'assurer qu'il y a un montant défini
            if facturation.resultat_enqueteur_montant is None:
                facturation.resultat_enqueteur_montant = 0.0
                
            # Commit des changements
            db.session.commit()
            logger.info(f"Facturation enregistrée avec succès pour l'enquête {donnee.id}: montant enquêteur {facturation.resultat_enqueteur_montant}€")
            
            return facturation
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul des tarifs: {str(e)}", exc_info=True)
            db.session.rollback()
            return None
    
    @staticmethod
    def _get_or_create_facturation(donnee, donnee_enqueteur):
        """Récupère ou crée une facturation pour l'enquête"""
        facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
        if not facturation:
            facturation = EnqueteFacturation(
                donnee_id=donnee.id,
                donnee_enqueteur_id=donnee_enqueteur.id,
                tarif_eos_code="",
                tarif_eos_montant=0.0,
                resultat_eos_montant=0.0,
                tarif_enqueteur_code="",
                tarif_enqueteur_montant=0.0,
                resultat_enqueteur_montant=0.0,
                paye=False
            )
            db.session.add(facturation)
            db.session.commit()
            logger.info(f"Facturation créée pour l'enquête {donnee.id}")
        return facturation

    @staticmethod
    def _handle_contestation_facturation(facturation, donnee, donnee_enqueteur):
        """Gère la facturation pour une contestation"""
        logger.info(f"Traitement contestation {donnee.id}: code_resultat={donnee_enqueteur.code_resultat}, elements={donnee_enqueteur.elements_retrouves}")
        
        # Si le code_resultat est vide, on crée juste une facturation vide pour le moment
        if not donnee_enqueteur.code_resultat:
            facturation.tarif_eos_code = "ENCOURS"
            facturation.tarif_eos_montant = 0.0
            facturation.resultat_eos_montant = 0.0
            facturation.tarif_enqueteur_code = "ENCOURS"
            facturation.tarif_enqueteur_montant = 0.0
            facturation.resultat_enqueteur_montant = 0.0
            db.session.commit()
            logger.info(f"Facturation mise à jour pour contestation en cours (sans code résultat)")
            return
        
        # Récupérer l'enquête originale et ses données
        enquete_originale = db.session.get(Donnee, donnee.enquete_originale_id)
        if not enquete_originale:
            logger.error(f"Enquête originale {donnee.enquete_originale_id} non trouvée")
            # MODIFICATION: Même sans enquête originale, créer une facturation basique
            elements_code = donnee_enqueteur.elements_retrouves or 'A'
            tarif_eos = TarificationService.get_tarif_eos(elements_code)
            tarif_enqueteur = TarificationService.get_tarif_enqueteur(elements_code, donnee.enqueteurId)
            
            if tarif_eos:
                facturation.tarif_eos_code = elements_code
                facturation.tarif_eos_montant = tarif_eos.montant
                facturation.resultat_eos_montant = tarif_eos.montant
            else:
                facturation.tarif_eos_code = elements_code
                facturation.tarif_eos_montant = 10.0  # Valeur par défaut
                facturation.resultat_eos_montant = 10.0
            
            if tarif_enqueteur:
                facturation.tarif_enqueteur_code = elements_code
                facturation.tarif_enqueteur_montant = tarif_enqueteur.montant
                facturation.resultat_enqueteur_montant = tarif_enqueteur.montant
            else:
                facturation.tarif_enqueteur_code = elements_code
                facturation.tarif_enqueteur_montant = 7.0  # Valeur par défaut
                facturation.resultat_enqueteur_montant = 7.0
            
            logger.info(f"Facturation créée sans enquête originale: {facturation.resultat_enqueteur_montant}€")
            return
        
        original_enquete = DonneeEnqueteur.query.filter_by(donnee_id=enquete_originale.id).first()
        if not original_enquete:
            logger.warning(f"Données enquêteur de l'enquête originale {enquete_originale.id} non trouvées")
            # MODIFICATION: Créer l'objet DonneeEnqueteur s'il n'existe pas
            original_enquete = DonneeEnqueteur(donnee_id=enquete_originale.id)
            db.session.add(original_enquete)
            db.session.commit()
        
        original_facturation = None
        if original_enquete:
            original_facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=original_enquete.id).first()
        
        # Traiter selon le code résultat
        if donnee_enqueteur.code_resultat == 'N':
            TarificationService._handle_negative_contestation(facturation, donnee, original_enquete, original_facturation)
        elif donnee_enqueteur.code_resultat in ['P', 'H']:
            TarificationService._handle_positive_contestation(facturation, donnee, donnee_enqueteur, original_enquete, original_facturation)
        else:
            # Pour les autres codes résultat (Z, I, Y...)
            logger.info(f"Contestation avec code résultat {donnee_enqueteur.code_resultat} pour l'enquête {donnee.id}")
            facturation.tarif_eos_code = donnee_enqueteur.code_resultat
            facturation.tarif_eos_montant = 0.0
            facturation.resultat_eos_montant = 0.0
            facturation.tarif_enqueteur_code = donnee_enqueteur.code_resultat
            facturation.tarif_enqueteur_montant = 0.0
            facturation.resultat_enqueteur_montant = 0.0

    @staticmethod
    def _handle_negative_contestation(facturation, donnee, original_enquete, original_facturation):
        """Gère une contestation avec résultat négatif"""
        logger.info(f"Contestation négative (N) pour l'enquête {donnee.id}")
        
        # Mettre à jour la facturation de la contestation à ZÉRO
        facturation.tarif_eos_code = 'N'
        facturation.tarif_eos_montant = 0.0
        facturation.resultat_eos_montant = 0.0
        facturation.tarif_enqueteur_code = 'N'
        facturation.tarif_enqueteur_montant = 0.0
        facturation.resultat_enqueteur_montant = 0.0  # IMPORTANT: Doit être zéro!
        
        # Créer une facturation négative pour l'enquête originale
        if original_facturation and original_enquete:
            previous_montant_eos = float(original_facturation.resultat_eos_montant or 0.0)
            previous_montant_enq = float(original_facturation.resultat_enqueteur_montant or 0.0)
            
            if previous_montant_enq > 0:
                try:
                    # Vérifier si une facturation négative existe déjà
                    existing_neg = EnqueteFacturation.query.filter_by(
                        donnee_id=donnee.enquete_originale_id,
                        resultat_enqueteur_montant=-previous_montant_enq
                    ).first()
                    
                    if not existing_neg:
                        logger.info(f"Création d'une facturation négative pour l'enquête originale {donnee.enquete_originale_id}")
                        neg_facturation = EnqueteFacturation(
                            donnee_id=donnee.enquete_originale_id,
                            donnee_enqueteur_id=original_enquete.id,
                            tarif_eos_code=original_facturation.tarif_eos_code,
                            tarif_eos_montant=original_facturation.tarif_eos_montant,
                            resultat_eos_montant=-previous_montant_eos,
                            tarif_enqueteur_code=original_facturation.tarif_enqueteur_code,
                            tarif_enqueteur_montant=original_facturation.tarif_enqueteur_montant,
                            resultat_enqueteur_montant=-previous_montant_enq,
                            paye=False
                        )
                        db.session.add(neg_facturation)
                        db.session.commit()  # Ajout du commit ici
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la facturation négative: {str(e)}")
    @staticmethod
    def _handle_positive_contestation(facturation, donnee, donnee_enqueteur, original_enquete, original_facturation):
        """Gère une contestation avec résultat positif ou confirmé"""
        elements_code = donnee_enqueteur.elements_retrouves
        
        # Si pas d'éléments retrouvés, utiliser A par défaut
        if not elements_code:
            logger.warning(f"Contestation positive sans éléments retrouvés pour l'enquête {donnee.id}. Utilisation de 'A' par défaut.")
            elements_code = 'A'
            donnee_enqueteur.elements_retrouves = 'A'
        
        # MODIFICATION: Même si original_enquete est None, nous continuons
        
        # Calculer les tarifs pour cette contestation
        tarif_eos = TarificationService.get_tarif_eos(elements_code)
        tarif_enqueteur = TarificationService.get_tarif_enqueteur(elements_code, donnee.enqueteurId)
        
        if tarif_eos:
            facturation.tarif_eos_code = elements_code
            facturation.tarif_eos_montant = tarif_eos.montant
            facturation.resultat_eos_montant = tarif_eos.montant
        else:
            # Valeur par défaut
            facturation.tarif_eos_code = elements_code
            facturation.tarif_eos_montant = 10.0
            facturation.resultat_eos_montant = 10.0
        
        if tarif_enqueteur:
            facturation.tarif_enqueteur_code = elements_code
            facturation.tarif_enqueteur_montant = tarif_enqueteur.montant
            facturation.resultat_enqueteur_montant = tarif_enqueteur.montant
        else:
            # Valeur par défaut
            facturation.tarif_enqueteur_code = elements_code
            facturation.tarif_enqueteur_montant = 7.0
            facturation.resultat_enqueteur_montant = 7.0
        
        logger.info(f"Facturation contestation positive: code={elements_code}, montant={facturation.resultat_enqueteur_montant}€")

    @staticmethod
    def _handle_elements_change(facturation, donnee, elements_code, original_elements, original_enquete):
        """Gère les ajustements quand les éléments retrouvés changent dans une contestation"""
        logger.info(f"Éléments changés dans la contestation: {original_elements} -> {elements_code}")
        
        # Récupérer les tarifs
        tarif_eos_new = TarificationService.get_tarif_eos(elements_code)
        tarif_enqueteur_new = TarificationService.get_tarif_enqueteur(elements_code, donnee.enqueteurId)
        
        tarif_eos_old = TarificationService.get_tarif_eos(original_elements)
        tarif_enqueteur_old = TarificationService.get_tarif_enqueteur(original_elements, donnee.enqueteurId)
        
        # Calculer les différences de montant
        if tarif_eos_new and tarif_eos_old:
            # Si nouveaux éléments valent moins que les originaux
            if tarif_eos_new.montant < tarif_eos_old.montant:
                diff_eos = float(tarif_eos_old.montant) - float(tarif_eos_new.montant)
                diff_enq = 0
                
                if tarif_enqueteur_old and tarif_enqueteur_new:
                    diff_enq = float(tarif_enqueteur_old.montant) - float(tarif_enqueteur_new.montant)
                
                # Créer une facturation d'ajustement pour l'enquête originale
                if diff_enq > 0:
                    try:
                        logger.info(f"Création d'une facturation d'ajustement négative pour l'enquête originale")
                        neg_facturation = EnqueteFacturation(
                            donnee_id=donnee.enquete_originale_id,
                            donnee_enqueteur_id=original_enquete.id,
                            tarif_eos_code=elements_code,
                            tarif_eos_montant=tarif_eos_new.montant,
                            resultat_eos_montant=-diff_eos,
                            tarif_enqueteur_code=elements_code,
                            tarif_enqueteur_montant=tarif_enqueteur_new.montant if tarif_enqueteur_new else 0,
                            resultat_enqueteur_montant=-diff_enq,
                            paye=False
                        )
                        db.session.add(neg_facturation)
                    except Exception as e:
                        logger.error(f"Erreur lors de la création de la facturation d'ajustement: {str(e)}")

    @staticmethod
    def _handle_standard_facturation(facturation, donnee, donnee_enqueteur):
        """Gère la facturation pour une enquête standard (non contestation)"""
        if donnee_enqueteur.code_resultat in ['P', 'H'] and donnee_enqueteur.elements_retrouves:
            elements_code = donnee_enqueteur.elements_retrouves
            
            # Récupérer les tarifs
            tarif_eos = TarificationService.get_tarif_eos(elements_code)
            tarif_enqueteur = TarificationService.get_tarif_enqueteur(elements_code, donnee.enqueteurId)
            
            if tarif_eos:
                facturation.tarif_eos_code = elements_code
                facturation.tarif_eos_montant = tarif_eos.montant
                facturation.resultat_eos_montant = tarif_eos.montant
            else:
                # Valeur par défaut
                facturation.tarif_eos_code = elements_code
                facturation.tarif_eos_montant = 10.0
                facturation.resultat_eos_montant = 10.0
            
            if tarif_enqueteur:
                facturation.tarif_enqueteur_code = elements_code
                facturation.tarif_enqueteur_montant = tarif_enqueteur.montant
                facturation.resultat_enqueteur_montant = tarif_enqueteur.montant
            else:
                # Valeur par défaut
                facturation.tarif_enqueteur_code = elements_code
                facturation.tarif_enqueteur_montant = 7.0
                facturation.resultat_enqueteur_montant = 7.0
        else:
            # Pour les autres codes résultat ou sans éléments
            facturation.tarif_eos_code = donnee_enqueteur.code_resultat or ''
            facturation.resultat_eos_montant = 0.0
            facturation.tarif_enqueteur_code = donnee_enqueteur.code_resultat or ''
            facturation.resultat_enqueteur_montant = 0.0
    
    @staticmethod
    def process_contestation(donnee_enqueteur, original_enquete, previous_billing_data):
        """
        Traitement spécifique pour les contestations selon le cahier des charges
        Gère les contestations négatives et les changements d'éléments retrouvés
        """
        try:
            code_resultat = donnee_enqueteur.code_resultat
            elements_retrouves = donnee_enqueteur.elements_retrouves
            
            # Récupérer les éléments et le code résultat de l'enquête originale
            original_elements = original_enquete.elements_retrouves if original_enquete else ''
            original_code = original_enquete.code_resultat if original_enquete else ''
            
            # 1. Calcul du tarif appliqué selon les éléments retrouvés
            tarif_applique = BillingService.calculate_tarif_applique(code_resultat, elements_retrouves)
            
            # 2. Calcul des montants précédemment facturés
            previous_montant = float(previous_billing_data.get('montant_facture', 0.0))
            
            # Par défaut, on annule complètement le montant précédent
            cumul_montants_precedents = -previous_montant if previous_montant else 0.0
            reprise_facturation = 0.0
            
            # Obtenir l'ID de la donnée originale si disponible
            original_id = None
            if donnee_enqueteur and donnee_enqueteur.donnee and donnee_enqueteur.donnee.enquete_originale:
                original_id = donnee_enqueteur.donnee.enquete_originale.id
            
            # Cas où l'enquête originale était positive et la contestation aussi, mais avec moins d'éléments
            if code_resultat == 'P' and original_code == 'P' and elements_retrouves != original_elements:
                # Calculer les tarifs pour les deux ensembles d'éléments
                from models.models import Donnee
                original_donnee = db.session.get(Donnee, original_id) if original_id else None
                
                # Obtenir les tarifs pour les éléments originaux et nouveaux
                tarif_original_eos = TarificationService.get_tarif_eos(original_elements)
                tarif_original_enq = TarificationService.get_tarif_enqueteur(
                    original_elements, 
                    original_donnee.enqueteurId if original_donnee else None
                )
                
                tarif_nouveau_eos = TarificationService.get_tarif_eos(elements_retrouves)
                tarif_nouveau_enq = TarificationService.get_tarif_enqueteur(
                    elements_retrouves, 
                    original_donnee.enqueteurId if original_donnee else None
                )
                
                # Si les nouveaux tarifs sont inférieurs aux originaux, créer une facturation négative pour la différence
                if (tarif_original_eos and tarif_nouveau_eos and 
                    tarif_original_eos.montant > tarif_nouveau_eos.montant):
                    
                    # Calculer la différence
                    diff_eos = float(tarif_original_eos.montant) - float(tarif_nouveau_eos.montant)
                    diff_enq = 0
                    
                    if tarif_original_enq and tarif_nouveau_enq:
                        diff_enq = float(tarif_original_enq.montant) - float(tarif_nouveau_enq.montant)
                    
                    # Ne pas annuler le montant précédent complètement, mais seulement la différence
                    cumul_montants_precedents = -diff_eos
                    
                    # Créer une facturation négative pour l'enquêteur original
                    if original_id and diff_enq > 0:
                        try:
                            from models.tarifs import EnqueteFacturation
                            
                            # Vérifier si une facturation d'ajustement existe déjà
                            existing_neg = EnqueteFacturation.query.filter_by(
                                donnee_id=original_id,
                                resultat_enqueteur_montant=-diff_enq
                            ).first()
                            
                            if not existing_neg:
                                # Créer une nouvelle facturation négative
                                neg_facturation = EnqueteFacturation(
                                    donnee_id=original_id,
                                    donnee_enqueteur_id=original_enquete.id if original_enquete else None,
                                    tarif_eos_code=elements_retrouves,
                                    tarif_eos_montant=tarif_nouveau_eos.montant,
                                    resultat_eos_montant=-diff_eos,
                                    tarif_enqueteur_code=elements_retrouves,
                                    tarif_enqueteur_montant=tarif_nouveau_enq.montant if tarif_nouveau_enq else 0,
                                    resultat_enqueteur_montant=-diff_enq,  # MONTANT NÉGATIF
                                    paye=False
                                )
                                db.session.add(neg_facturation)
                                db.session.commit()
                                
                                logger.info(f"Facturation d'ajustement créée avec succès pour l'enquête {original_id}: différence de {diff_enq}€")
                        except Exception as e:
                            logger.error(f"Erreur lors de la création de la facturation d'ajustement: {str(e)}")
                    
                    # Mettre à jour le tarif appliqué de cette contestation
                    tarif_applique = float(tarif_nouveau_eos.montant)
                    
                # Si les éléments sont les mêmes ou le tarif est identique, pas de déduction
                elif elements_retrouves == original_elements:
                    cumul_montants_precedents = 0
                    reprise_facturation = previous_montant  # On reprend le montant précédent
                    
            # Cas où le résultat est confirmé (H)
            elif code_resultat == 'H':
                # Pour les contestations confirmées, reprendre le montant
                today = datetime.now().date()
                if original_enquete and original_enquete.date_retour:
                    delai = (today - original_enquete.date_retour).days
                    if delai <= 15:  # Si moins de 15 jours
                        reprise_facturation = previous_montant
                        cumul_montants_precedents = 0  # Pas de déduction
            
            # Cas où le résultat est négatif (N)
            elif code_resultat == 'N':
                # Pour les résultats négatifs, on annule complètement le paiement précédent
                if original_id and previous_montant > 0:
                    try:
                        from models.models import Donnee
                        original_donnee = db.session.get(Donnee, original_id)
                        
                        if original_donnee and original_donnee.enqueteurId:
                            from models.tarifs import EnqueteFacturation
                            
                            # Vérifier si une facturation d'annulation existe déjà
                            existing_neg = EnqueteFacturation.query.filter_by(
                                donnee_id=original_id,
                                resultat_enqueteur_montant=-previous_montant
                            ).first()
                            
                            if not existing_neg:
                                # Créer une nouvelle facturation négative
                                neg_facturation = EnqueteFacturation(
                                    donnee_id=original_id,
                                    donnee_enqueteur_id=original_enquete.id if original_enquete else None,
                                    tarif_eos_code=previous_billing_data.get('tarif_eos_code'),
                                    tarif_eos_montant=previous_billing_data.get('tarif_eos_montant'),
                                    resultat_eos_montant=-previous_montant,
                                    tarif_enqueteur_code=previous_billing_data.get('tarif_enqueteur_code'),
                                    tarif_enqueteur_montant=previous_billing_data.get('tarif_enqueteur_montant'),
                                    resultat_enqueteur_montant=-previous_montant,  # MONTANT NÉGATIF
                                    paye=False
                                )
                                db.session.add(neg_facturation)
                                db.session.commit()
                                
                                logger.info(f"Facturation négative créée avec succès pour l'enquête originale {original_id}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la création de la facturation négative: {str(e)}")
            
            # 4. Remise éventuelle
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
            
            # Référencer l'enquête originale
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
            # Valeurs par défaut sécurisées en cas d'erreur
            return {
                'tarif_applique': 0.0,
                'cumul_montants_precedents': 0.0,
                'reprise_facturation': 0.0,
                'remise_eventuelle': 0.0,
                'montant_facture': 0.0
            }
    
    @staticmethod
    def get_enqueteur_earnings(enqueteur_id, month=None, year=None):
        """
        Calcule les gains d'un enquêteur pour un mois et une année donnés
        Si month et year ne sont pas fournis, retourne les gains totaux
        Inclut à la fois les facturations positives et négatives, ainsi que les contestations
        """
        try:
            # Utiliser SQL brut pour plus de contrôle sur la requête
            from sqlalchemy import text
            
            sql_query = """
            SELECT ef.* 
            FROM enquete_facturation ef
            JOIN donnees d ON ef.donnee_id = d.id
            WHERE 
                -- Cas 1: Facturations directes (enquêtes où l'enquêteur est assigné)
                (d.enqueteurId = :enqueteur_id)
                
                -- Cas 2: Facturations liées à des contestations où cet enquêteur est impliqué
                OR (ef.donnee_id IN (
                    SELECT id FROM donnees 
                    WHERE enquete_originale_id IN (
                        SELECT id FROM donnees WHERE enqueteurId = :enqueteur_id
                    )
                ))
            """
            
            # Préparer la requête avec les paramètres
            params = {"enqueteur_id": enqueteur_id}
            
            # Ajouter les filtres de date si nécessaire
            if month and year:
                sql_query += """
                AND (
                    ef.created_at >= :start_date 
                    AND ef.created_at < :end_date
                )
                """
                
                # Définir les dates de début et de fin
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                    
                params["start_date"] = start_date
                params["end_date"] = end_date
            
            # Exécuter la requête
            result = db.session.execute(text(sql_query), params)
            
            # Convertir les résultats en objets EnqueteFacturation
            facturations = []
            for row in result:
                # Récupérer la facturation complète à partir de son ID
                facturation = db.session.get(EnqueteFacturation, row[0])
                if facturation:
                    facturations.append(facturation)
            
            # Calculer les totaux en tenant compte des montants négatifs (contestations)
            total_gagne = sum(float(f.resultat_enqueteur_montant) for f in facturations)
            
            # Pour les paiements, ne compter que les facturations dont paye=True 
            # (inclut à la fois les montants positifs et négatifs déjà payés)
            total_paye = sum(float(f.resultat_enqueteur_montant) for f in facturations if f.paye)
            
            # Le montant à payer inclut toutes les facturations non payées
            total_a_payer = sum(float(f.resultat_enqueteur_montant) for f in facturations if not f.paye)
            
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
            date_paiement = datetime.now().date()
            
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
                        date_debut=datetime.now().date(),
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
                        date_debut=datetime.now().date(),
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