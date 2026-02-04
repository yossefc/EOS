import logging
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import yaml
import os
from models import ImportProfile, ImportFieldMapping, Donnee, DonneeEnqueteur, Client, SherlockDonnee
from extensions import db

logger = logging.getLogger(__name__)


class ImportEngine:
    """Moteur d'import générique basé sur les profils clients"""
    
    def __init__(self, import_profile, filename=None):
        """
        Initialise le moteur d'import
        
        Args:
            import_profile (ImportProfile): Profil d'import à utiliser
            filename (str, optional): Nom du fichier importé
        """
        self.profile = import_profile
        self.filename = filename
        self.file_type = import_profile.file_type
        self.mappings = ImportFieldMapping.query.filter_by(
            import_profile_id=import_profile.id
        ).all()
        
        # Chargement de la config client spécifique (YAML) si existante
        self.client_config = self._load_client_config()
        
        for m in self.mappings:
            logger.info(f"Mapping: internal={m.internal_field}, external={m.column_name}, index={m.column_index}, required={m.is_required}")
        
        if not self.mappings and not self.client_config:
            raise ValueError(f"Aucun mapping trouvé pour le profil d'import {import_profile.id}")
        
        logger.info(f"Moteur d'import initialisé pour {import_profile.name} ({self.file_type})")
        if self.client_config:
            logger.info(f"Config spécifique client chargée depuis YAML")
        else:
            logger.info(f"{len(self.mappings)} mappings de champs chargés depuis la base")
            
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
            excel_data = BytesIO(content)
            
            # Charger le fichier pour inspecter les feuilles
            excel_obj = pd.ExcelFile(excel_data)
            available_sheets = excel_obj.sheet_names
            
            target_sheet = self.profile.sheet_name
            
            if target_sheet:
                if target_sheet in available_sheets:
                    df = pd.read_excel(excel_obj, sheet_name=target_sheet)
                else:
                    logger.warning(f"Feuille '{target_sheet}' introuvable dans {available_sheets}. Utilisation de la première feuille.")
                    df = pd.read_excel(excel_obj, sheet_name=0)
            else:
                df = pd.read_excel(excel_obj, sheet_name=0)
            
            logger.info(f"Traitement de {len(df)} lignes (EXCEL)")
            logger.info(f"Colonnes disponibles: {list(df.columns)}")
            
            # Créer un dictionnaire de mapping pour les colonnes Excel (insensible à la casse/espaces)
            # Pour chaque colonne réelle, on stocke une clé normalisée
            col_map = {str(col).strip().upper(): col for col in df.columns}
            
            parsed_records = []
            
            for row_number, row in df.iterrows():
                try:
                    # Ignorer les lignes vides
                    if row.isna().all():
                        continue
                    
                    record = {}
                    
                    for mapping in self.mappings:
                        value = mapping.extract_value(row, 'EXCEL', col_map=col_map)
                        record[mapping.internal_field] = value
                    
                    # Vérifier les champs requis
                    if not self._validate_required_fields(record, row_number + 2):  # +2 pour header et index 0
                        continue
                    
                    parsed_records.append(record)
                    
                except Exception as e:
                    logger.error(f"Erreur ligne {row_number + 2}: {e}")
                    logger.error(f"Contenu de la ligne: {row.to_dict()}")
                    continue
            
            logger.info(f"{len(parsed_records)} enregistrements parsés avec succès")
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
            # Pas d'entête car format 2 colonnes Verticales
            df = pd.read_excel(excel_data, header=None)
            
            logger.info(f"Traitement d'un fichier Excel vertical ({len(df)} lignes)")
            
            # Récupérer les clés connues pour détecter un en-tête horizontal par erreur
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
                
                # Robustesse : Détection de header horizontal (si i=0, key est split_key mais value est un champ connu)
                if i == 0 and key == split_key and value in known_keys:
                    logger.warning(f"⚠️ Ligne 0 détectée comme en-tête horizontal ({key} | {value}). Sautée.")
                    continue
                
                # Détection de nouveau dossier
                if key == split_key and split_key in current_raw:
                    raw_records.append(current_raw)
                    current_raw = {}
                
                current_raw[key] = value
                
            if current_raw:
                raw_records.append(current_raw)
                
            logger.info(f"{len(raw_records)} dossiers bruts détectés dans le fichier vertical")
            
            # 2. Mapper vers les champs internes en appliquant les transformations
            parsed_records = []
            for idx, raw in enumerate(raw_records, 1):
                record = self._apply_client_mapping(raw)
                
                # Vérifier les champs requis
                if not self._validate_required_fields(record, idx):
                    continue
                    
                parsed_records.append(record)
                
            logger.info(f"{len(parsed_records)} enregistrements verticaux mappés avec succès")
            return parsed_records
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing Excel vertical: {e}")
            raise

    def _apply_client_mapping(self, raw_record):
        """Applique le mapping défini dans le YAML si présent, sinon mapping DB classique"""
        if not self.client_config or 'mappings' not in self.client_config:
            record = {}
            for mapping in self.mappings:
                val = raw_record.get(mapping.column_name)
                record[mapping.internal_field] = val
            return record

        record = {}
        for m in self.client_config['mappings']:
            source_key = m.get('source_key')
            
            # Valeur source
            if source_key == "__COMPUTED_AD_L4__":
                value = self._compute_ad_l4(raw_record)
            else:
                value = raw_record.get(source_key)
            
            # Transformation
            transform_name = m.get('transform')
            if transform_name:
                value = self._execute_transform(value, transform_name)
            
            # Attribution au premier champ candidat
            for field in m.get('candidate_fields', []):
                if hasattr(Donnee, field):
                    record[field] = value
                    break
        
        return record

    def _execute_transform(self, value, transform_name):
        """Exécute une transformation spécifiée sur une valeur"""
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
            # Garder les 5 premiers caractères num
            res = re.sub(r'[^0-9]', '', str(value))
            return res[:5] if res else None
        elif t == "phone_sanitize":
            # Garder uniquement les chiffres
            return re.sub(r'[^0-9+]', '', str(value))
        elif t == "parse_date_ddmmyyyy":
            try:
                # Gérer divers formats de date via pandas
                return pd.to_datetime(value, dayfirst=True).date()
            except:
                return None
        elif "concat_ad_l4" in t:
            # Déjà géré par _compute_ad_l4 car c'est un computed field complet
            return value
            
        return value

    def _compute_ad_l4(self, raw_record):
        """Calcule l'adresse ligne 4 à partir des composants num, type, voie"""
        num = raw_record.get("AD-L4 Numéro", "")
        type_voie = raw_record.get("AD-L4 Type", "")
        voie = raw_record.get("AD-L4 Voie", "")
        
        parts = [p for p in [num, type_voie, voie] if p and str(p).strip()]
        return " ".join(parts) if parts else None
    
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
            if not value or not str(value).strip() or str(value).lower() == 'nan':
                # Pour numeroDossier, on peut être indulgent pour les contestations
                if mapping.internal_field == 'numeroDossier':
                    logger.info(f"Ligne {line_number}: 'numeroDossier' absent, continué...")
                    continue
                    
                logger.warning(
                    f"Ligne {line_number}: Champ requis manquant '{mapping.internal_field}'"
                )
                logger.info(f"Record content: {record}")
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
        
        # Traitement spécial pour CLIENT_X
        record = self._preprocess_client_x_record(record, client_id)
        
        if client_id:
            from models.client import Client
            client = db.session.get(Client, client_id)
            if client and client.code == 'RG_SHERLOCK':
                return self._create_sherlock_donnee(record, fichier_id)

        # Détection automatique de contestation (PARTNER) — uniquement via le nom du fichier
        type_demande = record.get('typeDemande', '')
        if (not type_demande or type_demande == 'ENQ') and client_id:
            if client and client.code in ['CLIENT_X', 'PARTNER']:
                filename_upper = self.filename.upper().replace('-', ' ').replace('_', ' ') if self.filename else ''
                if 'CONTESTATION' in filename_upper or 'CONTRE ENQUETE' in filename_upper:
                    type_demande = 'CON'
                    record['typeDemande'] = 'CON'
                    logger.info(f"✅ Détection CON via Nom Fichier: {self.filename}")
        
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
            # Champs spécifiques PARTNER (ex-CLIENT_X)
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
        
        # IMPORTANT: Flush pour obtenir l'ID avant de créer les PartnerCaseRequest
        db.session.add(nouvelle_donnee)
        db.session.flush()
        
        # Parse RECHERCHE pour PARTNER (créer les demandes)
        self._parse_recherche_if_partner(nouvelle_donnee, client_id)
        
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
            
        # Fallback: Recherche par Nom/Prénom si toujours rien (et qu'on a un nom dans le record)
        if not enquete_originale and record.get('nom'):
            from services.partner_request_parser import PartnerRequestParser
            from utils import convert_date
            
            nom_norm = PartnerRequestParser.normalize_text(record.get('nom'))
            prenom_norm = PartnerRequestParser.normalize_text(record.get('prenom')) if record.get('prenom') else ''
            date_naissance_record = convert_date(record.get('dateNaissance'))
            
            # Chercher dans les enquêtes non-contestations du même client
            # On utilise une recherche insensible à la casse et sans accents via normalisation simple
            # Pour la performance, on cherche d'abord les correspondances exactes (nom seulement par exemple)
            all_candidats = Donnee.query.filter_by(
                client_id=client_id,
                est_contestation=False
            ).filter(Donnee.nom.ilike(f"%{record.get('nom').strip()}%")).all()
            
            meilleur_match = None
            meilleur_score = 0
            
            for candidat in all_candidats:
                c_nom = PartnerRequestParser.normalize_text(candidat.nom)
                c_prenom = PartnerRequestParser.normalize_text(candidat.prenom) if candidat.prenom else ''
                
                # Score de correspondance (plus élevé = meilleur match)
                score = 0
                
                # Correspondance exacte du nom (obligatoire)
                if nom_norm == c_nom:
                    score += 10
                else:
                    continue  # Le nom doit correspondre
                
                # Correspondance du prénom (si disponible)
                if prenom_norm and c_prenom:
                    if prenom_norm == c_prenom:
                        score += 10
                    elif prenom_norm in c_prenom or c_prenom in prenom_norm:
                        score += 5  # Correspondance partielle
                
                # Correspondance de la date de naissance (si disponible)
                if date_naissance_record and candidat.dateNaissance:
                    if date_naissance_record == candidat.dateNaissance:
                        score += 10
                
                # Si on a un meilleur match, le garder
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_match = candidat
            
            # Si on a trouvé un match avec un score suffisant (au moins le nom)
            if meilleur_match and meilleur_score >= 10:
                enquete_originale = meilleur_match
                logger.info(f"✅ Enquête originale trouvée via Fallback Nom/Prénom/Date (score: {meilleur_score}): {meilleur_match.id} - {meilleur_match.numeroDossier}")
        
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
    
    def _preprocess_client_x_record(self, record, client_id):
        """
        Prétraite les enregistrements CLIENT_X/PARTNER avec logiques spécifiques
        
        Args:
            record (dict): Enregistrement parsé
            client_id (int): ID du client
            
        Returns:
            dict: Enregistrement prétraité
        """
        from models.client import Client
        
        # Vérifier si c'est CLIENT_X ou PARTNER
        client = db.session.get(Client, client_id)
        if not client or client.code not in ['CLIENT_X', 'PARTNER']:
            return record
        
        # 1. Combiner JOUR/MOIS/ANNEE en dateNaissance
        # Les 3 champs peuvent être séparés dans l'import Excel PARTNER
        jour_raw = record.get('dateNaissance', '')
        mois_raw = record.get('dateNaissance_mois', '')
        annee_raw = record.get('dateNaissance_annee', '')
        
        # Nettoyer et convertir (gérer float pandas: 27.0 -> "27")
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
                    logger.info(f"✅ Date de naissance combinée: {record['dateNaissance']}")
                else:
                    logger.warning(f"⚠️ Date invalide ignorée: {j}/{m}/{a}")
                    record['dateNaissance'] = None
            except Exception as e:
                logger.warning(f"⚠️ Erreur combinaison date: {jour}/{mois}/{annee} - {e}")
                record['dateNaissance'] = None
        else:
            # Si l'un des 3 manque, laisser NULL
            record['dateNaissance'] = None
            if jour or mois or annee:
                logger.warning(f"⚠️ Date incomplète (JOUR:{jour}, MOIS:{mois}, ANNEE:{annee})")
        
        # 2. Normaliser le code postal (zfill(5))
        if 'codePostal' in record and record.get('codePostal'):
            cp = str(record['codePostal']).strip()
            if cp and cp.isdigit():
                record['codePostal'] = cp.zfill(5)
        
        # 3. Nettoyer le téléphone (null si "0")
        if 'telephonePersonnel' in record:
            tel = str(record.get('telephonePersonnel', '')).strip()
            if tel == '0' or tel == '':
                record['telephonePersonnel'] = None
        
        # 4. Gérer l'urgence pour contestations
        # Note: L'urgence doit venir d'un champ dédié 'urgence', pas du prénom
        if record.get('typeDemande') == 'CON':
            # Si un champ 'urgence' existe explicitement, l'utiliser
            if 'urgence' in record:
                urgence_value = str(record.get('urgence', '')).strip().upper()
                if urgence_value in ['URGENT', '1', 'O', 'OUI', 'YES']:
                    record['urgence'] = '1'  # True
                else:
                    record['urgence'] = '0'  # False
            # Sinon, laisser vide (pas d'urgence par défaut)
            elif 'urgence' not in record:
                record['urgence'] = '0'  # Pas d'urgence par défaut
        
        return record
    
    def _parse_recherche_if_partner(self, donnee, client_id):
        """
        Parse le champ RECHERCHE pour PARTNER et crée les demandes
        
        Args:
            donnee (Donnee): Instance de Donnee (DOIT avoir un ID - après flush)
            client_id (int): ID du client
        """
        from models.client import Client
        from models.partner_models import PartnerCaseRequest
        from services.partner_request_parser import PartnerRequestParser
        
        # Vérifier si c'est PARTNER
        client = db.session.get(Client, client_id)
        if not client or client.code not in ['CLIENT_X', 'PARTNER']:
            return
        
        # Vérifier si RECHERCHE existe
        if not donnee.recherche or not donnee.recherche.strip():
            logger.info(f"Pas de RECHERCHE pour donnee {donnee.numeroDossier}, skip parsing")
            return
        
        # Vérifier que donnee a un ID (doit être flushed avant)
        if not donnee.id:
            logger.error(f"ERREUR: donnee.id est None, impossible de créer les PartnerCaseRequest")
            return
        
        # Parser RECHERCHE
        detected_requests = PartnerRequestParser.parse_recherche(donnee.recherche, client_id)
        
        if not detected_requests:
            logger.warning(f"Aucune demande détectée dans RECHERCHE: '{donnee.recherche}'")
            return
        
        # Créer les PartnerCaseRequest
        logger.info(f"Création de {len(detected_requests)} demandes pour donnee {donnee.id} ({donnee.numeroDossier})")
        
        for request_code in detected_requests:
            # Vérifier si existe déjà
            existing = PartnerCaseRequest.query.filter_by(
                donnee_id=donnee.id,
                request_code=request_code
            ).first()
            
            if not existing:
                new_request = PartnerCaseRequest(
                    donnee_id=donnee.id,
                    request_code=request_code,
                    requested=True,
                    found=False,  # Sera calculé plus tard
                    status='NEG'  # Sera calculé plus tard
                )
                db.session.add(new_request)
                logger.info(f"  → PartnerCaseRequest créé: {request_code}")
            else:
                logger.info(f"  → PartnerCaseRequest existe déjà: {request_code}")

    def _create_sherlock_donnee(self, record, fichier_id):
        """Crée une instance SherlockDonnee"""
        # Mapper les champs record -> SherlockDonnee
        # On suppose que les internal_fields dans le YAML correspondent aux attributs de SherlockDonnee
        nouvelle_donnee = SherlockDonnee(
            fichier_id=fichier_id,
            **{k: v for k, v in record.items() if hasattr(SherlockDonnee, k)}
        )
        
        db.session.add(nouvelle_donnee)
        return nouvelle_donnee


