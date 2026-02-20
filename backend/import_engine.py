import logging
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import yaml
import os
import unicodedata
from models import ImportProfile, ImportFieldMapping, Donnee, DonneeEnqueteur, Client, SherlockDonnee
from extensions import db

logger = logging.getLogger(__name__)


def normalize_column_name(name):
    """Normalise un nom de colonne en enlevant les accents et en mettant en majuscules"""
    if not name:
        return ""
    # Enlever les accents
    name_str = str(name)
    nfd = unicodedata.normalize('NFD', name_str)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    # Mettre en majuscules et enlever espaces superflus
    return without_accents.upper().strip()


def normalize_token(value):
    """Normalise une valeur en token ASCII majuscule sans sֳ©parateurs."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    nfd = unicodedata.normalize('NFD', text)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', without_accents.upper())


def is_urgency_marker(value):
    return normalize_token(value) in {'URGENT', 'URGENTE', 'URGENTS', 'URGENTES', 'URGENCE', 'URG'}


class ImportEngine:
    """Moteur d'import gֳ©nֳ©rique basֳ© sur les profils clients"""
    
    def __init__(self, import_profile, filename=None):
        """
        Initialise le moteur d'import
        
        Args:
            import_profile (ImportProfile): Profil d'import ֳ  utiliser
            filename (str, optional): Nom du fichier importֳ©
        """
        self.profile = import_profile
        self.filename = filename
        self.file_type = import_profile.file_type
        self.mappings = ImportFieldMapping.query.filter_by(
            import_profile_id=import_profile.id
        ).all()
        
        # Chargement de la config client spֳ©cifique (YAML) si existante
        self.client_config = self._load_client_config()
        
        for m in self.mappings:
            logger.info(f"Mapping: internal={m.internal_field}, external={m.column_name}, index={m.column_index}, required={m.is_required}")
        
        if not self.mappings and not self.client_config:
            raise ValueError(f"Aucun mapping trouvֳ© pour le profil d'import {import_profile.id}")
        
        logger.info(f"Moteur d'import initialisֳ© pour {import_profile.name} ({self.file_type})")
        if self.client_config:
            logger.info(f"Config spֳ©cifique client chargֳ©e depuis YAML")
        else:
            logger.info(f"{len(self.mappings)} mappings de champs chargֳ©s depuis la base")
            
    def _load_client_config(self):
        """Charge la configuration YAML du client si elle existe"""
        client = db.session.get(Client, self.profile.client_id)
        if not client:
            return None
            
        # Chercher dans backend/clients/<client_code>/mapping_import.yaml
        client_code = client.code.lower()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(base_dir, 'clients', client_code, 'mapping_import.yaml')
        
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement du YAML {yaml_path}: {e}")
                
        return None
    
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
        elif self.file_type == 'EXCEL_VERTICAL':
            return self._parse_excel_vertical(content)
        else:
            raise ValueError(f"Type de fichier non supportֳ©: {self.file_type}")
    
    def _parse_txt_fixed(self, content):
        """
        Parse un fichier TXT ֳ  positions fixes
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste de dictionnaires parsֳ©s
        """
        # Dֳ©codage du contenu
        text_content = self._decode_content(content)
        
        # Sֳ©paration des lignes
        lines = [line for line in text_content.splitlines() if line.strip()]
        logger.info(f"Traitement de {len(lines)} lignes (TXT_FIXED)")
        
        parsed_records = []
        
        for line_number, line in enumerate(lines, 1):
            try:
                record = {}
                
                for mapping in self.mappings:
                    value = mapping.extract_value(line, 'TXT_FIXED')
                    record[mapping.internal_field] = value
                
                # Vֳ©rifier les champs requis
                if not self._validate_required_fields(record, line_number):
                    continue
                
                parsed_records.append(record)
                
            except Exception as e:
                logger.error(f"Erreur ligne {line_number}: {e}")
                continue
        
        logger.info(f"{len(parsed_records)} enregistrements parsֳ©s avec succֳ¨s")
        return parsed_records
    
    def _parse_excel(self, content):
        """
        Parse un fichier Excel
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste de dictionnaires parsֳ©s
        """
        try:
            # Lire le fichier Excel avec pandas
            excel_data = BytesIO(content)
            
            # Charger le fichier pour inspecter les feuilles
            excel_obj = pd.ExcelFile(excel_data)
            available_sheets = excel_obj.sheet_names
            
            target_sheet = self.profile.sheet_name
            
            if target_sheet:
                if target_sheet in available_sheets:
                    df = pd.read_excel(excel_obj, sheet_name=target_sheet)
                else:
                    logger.warning(f"Feuille '{target_sheet}' introuvable dans {available_sheets}. Utilisation de la premiֳ¨re feuille.")
                    df = pd.read_excel(excel_obj, sheet_name=0)
            else:
                df = pd.read_excel(excel_obj, sheet_name=0)
            
            logger.info(f"Traitement de {len(df)} lignes (EXCEL)")
            logger.info(f"Colonnes disponibles: {list(df.columns)}")
            
            # Crֳ©er DEUX mappings pour gֳ©rer les accents:
            # 1. Mapping exact (garde les accents)
            # 2. Mapping normalisֳ© (enlֳ¨ve les accents pour compatibilitֳ©)
            col_map_exact = {str(col).strip(): col for col in df.columns}
            col_map_normalized = {normalize_column_name(col): col for col in df.columns}
            
            # Fusionner les deux (le mapping exact a prioritֳ©)
            col_map = {**col_map_normalized, **col_map_exact}
            
            logger.info(f"Colonnes Excel trouvֳ©es: {len(df.columns)}")
            logger.info(f"  - Exemples: {list(df.columns)[:5]}")
            
            parsed_records = []

            # Dֳ©terminer si on utilise le mapping YAML (client_config) ou les mappings DB
            use_yaml_mapping = bool(self.client_config and 'mappings' in self.client_config)
            if use_yaml_mapping:
                logger.info(f"Utilisation du mapping YAML client ({len(self.client_config['mappings'])} champs)")
            else:
                logger.info(f"Utilisation des mappings DB ({len(self.mappings)} champs)")

            for row_number, row in df.iterrows():
                try:
                    # Ignorer les lignes vides
                    if row.isna().all():
                        continue

                    if use_yaml_mapping:
                        # Convertir la row pandas en dict pour _apply_client_mapping
                        raw_record = {}
                        for col in df.columns:
                            val = row[col]
                            if pd.isna(val):
                                raw_record[str(col).strip()] = None
                            else:
                                raw_record[str(col).strip()] = str(val).strip()

                        record = self._apply_client_mapping(raw_record)
                    else:
                        record = {}
                        for mapping in self.mappings:
                            value = mapping.extract_value(row, 'EXCEL', col_map=col_map)
                            record[mapping.internal_field] = value

                    # Vֳ©rifier les champs requis
                    if not self._validate_required_fields(record, row_number + 2):  # +2 pour header et index 0
                        continue

                    parsed_records.append(record)

                except Exception as e:
                    logger.error(f"Erreur ligne {row_number + 2}: {e}")
                    logger.error(f"Contenu de la ligne: {row.to_dict()}")
                    continue
            
            logger.info(f"{len(parsed_records)} enregistrements parsֳ©s avec succֳ¨s")
            return parsed_records
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Excel: {e}")
            raise ValueError(f"Impossible de lire le fichier Excel: {e}")
            
    def _parse_excel_vertical(self, content):
        """
        Parse un fichier Excel vertical (format 2 colonnes Key/Value)
        
        Args:
            content (bytes): Contenu du fichier
            
        Returns:
            list[dict]: Liste d'enregistrements (avec champs internes)
        """
        try:
            excel_data = BytesIO(content)
            # Pas d'entֳ×te car format 2 colonnes Verticales
            df = pd.read_excel(excel_data, header=None)
            
            logger.info(f"Traitement d'un fichier Excel vertical ({len(df)} lignes)")
            
            # Rֳ©cupֳ©rer les clֳ©s connues pour dֳ©tecter un en-tֳ×te horizontal par erreur
            known_keys = set()
            if self.client_config and 'mappings' in self.client_config:
                known_keys = {m.get('source_key') for m in self.client_config['mappings']}
            
            # 1. Grouper en blocs (Raw Records)
            raw_records = []
            current_raw = {}
            split_key = "DossierId"
            
            for i, row in df.iterrows():
                if len(row) < 2:
                    continue
                    
                key = str(row[0]).strip() if pd.notna(row[0]) else ""
                if not key:
                    continue
                
                value = row[1]
                if pd.isna(value) or str(value).strip().lower() in ["", "nan", "none"]:
                    value = None
                else:
                    value = str(value).strip()
                
                # Robustesse : Dֳ©tection de header horizontal (si i=0, key est split_key mais value est un champ connu)
                if i == 0 and key == split_key and value in known_keys:
                    logger.warning(f"ג ן¸ Ligne 0 dֳ©tectֳ©e comme en-tֳ×te horizontal ({key} | {value}). Sautֳ©e.")
                    continue
                
                # Dֳ©tection de nouveau dossier
                if key == split_key and split_key in current_raw:
                    raw_records.append(current_raw)
                    current_raw = {}
                
                current_raw[key] = value
                
            if current_raw:
                raw_records.append(current_raw)
                
            logger.info(f"{len(raw_records)} dossiers bruts dֳ©tectֳ©s dans le fichier vertical")
            
            # 2. Mapper vers les champs internes en appliquant les transformations
            parsed_records = []
            for idx, raw in enumerate(raw_records, 1):
                record = self._apply_client_mapping(raw)
                
                # Vֳ©rifier les champs requis
                if not self._validate_required_fields(record, idx):
                    continue
                    
                parsed_records.append(record)
                
            logger.info(f"{len(parsed_records)} enregistrements verticaux mappֳ©s avec succֳ¨s")
            return parsed_records
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing Excel vertical: {e}")
            raise

    def _apply_client_mapping(self, raw_record):
        """Applique le mapping dֳ©fini dans le YAML si prֳ©sent, sinon mapping DB classique"""
        if not self.client_config or 'mappings' not in self.client_config:
            record = {}
            for mapping in self.mappings:
                val = raw_record.get(mapping.column_name)
                record[mapping.internal_field] = val
            return record

        # Crֳ©er un dictionnaire de mapping normalisֳ© pour gֳ©rer les accents
        # Mapping: nom_normalisֳ© ג†’ nom_original
        normalized_map = {normalize_column_name(k): k for k in raw_record.keys()}
        
        record = {}
        for m in self.client_config['mappings']:
            source_key = m.get('source_key')
            
            # Valeur source
            if source_key == "__COMPUTED_AD_L4__":
                value = self._compute_ad_l4(raw_record)
            else:
                # Essayer d'abord avec le nom exact
                value = raw_record.get(source_key)

                # Si pas trouvֳ©, essayer avec la normalisation (sans accents)
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    normalized_source = normalize_column_name(source_key)
                    original_key = normalized_map.get(normalized_source)
                    if original_key:
                        value = raw_record.get(original_key)

                # Si toujours pas trouvֳ©, essayer les alternative_keys du YAML
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    for alt_key in m.get('alternative_keys', []):
                        value = raw_record.get(alt_key)
                        if value is not None and not (isinstance(value, float) and pd.isna(value)):
                            break
                        # Essayer aussi la version normalisֳ©e de l'alternative
                        norm_alt = normalize_column_name(alt_key)
                        original_key = normalized_map.get(norm_alt)
                        if original_key:
                            value = raw_record.get(original_key)
                            if value is not None and not (isinstance(value, float) and pd.isna(value)):
                                break
            
            # Transformation
            transform_name = m.get('transform')
            if transform_name:
                value = self._execute_transform(value, transform_name)
            
            # Attribution au premier champ candidat
            for field in m.get('candidate_fields', []):
                if hasattr(Donnee, field):
                    record[field] = value
                    break
                elif hasattr(SherlockDonnee, field):
                    record[field] = value
                    break
        
        return record

    def _execute_transform(self, value, transform_name):
        """Exֳ©cute une transformation spֳ©cifiֳ©e sur une valeur"""
        if value is None:
            return None
            
        t = str(transform_name).lower()
        
        if t == "to_string":
            return str(value)
        elif t == "trim":
            return str(value).strip()
        elif t == "trim_upper":
            return str(value).strip().upper()
        elif t == "trim_lower":
            return str(value).strip().lower()
        elif t == "email_trim_lower":
            return str(value).strip().lower()
        elif t == "cp_string":
            # Garder les 5 premiers caractֳ¨res num
            res = re.sub(r'[^0-9]', '', str(value))
            return res[:5] if res else None
        elif t == "phone_sanitize":
            # Garder uniquement les chiffres
            return re.sub(r'[^0-9+]', '', str(value))
        elif t == "parse_date_ddmmyyyy":
            try:
                # Gֳ©rer divers formats de date via pandas
                return pd.to_datetime(value, dayfirst=True).date()
            except:
                return None
        elif "concat_ad_l4" in t:
            # Dֳ©jֳ  gֳ©rֳ© par _compute_ad_l4 car c'est un computed field complet
            return value
            
        return value

    def _compute_ad_l4(self, raw_record):
        """Calcule l'adresse ligne 4 ֳ  partir des composants num, type, voie"""
        num = raw_record.get("AD-L4 Numֳ©ro", "")
        type_voie = raw_record.get("AD-L4 Type", "")
        voie = raw_record.get("AD-L4 Voie", "")
        
        parts = [p for p in [num, type_voie, voie] if p and str(p).strip()]
        return " ".join(parts) if parts else None
    
    def _decode_content(self, content):
        """
        Dֳ©code le contenu avec l'encodage du profil
        
        Args:
            content (bytes): Contenu brut
            
        Returns:
            str: Contenu dֳ©codֳ©
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
                    logger.warning(f"Encodage {encoding} ֳ©chouֳ©, utilisation de {fallback}")
                    return result
                except UnicodeDecodeError:
                    continue
            
            # En dernier recours
            logger.error("Tous les encodages ont ֳ©chouֳ©, utilisation de utf-8 avec remplacement")
            return content.decode('utf-8', errors='replace')
    
    def _validate_required_fields(self, record, line_number):
        """
        Valide que les champs requis sont prֳ©sents

        Args:
            record (dict): Enregistrement parsֳ©
            line_number (int): Numֳ©ro de ligne pour logging

        Returns:
            bool: True si valide, False sinon
        """
        # Validation via mappings DB
        required_mappings = [m for m in self.mappings if m.is_required]

        for mapping in required_mappings:
            value = record.get(mapping.internal_field)
            if not value or not str(value).strip() or str(value).lower() == 'nan':
                # Pour numeroDossier, on peut ֳ×tre indulgent pour les contestations
                if mapping.internal_field == 'numeroDossier':
                    logger.info(f"Ligne {line_number}: 'numeroDossier' absent, continuֳ©...")
                    continue

                logger.warning(
                    f"Ligne {line_number}: Champ requis manquant '{mapping.internal_field}'"
                )
                logger.info(f"Record content: {record}")
                return False

        # Validation via YAML (si pas de mappings DB)
        if not required_mappings and self.client_config and 'mappings' in self.client_config:
            for m in self.client_config['mappings']:
                if m.get('required'):
                    for field in m.get('candidate_fields', []):
                        value = record.get(field)
                        if not value or not str(value).strip() or str(value).lower() == 'nan':
                            logger.warning(
                                f"Ligne {line_number}: Champ requis YAML manquant '{field}' (source: {m.get('source_key')})"
                            )
                            return False

        return True
    
    def create_donnee_from_record(self, record, fichier_id, client_id, date_butoir=None):
        """
        Crֳ©e une instance Donnee depuis un enregistrement parsֳ©
        
        Args:
            record (dict): Enregistrement parsֳ©
            fichier_id (int): ID du fichier
            client_id (int): ID du client
            date_butoir (date, optional): Date butoir
            
        Returns:
            Donnee: Instance de Donnee crֳ©ֳ©e
        """
        from utils import convert_date, convert_float

        # Nettoyer les valeurs 'nan'/'None' de pandas sur tous les champs string
        for key in list(record.keys()):
            if isinstance(record[key], str) and record[key].strip().lower() in ('nan', 'none'):
                record[key] = ''

        # Traitement spֳ©cial pour CLIENT_X
        record = self._preprocess_client_x_record(record, client_id)
        
        if client_id:
            from models.client import Client
            client = db.session.get(Client, client_id)
            if client and client.code == 'RG_SHERLOCK':
                return self._create_sherlock_donnee(record, fichier_id)

        # Detection automatique de contestation (PARTNER/CLIENT_X) via metadata de source.
        type_demande = record.get('typeDemande', '')
        if (not type_demande or type_demande == 'ENQ') and client_id:
            if client and client.code in ['CLIENT_X', 'PARTNER']:
                filename_upper = self.filename.upper().replace('-', ' ').replace('_', ' ') if self.filename else ''
                filename_token = normalize_token(self.filename) if self.filename else ''
                profile_name_token = normalize_token(getattr(self.profile, 'name', ''))
                profile_sheet_token = normalize_token(getattr(self.profile, 'sheet_name', ''))

                if (
                    'CONTESTATION' in filename_upper or
                    'CONTRE ENQUETE' in filename_upper or
                    'CRCONT' in filename_token or
                    'CONTESTATION' in filename_token or
                    'CONTREENQUETE' in filename_token or
                    'CONTEST' in profile_name_token or
                    'CONTRE' in profile_sheet_token
                ):
                    type_demande = 'CON'
                    record['typeDemande'] = 'CON'
                    logger.info(f"Detection CON via source import: {self.filename} / profil {self.profile.name}")

        # Contestation: normaliser les champs identite (supprimer URGENT du prenom, gerer nom+prenom fusionnes).
        if type_demande == 'CON':
            record = self._normalize_contestation_identity_record(record)
            record['typeDemande'] = 'CON'
        
        nouvelle_donnee = Donnee(
            client_id=client_id,
            fichier_id=fichier_id,
            numeroDossier=record.get('numeroDossier', ''),
            referenceDossier=record.get('referenceDossier', ''),
            numeroInterlocuteur=record.get('numeroInterlocuteur', ''),
            guidInterlocuteur=record.get('guidInterlocuteur', ''),
            typeDemande=type_demande,
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
            date_butoir=date_butoir or convert_date(record.get('date_butoir', '')),
            # Champs spֳ©cifiques PARTNER (ex-CLIENT_X)
            tarif_lettre=record.get('tarif_lettre'),
            recherche=record.get('recherche', '').strip() if record.get('recherche') else None,
            instructions=record.get('instructions', '').strip() if record.get('instructions') and str(record.get('instructions')).strip().lower() not in ('nan', 'none') else None,
            date_jour=convert_date(record.get('date_jour', '')),
            nom_complet=record.get('nom_complet'),
            motif=record.get('motif') if record.get('motif') and str(record.get('motif')).strip().lower() not in ('nan', 'none') else None
        )
        
        # Traiter les contestations
        if record.get('typeDemande') == 'CON':
            # IMPORTANT : Marquer TOUJOURS comme contestation si typeDemande = CON
            nouvelle_donnee.est_contestation = True
            nouvelle_donnee.typeDemande = 'CON'
            self._handle_contestation(nouvelle_donnee, record, client_id)
        
        # IMPORTANT: Flush pour obtenir l'ID avant de crֳ©er les PartnerCaseRequest
        db.session.add(nouvelle_donnee)
        db.session.flush()
        
        # Parse RECHERCHE pour PARTNER (crֳ©er les demandes)
        self._parse_recherche_if_partner(nouvelle_donnee, client_id)
        
        return nouvelle_donnee
    
    def _handle_contestation(self, nouvelle_donnee, record, client_id):
        """
        Gֳ¨re les logiques de contestation
        
        Args:
            nouvelle_donnee (Donnee): Nouvelle donnֳ©e de contestation
            record (dict): Enregistrement parsֳ©
            client_id (int): ID du client
        """
        contested_number = (record.get('numeroDemandeContestee') or '').strip()
        logger.info(f"Traitement contestation: {record.get('numeroDossier')}, conteste: {contested_number}")

        nom_recherche, prenom_recherche, nom_complet, date_naissance_record = (
            self._extract_contestation_identity(record)
        )
        matching_enquetes = self._find_same_identity_matches(
            client_id=client_id,
            nom_recherche=nom_recherche,
            prenom_recherche=prenom_recherche,
            nom_complet=nom_complet,
            date_naissance_record=date_naissance_record
        )
        nouvelle_donnee._matching_enquetes = matching_enquetes
        nouvelle_donnee._matching_identity = {
            'nom': nom_recherche or '',
            'prenom': prenom_recherche or '',
            'dateNaissance': date_naissance_record.strftime('%Y-%m-%d') if date_naissance_record else None
        }
        if matching_enquetes:
            logger.info(
                f"Contestation {record.get('numeroDossier')}: "
                f"{len(matching_enquetes)} enquete(s) avec meme identite trouvee(s)"
            )

        # Chercher l'enquֳ×te originale (dans le mֳ×me client)
        # IMPORTANT: Ne pas chercher si contested_number est vide pour ֳ©viter les faux positifs
        enquete_originale = None
        if contested_number:
            enquete_originale = Donnee.query.filter_by(
                client_id=client_id,
                numeroDossier=contested_number
            ).first()

            if not enquete_originale:
                enquete_originale = Donnee.query.filter_by(
                    client_id=client_id,
                    numeroDemande=contested_number
                ).first()

        # Fallback strict: seulement meme NOM + meme PRENOM (pas de rapprochement approximatif).
        if not enquete_originale and (nom_recherche or nom_complet):
            logger.info(
                f"Recherche enquete originale stricte (client={client_id}): "
                f"nom='{nom_recherche}' prenom='{prenom_recherche}' complet='{nom_complet}'"
            )

            nom_token = normalize_token(nom_recherche)
            prenom_token = normalize_token(prenom_recherche)

            if not nom_token or not prenom_token:
                logger.warning(
                    f"Recherche stricte impossible pour contestation {record.get('numeroDossier')} "
                    f"(nom='{nom_recherche}', prenom='{prenom_recherche}')."
                )
            else:
                def _strict_identity_match(candidat):
                    return (
                        normalize_token(candidat.nom) == nom_token and
                        normalize_token(candidat.prenom) == prenom_token
                    )

                def _date_is_compatible(candidat):
                    if not date_naissance_record:
                        return True
                    if not candidat.dateNaissance:
                        return True
                    return candidat.dateNaissance == date_naissance_record

                archived_candidates = Donnee.query.filter(
                    Donnee.client_id == client_id,
                    Donnee.est_contestation == False,
                    Donnee.statut_validation.in_(['archive', 'archivee', 'valide', 'validee'])
                ).order_by(Donnee.updated_at.desc()).all()

                strict_archived = [
                    c for c in archived_candidates
                    if _strict_identity_match(c) and _date_is_compatible(c)
                ]
                if strict_archived:
                    enquete_originale = strict_archived[0]
                    logger.info(
                        f"Enquete originale trouvee (strict archives): ID {enquete_originale.id} "
                        f"- {enquete_originale.nom} {enquete_originale.prenom}"
                    )

                if not enquete_originale:
                    all_candidates = Donnee.query.filter(
                        Donnee.client_id == client_id,
                        Donnee.est_contestation == False
                    ).order_by(Donnee.updated_at.desc()).all()

                    strict_all = [
                        c for c in all_candidates
                        if _strict_identity_match(c) and _date_is_compatible(c)
                    ]
                    if strict_all:
                        enquete_originale = strict_all[0]
                        logger.info(
                            f"Enquete originale trouvee (strict tous statuts): ID {enquete_originale.id} "
                            f"- {enquete_originale.nom} {enquete_originale.prenom}"
                        )
             
        if enquete_originale:
            logger.info(f"Enquֳ×te originale trouvֳ©e: {enquete_originale.numeroDossier} (ID: {enquete_originale.id})")
            
            # Conserver les valeurs spֳ©cifiques de la contestation importֳ©e.
            preserved_date_butoir = nouvelle_donnee.date_butoir
            preserved_code_motif = nouvelle_donnee.codeMotif
            preserved_motif_detail = nouvelle_donnee.motifDeContestation

            # Complֳ©ter uniquement les champs manquants depuis la table donnees (et non donnees_enqueteur).
            copied_fields_count = self._copy_missing_fields_from_original_donnee(
                nouvelle_donnee,
                enquete_originale
            )

            # Rֳ©appliquer explicitement les champs contestation ֳ  conserver.
            nouvelle_donnee.date_butoir = preserved_date_butoir
            nouvelle_donnee.codeMotif = preserved_code_motif
            nouvelle_donnee.motifDeContestation = preserved_motif_detail

            nouvelle_donnee.est_contestation = True
            nouvelle_donnee.enquete_originale_id = enquete_originale.id
            nouvelle_donnee.date_contestation = datetime.now().date()
            nouvelle_donnee.motif_contestation_code = record.get('codeMotif', '')
            nouvelle_donnee.motif_contestation_detail = record.get('motifDeContestation', '')
            nouvelle_donnee.enqueteurId = enquete_originale.enqueteurId

            if copied_fields_count:
                logger.info(
                    f"Contestation {nouvelle_donnee.numeroDossier}: "
                    f"{copied_fields_count} champ(s) completes depuis donnees (originale ID {enquete_originale.id})"
                )
            
            # Historique
            if hasattr(enquete_originale, 'add_to_history'):
                enquete_originale.add_to_history(
                    'contestation',
                    f"Contestation reֳ§ue: {nouvelle_donnee.numeroDossier}. Motif: {nouvelle_donnee.motif_contestation_detail}",
                    'Systֳ¨me d\'import'
                )
            
            db.session.add(enquete_originale)
        else:
            logger.warning(f"Enquֳ×te originale non trouvֳ©e pour contestation {record.get('numeroDossier')}, dossier contestֳ©: {contested_number}")
        
        if hasattr(nouvelle_donnee, 'add_to_history'):
            matching_ids = [str(m.get('id')) for m in matching_enquetes]
            matching_detail = (
                f" | Identites correspondantes (nom+prenom+date): {', '.join(matching_ids)}"
                if matching_ids else ""
            )
            nouvelle_donnee.add_to_history(
                'creation',
                f"Contestation de l'enquֳ×te {contested_number}{matching_detail}",
                'Systֳ¨me d\'import'
            )

    def _normalize_contestation_identity_record(self, record):
        """
        Normalise les champs identite d'une contestation.
        - retire les marqueurs d'urgence (URGENT...) du prenom/nom_complet
        - reconstruit nom/prenom si le nom complet est dans un seul champ
        """
        nom_raw = str(record.get('nom') or '').strip()
        prenom_raw = str(record.get('prenom') or '').strip()
        nom_complet_raw = str(record.get('nom_complet') or '').strip()
        prenom_was_only_urgency = bool(prenom_raw) and is_urgency_marker(prenom_raw)

        def remove_urgency_tokens(text):
            if not text:
                return '', False
            tokens = [tok for tok in re.split(r'\s+', text.strip()) if tok]
            kept = []
            removed = False
            for tok in tokens:
                if is_urgency_marker(tok):
                    removed = True
                else:
                    kept.append(tok)
            return ' '.join(kept).strip(), removed

        nom_clean, nom_had_urgency = remove_urgency_tokens(nom_raw)
        prenom_clean, prenom_had_urgency = remove_urgency_tokens(prenom_raw)
        nom_complet_clean, full_had_urgency = remove_urgency_tokens(nom_complet_raw)
        had_urgency = nom_had_urgency or prenom_had_urgency or full_had_urgency

        # Choisir une source nom complet.
        if nom_complet_clean:
            combined = nom_complet_clean
        elif nom_clean and prenom_clean and prenom_clean.upper() not in nom_clean.upper():
            combined = f"{nom_clean} {prenom_clean}".strip()
        else:
            combined = nom_clean or prenom_clean

        parts = [p for p in combined.split() if p]

        # Cas: nom vide, prenom contient en fait "NOM PRENOM"
        if not nom_raw and prenom_clean and len(parts) >= 2:
            nom_clean = parts[0]
            prenom_clean = ' '.join(parts[1:])
        else:
            if not nom_clean and len(parts) >= 1:
                nom_clean = parts[0]
            if (not prenom_clean or is_urgency_marker(prenom_clean)) and len(parts) >= 2:
                prenom_clean = ' '.join(parts[1:])

        # Cas: NOM contient "NOM PRENOM" et prenom vide/urgent
        nom_parts = [p for p in nom_clean.split() if p]
        if (
            (not prenom_clean or is_urgency_marker(prenom_clean) or prenom_was_only_urgency) and
            len(nom_parts) >= 2
        ):
            nom_clean = nom_parts[0]
            prenom_clean = ' '.join(nom_parts[1:])
            combined = f"{nom_clean} {prenom_clean}".strip()

        if had_urgency:
            record['urgence'] = '1'

        record['nom'] = nom_clean
        record['prenom'] = prenom_clean
        record['nom_complet'] = combined or None

        return record

    def _is_blank_import_value(self, value):
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ''
        return False

    def _copy_missing_fields_from_original_donnee(self, target_donnee, original_donnee):
        """
        Copie uniquement les champs manquants depuis l'enquete originale (table donnees).
        Ne copie pas les champs specifique contestation (motif/date butoir/identifiants contestation).
        """
        fields_to_fill = [
            'referenceDossier',
            'numeroInterlocuteur',
            'guidInterlocuteur',
            'forfaitDemande',
            'dateRetourEspere',
            'qualite',
            'nom',
            'prenom',
            'dateNaissance',
            'lieuNaissance',
            'codePostalNaissance',
            'paysNaissance',
            'nomPatronymique',
            'adresse1',
            'adresse2',
            'adresse3',
            'adresse4',
            'ville',
            'codePostal',
            'paysResidence',
            'telephonePersonnel',
            'telephoneEmployeur',
            'telecopieEmployeur',
            'nomEmployeur',
            'banqueDomiciliation',
            'libelleGuichet',
            'titulaireCompte',
            'codeBanque',
            'codeGuichet',
            'numeroCompte',
            'ribCompte',
            'elementDemandes',
            'elementObligatoires',
            'elementContestes',
            'codesociete',
            'commentaire'
        ]

        copied_count = 0
        for field_name in fields_to_fill:
            target_value = getattr(target_donnee, field_name, None)
            if not self._is_blank_import_value(target_value):
                continue

            source_value = getattr(original_donnee, field_name, None)
            if self._is_blank_import_value(source_value):
                continue

            setattr(target_donnee, field_name, source_value)
            copied_count += 1

        return copied_count

    def _extract_contestation_identity(self, record):
        """Construit une identite exploitable (nom/prenom/date) depuis un record contestation."""
        from utils import convert_date

        nom_source = (record.get('nom') or '').strip()
        prenom_source = (record.get('prenom') or '').strip()
        nom_complet_source = (record.get('nom_complet') or '').strip()

        # Cas frֳ©quent contestation: nom+prenom dans une seule cellule (nom_complet).
        if not nom_source and nom_complet_source:
            nom_source = nom_complet_source

        # Normaliser sֳ©parateurs avant split.
        if nom_complet_source:
            nom_complet = re.sub(r'[,;|/_-]+', ' ', nom_complet_source).strip()
        elif (
            prenom_source and
            not is_urgency_marker(prenom_source) and
            prenom_source.upper() not in nom_source.upper()
        ):
            nom_complet = f"{nom_source} {prenom_source}".strip()
        else:
            nom_complet = nom_source

        parts = [p for p in nom_complet.split() if p and not is_urgency_marker(p)]
        nom_recherche = nom_source
        prenom_recherche = prenom_source

        # Si prenom absent (ou urgent), reconstruire depuis le champ complet.
        if (not prenom_recherche or is_urgency_marker(prenom_recherche)) and len(parts) >= 2:
            nom_recherche = parts[0]
            prenom_recherche = ' '.join(parts[1:])
        elif not nom_recherche and len(parts) >= 1:
            nom_recherche = parts[0]
            prenom_recherche = ' '.join(parts[1:]) if len(parts) > 1 else prenom_recherche

        return nom_recherche, prenom_recherche, nom_complet, convert_date(record.get('dateNaissance'))

    def _find_same_identity_matches(self, client_id, nom_recherche, prenom_recherche, nom_complet, date_naissance_record):
        """
        Retourne toutes les enquetes non contestation avec meme nom+prenom+date de naissance.
        """
        if not client_id or not date_naissance_record:
            return []

        candidats = Donnee.query.filter(
            Donnee.client_id == client_id,
            Donnee.est_contestation == False,
            Donnee.dateNaissance == date_naissance_record
        ).all()

        nom_norm = normalize_token(nom_recherche)
        prenom_norm = normalize_token(prenom_recherche)
        nom_complet_norm = normalize_token(nom_complet)
        matches = []
        seen = set()

        for candidat in candidats:
            c_nom_norm = normalize_token(candidat.nom)
            c_prenom_norm = normalize_token(candidat.prenom)
            same_order = nom_norm == c_nom_norm and prenom_norm == c_prenom_norm
            swapped_order = nom_norm == c_prenom_norm and prenom_norm == c_nom_norm
            full_match = nom_complet_norm and (
                nom_complet_norm == normalize_token(f"{candidat.nom or ''} {candidat.prenom or ''}") or
                nom_complet_norm == normalize_token(f"{candidat.prenom or ''} {candidat.nom or ''}")
            )

            if not (same_order or swapped_order or full_match):
                continue
            if candidat.id in seen:
                continue

            seen.add(candidat.id)
            matches.append({
                'id': candidat.id,
                'numeroDossier': candidat.numeroDossier,
                'numeroDemande': candidat.numeroDemande,
                'nom': candidat.nom,
                'prenom': candidat.prenom,
                'dateNaissance': candidat.dateNaissance.strftime('%Y-%m-%d') if candidat.dateNaissance else None,
                'statut_validation': candidat.statut_validation,
                'enqueteurId': candidat.enqueteurId
            })

        matches.sort(key=lambda item: (item.get('numeroDossier') or '', item.get('id') or 0))
        return matches
    
    def _preprocess_client_x_record(self, record, client_id):
        """
        Prֳ©traite les enregistrements CLIENT_X/PARTNER avec logiques spֳ©cifiques
        
        Args:
            record (dict): Enregistrement parsֳ©
            client_id (int): ID du client
            
        Returns:
            dict: Enregistrement prֳ©traitֳ©
        """
        from models.client import Client
        
        # Vֳ©rifier si c'est CLIENT_X ou PARTNER
        client = db.session.get(Client, client_id)
        if not client or client.code not in ['CLIENT_X', 'PARTNER']:
            return record

        # Contestations PARTNER: normaliser identitֳ© et urgence.
        if record.get('typeDemande') == 'CON':
            nom_raw = str(record.get('nom') or '').strip()
            prenom_raw = str(record.get('prenom') or '').strip()
            nom_complet_raw = str(record.get('nom_complet') or '').strip()

            # Si seul nom_complet est fourni (profil contestation), le dֳ©couper en nom/prֳ©nom.
            if not nom_raw and nom_complet_raw:
                parts = [p for p in nom_complet_raw.split() if p]
                if parts:
                    record['nom'] = parts[0]
                    record['prenom'] = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    nom_raw = record['nom']
                    prenom_raw = record['prenom']

            # Cas observֳ©: PRENOM contient "URGENT" dans le fichier contestation.
            if is_urgency_marker(prenom_raw):
                nom_parts = [p for p in nom_raw.split() if p]
                if len(nom_parts) >= 2:
                    record['nom_complet'] = record.get('nom_complet') or nom_raw
                    record['nom'] = nom_parts[0]
                    record['prenom'] = ' '.join(nom_parts[1:])
                else:
                    record['prenom'] = ''
                record['urgence'] = '1'
                logger.info(
                    f"Contestation PARTNER: PRENOM='{prenom_raw}' interprֳ©tֳ© comme urgence "
                    f"pour nom='{nom_raw}'."
                )
        
        # 1. Combiner JOUR/MOIS/ANNEE en dateNaissance
        # Les 3 champs peuvent ֳ×tre sֳ©parֳ©s dans l'import Excel PARTNER
        jour_raw = record.get('dateNaissance', '')
        mois_raw = record.get('dateNaissance_mois', '')
        annee_raw = record.get('dateNaissance_annee', '')
        
        # Nettoyer et convertir (gֳ©rer float pandas: 27.0 -> "27")
        def clean_date_part(value):
            """Convertit valeur Excel (float/str) en string propre"""
            if value is None or str(value).strip() in ('', 'nan', 'NaN', 'None'):
                return None
            try:
                # Si c'est un float (ex: 27.0), convertir en int puis string
                return str(int(float(value)))
            except (ValueError, TypeError):
                return str(value).strip()
        
        jour = clean_date_part(jour_raw)
        mois = clean_date_part(mois_raw)
        annee = clean_date_part(annee_raw)
        
        logger.info(f"Date naissance PARTNER - JOUR:{jour} MOIS:{mois} ANNEE:{annee}")
        
        if jour and mois and annee:
            try:
                # Valider les valeurs
                j = int(jour)
                m = int(mois)
                a = int(annee)
                if 1 <= j <= 31 and 1 <= m <= 12 and 1900 <= a <= 2100:
                    # Format: DD/MM/YYYY pour convert_date()
                    record['dateNaissance'] = f"{str(j).zfill(2)}/{str(m).zfill(2)}/{a}"
                    logger.info(f"ג… Date de naissance combinֳ©e: {record['dateNaissance']}")
                else:
                    logger.warning(f"ג ן¸ Date invalide ignorֳ©e: {j}/{m}/{a}")
                    record['dateNaissance'] = None
            except Exception as e:
                logger.warning(f"ג ן¸ Erreur combinaison date: {jour}/{mois}/{annee} - {e}")
                record['dateNaissance'] = None
        else:
            # Si l'un des 3 manque, laisser NULL
            record['dateNaissance'] = None
            if jour or mois or annee:
                logger.warning(f"ג ן¸ Date incomplֳ¨te (JOUR:{jour}, MOIS:{mois}, ANNEE:{annee})")
        
        # 2. Normaliser le code postal (zfill(5))
        if 'codePostal' in record and record.get('codePostal'):
            cp = str(record['codePostal']).strip()
            if cp and cp.isdigit():
                record['codePostal'] = cp.zfill(5)
        
        # 3. Nettoyer le tֳ©lֳ©phone (null si "0")
        if 'telephonePersonnel' in record:
            tel = str(record.get('telephonePersonnel', '')).strip()
            if tel == '0' or tel == '':
                record['telephonePersonnel'] = None
        
        # 4. Gֳ©rer l'urgence pour contestations
        # Note: L'urgence doit venir d'un champ dֳ©diֳ© 'urgence', pas du prֳ©nom
        if record.get('typeDemande') == 'CON':
            # Si un champ 'urgence' existe explicitement, l'utiliser
            if 'urgence' in record:
                urgence_value = str(record.get('urgence', '')).strip().upper()
                if urgence_value in ['URGENT', '1', 'O', 'OUI', 'YES']:
                    record['urgence'] = '1'  # True
                else:
                    record['urgence'] = '0'  # False
            # Sinon, laisser vide (pas d'urgence par dֳ©faut)
            elif 'urgence' not in record:
                record['urgence'] = '0'  # Pas d'urgence par dֳ©faut

        # 5. Conserver une version assemblֳ©e NOM + PRENOM pour faciliter les rapprochements contestation.
        nom_raw = str(record.get('nom') or '').strip()
        prenom_raw = str(record.get('prenom') or '').strip()
        nom_parts = [p for p in nom_raw.split() if p]
        if not record.get('nom_complet'):
            if len(nom_parts) >= 2:
                record['nom_complet'] = nom_raw
            elif nom_raw and prenom_raw and prenom_raw.upper() not in nom_raw.upper():
                record['nom_complet'] = f"{nom_raw} {prenom_raw}".strip()
            else:
                record['nom_complet'] = nom_raw or prenom_raw or None
        
        return record
    
    def _parse_recherche_if_partner(self, donnee, client_id):
        """
        Parse le champ RECHERCHE pour PARTNER et crֳ©e les demandes
        
        Args:
            donnee (Donnee): Instance de Donnee (DOIT avoir un ID - aprֳ¨s flush)
            client_id (int): ID du client
        """
        from models.client import Client
        from models.partner_models import PartnerCaseRequest
        from services.partner_request_parser import PartnerRequestParser
        
        # Vֳ©rifier si c'est PARTNER
        client = db.session.get(Client, client_id)
        if not client or client.code not in ['CLIENT_X', 'PARTNER']:
            return
        
        # Vֳ©rifier si RECHERCHE existe
        if not donnee.recherche or not donnee.recherche.strip():
            logger.info(f"Pas de RECHERCHE pour donnee {donnee.numeroDossier}, skip parsing")
            return
        
        # Vֳ©rifier que donnee a un ID (doit ֳ×tre flushed avant)
        if not donnee.id:
            logger.error(f"ERREUR: donnee.id est None, impossible de crֳ©er les PartnerCaseRequest")
            return
        
        # Parser RECHERCHE
        detected_requests = PartnerRequestParser.parse_recherche(donnee.recherche, client_id)
        
        if not detected_requests:
            logger.warning(f"Aucune demande dֳ©tectֳ©e dans RECHERCHE: '{donnee.recherche}'")
            return
        
        # Crֳ©er les PartnerCaseRequest
        logger.info(f"Crֳ©ation de {len(detected_requests)} demandes pour donnee {donnee.id} ({donnee.numeroDossier})")
        
        for request_code in detected_requests:
            # Vֳ©rifier si existe dֳ©jֳ 
            existing = PartnerCaseRequest.query.filter_by(
                donnee_id=donnee.id,
                request_code=request_code
            ).first()
            
            if not existing:
                new_request = PartnerCaseRequest(
                    donnee_id=donnee.id,
                    request_code=request_code,
                    requested=True,
                    found=False,  # Sera calculֳ© plus tard
                    status='NEG'  # Sera calculֳ© plus tard
                )
                db.session.add(new_request)
                logger.info(f"  ג†’ PartnerCaseRequest crֳ©ֳ©: {request_code}")
            else:
                logger.info(f"  ג†’ PartnerCaseRequest existe dֳ©jֳ : {request_code}")

    def _create_sherlock_donnee(self, record, fichier_id):
        """Crֳ©e une instance SherlockDonnee"""
        from utils import convert_float
        
        # Mapper les champs record -> SherlockDonnee
        # On suppose que les internal_fields dans le YAML correspondent aux attributs de SherlockDonnee
        
        # Prֳ©parer les donnֳ©es en convertissant les valeurs numֳ©riques correctement
        donnee_data = {}
        for k, v in record.items():
            if hasattr(SherlockDonnee, k):
                # Convertir les champs Float avec la fonction convert_float
                if k == 'montant_ht':
                    donnee_data[k] = convert_float(v)
                else:
                    donnee_data[k] = v
        
        nouvelle_donnee = SherlockDonnee(
            fichier_id=fichier_id,
            **donnee_data
        )
        
        db.session.add(nouvelle_donnee)
        return nouvelle_donnee
