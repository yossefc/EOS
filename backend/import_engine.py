"""
Moteur d'import générique pour traiter les fichiers selon les profils clients
Supporte TXT à positions fixes et Excel
"""
import logging
import pandas as pd
from io import BytesIO
from datetime import datetime
from models import ImportProfile, ImportFieldMapping, Donnee, DonneeEnqueteur
from extensions import db

logger = logging.getLogger(__name__)


class ImportEngine:
    """Moteur d'import générique basé sur les profils clients"""
    
    def __init__(self, import_profile):
        """
        Initialise le moteur d'import
        
        Args:
            import_profile (ImportProfile): Profil d'import à utiliser
        """
        self.profile = import_profile
        self.file_type = import_profile.file_type
        self.mappings = ImportFieldMapping.query.filter_by(
            import_profile_id=import_profile.id
        ).all()
        
        if not self.mappings:
            raise ValueError(f"Aucun mapping trouvé pour le profil d'import {import_profile.id}")
        
        logger.info(f"Moteur d'import initialisé pour {import_profile.name} ({self.file_type})")
        logger.info(f"{len(self.mappings)} mappings de champs chargés")
    
    def parse_content(self, content):
        """
        Parse le contenu du fichier selon le type
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste de dictionnaires {internal_field: valeur}
        """
        if self.file_type == 'TXT_FIXED':
            return self._parse_txt_fixed(content)
        elif self.file_type == 'EXCEL':
            return self._parse_excel(content)
        else:
            raise ValueError(f"Type de fichier non supporté: {self.file_type}")
    
    def _parse_txt_fixed(self, content):
        """
        Parse un fichier TXT à positions fixes
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste de dictionnaires parsés
        """
        # Décodage du contenu
        text_content = self._decode_content(content)
        
        # Séparation des lignes
        lines = [line for line in text_content.splitlines() if line.strip()]
        logger.info(f"Traitement de {len(lines)} lignes (TXT_FIXED)")
        
        parsed_records = []
        
        for line_number, line in enumerate(lines, 1):
            try:
                record = {}
                
                for mapping in self.mappings:
                    value = mapping.extract_value(line, 'TXT_FIXED')
                    record[mapping.internal_field] = value
                
                # Vérifier les champs requis
                if not self._validate_required_fields(record, line_number):
                    continue
                
                parsed_records.append(record)
                
            except Exception as e:
                logger.error(f"Erreur ligne {line_number}: {e}")
                continue
        
        logger.info(f"{len(parsed_records)} enregistrements parsés avec succès")
        return parsed_records
    
    def _parse_excel(self, content):
        """
        Parse un fichier Excel
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste de dictionnaires parsés
        """
        try:
            # Lire le fichier Excel avec pandas
            excel_file = BytesIO(content)
            
            if self.profile.sheet_name:
                df = pd.read_excel(excel_file, sheet_name=self.profile.sheet_name)
            else:
                df = pd.read_excel(excel_file)
            
            logger.info(f"Traitement de {len(df)} lignes (EXCEL)")
            
            parsed_records = []
            
            for row_number, row in df.iterrows():
                try:
                    record = {}
                    
                    for mapping in self.mappings:
                        value = mapping.extract_value(row, 'EXCEL')
                        record[mapping.internal_field] = value
                    
                    # Vérifier les champs requis
                    if not self._validate_required_fields(record, row_number + 2):  # +2 pour header et index 0
                        continue
                    
                    parsed_records.append(record)
                    
                except Exception as e:
                    logger.error(f"Erreur ligne {row_number + 2}: {e}")
                    continue
            
            logger.info(f"{len(parsed_records)} enregistrements parsés avec succès")
            return parsed_records
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Excel: {e}")
            raise ValueError(f"Impossible de lire le fichier Excel: {e}")
    
    def _decode_content(self, content):
        """
        Décode le contenu avec l'encodage du profil
        
        Args:
            content (bytes): Contenu brut
            
        Returns:
            str: Contenu décodé
        """
        if isinstance(content, str):
            return content
        
        encoding = self.profile.encoding or 'utf-8'
        
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            # Essayer d'autres encodages courants
            fallback_encodings = ['latin1', 'iso-8859-1', 'cp1252', 'utf-8']
            
            for fallback in fallback_encodings:
                if fallback == encoding:
                    continue
                try:
                    result = content.decode(fallback)
                    logger.warning(f"Encodage {encoding} échoué, utilisation de {fallback}")
                    return result
                except UnicodeDecodeError:
                    continue
            
            # En dernier recours
            logger.error("Tous les encodages ont échoué, utilisation de utf-8 avec remplacement")
            return content.decode('utf-8', errors='replace')
    
    def _validate_required_fields(self, record, line_number):
        """
        Valide que les champs requis sont présents
        
        Args:
            record (dict): Enregistrement parsé
            line_number (int): Numéro de ligne pour logging
            
        Returns:
            bool: True si valide, False sinon
        """
        required_mappings = [m for m in self.mappings if m.is_required]
        
        for mapping in required_mappings:
            value = record.get(mapping.internal_field)
            if not value or not str(value).strip():
                logger.warning(
                    f"Ligne {line_number}: Champ requis manquant '{mapping.internal_field}'"
                )
                return False
        
        return True
    
    def create_donnee_from_record(self, record, fichier_id, client_id, date_butoir=None):
        """
        Crée une instance Donnee depuis un enregistrement parsé
        
        Args:
            record (dict): Enregistrement parsé
            fichier_id (int): ID du fichier
            client_id (int): ID du client
            date_butoir (date, optional): Date butoir
            
        Returns:
            Donnee: Instance de Donnee créée
        """
        from utils import convert_date, convert_float
        
        nouvelle_donnee = Donnee(
            client_id=client_id,
            fichier_id=fichier_id,
            numeroDossier=record.get('numeroDossier', ''),
            referenceDossier=record.get('referenceDossier', ''),
            numeroInterlocuteur=record.get('numeroInterlocuteur', ''),
            guidInterlocuteur=record.get('guidInterlocuteur', ''),
            typeDemande=record.get('typeDemande', ''),
            numeroDemande=record.get('numeroDemande', ''),
            numeroDemandeContestee=record.get('numeroDemandeContestee', ''),
            numeroDemandeInitiale=record.get('numeroDemandeInitiale', ''),
            forfaitDemande=record.get('forfaitDemande', ''),
            dateRetourEspere=convert_date(record.get('dateRetourEspere', '')),
            qualite=record.get('qualite', ''),
            nom=record.get('nom', ''),
            prenom=record.get('prenom', ''),
            dateNaissance=convert_date(record.get('dateNaissance', '')),
            lieuNaissance=record.get('lieuNaissance', ''),
            codePostalNaissance=record.get('codePostalNaissance', ''),
            paysNaissance=record.get('paysNaissance', ''),
            nomPatronymique=record.get('nomPatronymique', ''),
            adresse1=record.get('adresse1', ''),
            adresse2=record.get('adresse2', ''),
            adresse3=record.get('adresse3', ''),
            adresse4=record.get('adresse4', ''),
            ville=record.get('ville', ''),
            codePostal=record.get('codePostal', ''),
            paysResidence=record.get('paysResidence', ''),
            telephonePersonnel=record.get('telephonePersonnel', ''),
            telephoneEmployeur=record.get('telephoneEmployeur', ''),
            telecopieEmployeur=record.get('telecopieEmployeur', ''),
            nomEmployeur=record.get('nomEmployeur', ''),
            banqueDomiciliation=record.get('banqueDomiciliation', ''),
            libelleGuichet=record.get('libelleGuichet', ''),
            titulaireCompte=record.get('titulaireCompte', ''),
            codeBanque=record.get('codeBanque', ''),
            codeGuichet=record.get('codeGuichet', ''),
            numeroCompte=record.get('numeroCompte', ''),
            ribCompte=record.get('ribCompte', ''),
            datedenvoie=convert_date(record.get('datedenvoie', '')),
            elementDemandes=record.get('elementDemandes', ''),
            elementObligatoires=record.get('elementObligatoires', ''),
            elementContestes=record.get('elementContestes', ''),
            codeMotif=record.get('codeMotif', ''),
            motifDeContestation=record.get('motifDeContestation', ''),
            cumulMontantsPrecedents=convert_float(record.get('cumulMontantsPrecedents', '')),
            codesociete=record.get('codeSociete', '') or record.get('codesociete', ''),
            urgence=record.get('urgence', ''),
            commentaire=record.get('commentaire', ''),
            date_butoir=date_butoir
        )
        
        # Traiter les contestations
        if record.get('typeDemande') == 'CON':
            self._handle_contestation(nouvelle_donnee, record, client_id)
        
        return nouvelle_donnee
    
    def _handle_contestation(self, nouvelle_donnee, record, client_id):
        """
        Gère les logiques de contestation
        
        Args:
            nouvelle_donnee (Donnee): Nouvelle donnée de contestation
            record (dict): Enregistrement parsé
            client_id (int): ID du client
        """
        contested_number = record.get('numeroDemandeContestee', '')
        logger.info(f"Traitement contestation: {record.get('numeroDossier')}, conteste: {contested_number}")
        
        # Chercher l'enquête originale (dans le même client)
        enquete_originale = Donnee.query.filter_by(
            client_id=client_id,
            numeroDossier=contested_number
        ).first()
        
        if not enquete_originale:
            enquete_originale = Donnee.query.filter_by(
                client_id=client_id,
                numeroDemande=contested_number
            ).first()
        
        if enquete_originale:
            logger.info(f"Enquête originale trouvée: {enquete_originale.numeroDossier} (ID: {enquete_originale.id})")
            
            nouvelle_donnee.est_contestation = True
            nouvelle_donnee.enquete_originale_id = enquete_originale.id
            nouvelle_donnee.date_contestation = datetime.now().date()
            nouvelle_donnee.motif_contestation_code = record.get('codeMotif', '')
            nouvelle_donnee.motif_contestation_detail = record.get('motifDeContestation', '')
            nouvelle_donnee.enqueteurId = enquete_originale.enqueteurId
            
            # Historique
            if hasattr(enquete_originale, 'add_to_history'):
                enquete_originale.add_to_history(
                    'contestation',
                    f"Contestation reçue: {nouvelle_donnee.numeroDossier}. Motif: {nouvelle_donnee.motif_contestation_detail}",
                    'Système d\'import'
                )
            
            db.session.add(enquete_originale)
        else:
            logger.warning(f"Enquête originale non trouvée pour contestation {record.get('numeroDossier')}, dossier contesté: {contested_number}")
        
        if hasattr(nouvelle_donnee, 'add_to_history'):
            nouvelle_donnee.add_to_history(
                'creation',
                f"Contestation de l'enquête {contested_number}",
                'Système d\'import'
            )


