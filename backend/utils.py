import logging
from datetime import datetime
from extensions import db
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur
import codecs

logger = logging.getLogger(__name__)


class NanCleaner:
    """Proxy qui retourne '' pour les attributs string 'nan'/'none' (artefacts pandas)"""
    __slots__ = ('_obj',)
    def __init__(self, obj):
        object.__setattr__(self, '_obj', obj)
    def __getattr__(self, name):
        val = getattr(self._obj, name)
        if isinstance(val, str) and val.strip().lower() in ('nan', 'none'):
            return ''
        return val
    def __bool__(self):
        return self._obj is not None


# Définition des positions et longueurs exactes selon le cahier des charges
# Format: (nom du champ, position de début, longueur)
COLUMN_SPECS = [
    ("numeroDossier", 0, 10),
    ("referenceDossier", 10, 15),
    ("numeroInterlocuteur", 25, 12),
    ("guidInterlocuteur", 37, 36),
    ("typeDemande", 73, 3),
    ("numeroDemande", 76, 11),
    ("numeroDemandeContestee", 87, 11),
    ("numeroDemandeInitiale", 98, 11),
    ("forfaitDemande", 109, 16),
    ("dateRetourEspere", 125, 10),
    ("qualite", 135, 10),
    ("nom", 145, 30),
    ("prenom", 175, 20),
    ("dateNaissance", 195, 10),
    ("lieuNaissance", 205, 50),
    ("codePostalNaissance", 255, 10),
    ("paysNaissance", 265, 32),
    ("nomPatronymique", 297, 30),
    ("adresse1", 327, 32),
    ("adresse2", 359, 32),
    ("adresse3", 391, 32),
    ("adresse4", 423, 32),
    ("ville", 455, 32),
    ("codePostal", 487, 10),
    ("paysResidence", 497, 32),
    ("telephonePersonnel", 529, 15),
    ("telephoneEmployeur", 544, 15),
    ("telecopieEmployeur", 559, 15),
    ("nomEmployeur", 574, 32),
    ("banqueDomiciliation", 606, 32),
    ("libelleGuichet", 638, 30),
    ("titulaireCompte", 668, 32),
    ("codeBanque", 700, 5),
    ("codeGuichet", 705, 5),
    ("numeroCompte", 710, 11),
    ("ribCompte", 721, 2),
    ("datedenvoie", 723, 10),
    ("elementDemandes", 733, 10),
    ("elementObligatoires", 743, 10),
    ("elementContestes", 753, 10),
    ("codeMotif", 763, 16),
    ("motifDeContestation", 779, 64),
    ("cumulMontantsPrecedents", 843, 8),
    ("codeSociete", 851, 2),
    ("urgence", 853, 1),
    ("commentaire", 854, 1000)
]

# Définition des positions et longueurs pour le fichier de retour
RETURN_COLUMN_SPECS = [
    ("numeroDossier", 0, 10),
    ("referenceDossier", 10, 15),
    ("numeroInterlocuteur", 25, 12),
    ("guidInterlocuteur", 37, 36),
    ("typeDemande", 73, 3),
    ("numeroDemande", 76, 11),
    ("numeroDemandeContestee", 87, 11),
    ("numeroDemandeInitiale", 98, 11),
    ("forfaitDemande", 109, 16),
    ("dateRetourEspere", 125, 10),
    ("qualite", 135, 10),
    ("nom", 145, 30),
    ("prenom", 175, 20),
    ("dateNaissance", 195, 10),
    ("lieuNaissance", 205, 50),
    ("codePostalNaissance", 255, 10),
    ("paysNaissance", 265, 32),
    ("nomPatronymique", 297, 30),
    ("dateRetour", 327, 10),
    ("codeResultat", 337, 1),
    ("elementsRetrouves", 338, 10),
    ("flagEtatCivilErrone", 348, 1),
    ("numeroFacture", 349, 9),
    ("dateFacture", 358, 10),
    ("montantFacture", 368, 8),
    ("tarifApplique", 376, 8),
    ("cumulMontantsPrecedents", 384, 8),
    ("repriseFacturation", 392, 8),
    ("remiseEventuelle", 400, 8),
    ("dateDeces", 408, 10),
    ("numeroActeDeces", 418, 10),
    ("codeInseeDeces", 428, 5),
    ("codePostalDeces", 433, 10),
    ("localiteDeces", 443, 32),
    ("adresse1", 475, 32),
    ("adresse2", 507, 32),
    ("adresse3", 539, 32),
    ("adresse4", 571, 32),
    ("codePostal", 603, 10),
    ("ville", 613, 32),
    ("paysResidence", 645, 32),
    ("telephonePersonnel", 677, 15),
    ("telephoneEmployeur", 692, 15),
    ("nomEmployeur", 707, 32),
    ("telephoneEmployeur2", 739, 15),
    ("telecopieEmployeur", 754, 15),
    ("adresse1Employeur", 769, 32),
    ("adresse2Employeur", 801, 32),
    ("adresse3Employeur", 833, 32),
    ("adresse4Employeur", 865, 32),
    ("codePostalEmployeur", 897, 10),
    ("villeEmployeur", 907, 32),
    ("paysEmployeur", 939, 32),
    ("banqueDomiciliation", 971, 32),
    ("libelleGuichet", 1003, 30),
    ("titulaireCompte", 1033, 32),
    ("codeBanque", 1065, 5),
    ("codeGuichet", 1070, 5),
    ("numeroCompte", 1075, 11),
    ("ribCompte", 1086, 2),
    # Autres champs qui ne correspondent pas exactement à l'entrée
    ("commentairesRevenus", 1088, 128),
    ("montantSalaire", 1216, 10),
    ("periodeVersementSalaire", 1226, 2),
    ("frequenceVersementSalaire", 1228, 2),
    # Autres revenus
    ("natureRevenu1", 1230, 30),
    ("montantRevenu1", 1260, 10),
    ("periodeVersementRevenu1", 1270, 2),
    ("frequenceVersementRevenu1", 1272, 2),
    ("natureRevenu2", 1274, 30),
    ("montantRevenu2", 1304, 10),
    ("periodeVersementRevenu2", 1314, 2),
    ("frequenceVersementRevenu2", 1316, 2),
    ("natureRevenu3", 1318, 30),
    ("montantRevenu3", 1348, 10),
    ("periodeVersementRevenu3", 1358, 2),
    ("frequenceVersementRevenu3", 1360, 2),
    # Mémos et commentaires
    ("memo1", 1362, 64),
    ("memo2", 1426, 64),
    ("memo3", 1490, 64),
    ("memo4", 1554, 64),
    ("memo5", 1618, 1000)
]

def parse_line(line):
    """Parse une ligne selon les spécifications exactes du cahier des charges"""
    try:
        # Vérifier si la ligne est vide
        if not line or len(line.strip()) == 0:
            logger.warning("Ligne vide ignorée")
            return None
        
        # Vérifier la longueur de la ligne (doit être d'au moins 854 caractères)
        expected_min_length = 854
        if len(line) < expected_min_length:
            # Compléter la ligne avec des espaces si nécessaire
            line = line + ' ' * (expected_min_length - len(line))
            logger.warning(f"Ligne trop courte, complétée à {expected_min_length} caractères")
        
        # Initialiser un dictionnaire pour stocker les données de la ligne
        record = {}
        
        # Extraire chaque champ selon sa position et sa longueur
        for field_name, start_pos, length in COLUMN_SPECS:
            # Si la ligne est assez longue pour contenir ce champ
            if len(line) > start_pos:
                # Extraire la sous-chaîne à la position spécifiée
                end_pos = min(start_pos + length, len(line))
                value = line[start_pos:end_pos].strip()
                record[field_name] = value
            else:
                record[field_name] = ""
        
        # Vérifier si les champs obligatoires sont présents
        required_fields = ['numeroDossier', 'nom']
        missing_fields = [field for field in required_fields if not record.get(field)]
        
        if missing_fields:
            logger.warning(f"Champs obligatoires manquants: {', '.join(missing_fields)}")
            return None
        
        return record
        
    except Exception as e:
        logger.error(f"Erreur lors du parsing de la ligne: {str(e)}")
        return None

def process_file_content(content, fichier_id, date_butoir=None):
    """Traite le contenu du fichier et crée les enregistrements"""
    try:
        # Décodage du contenu en UTF-8 (avec remplacement des caractères non valides)
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # En cas d'échec, essayer d'autres encodages courants
                encodings = ['latin1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        content = content.decode(encoding)
                        logger.info(f"Fichier décodé avec l'encodage {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # Si aucun encodage ne fonctionne, utiliser utf-8 avec remplacement
                    content = content.decode('utf-8', errors='replace')
                    logger.warning("Fichier décodé avec remplacement de caractères invalides")
        
        # Séparation des lignes et suppression des lignes vides
        lines = [line for line in content.splitlines() if line.strip()]
        
        logger.info(f"Traitement de {len(lines)} lignes pour le fichier {fichier_id}")
        processed_records = []
        errors = []

        # Traiter chaque ligne
        for line_number, line in enumerate(lines, 1):
            try:
                # Parser la ligne
                record = parse_line(line)
                
                if not record:
                    logger.warning(f"Ligne {line_number} ignorée: format invalide")
                    continue
                
                # Ajouter l'ID du fichier au record
                record['fichier_id'] = fichier_id
                
                # Créer une nouvelle instance de Donnee
                nouvelle_donnee = Donnee(
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
                    codesociete=record.get('codeSociete', ''),
                    urgence=record.get('urgence', ''),
                    commentaire=record.get('commentaire', ''),
                    date_butoir=date_butoir  # Ajouter la date butoir
                )
                
                if record.get('typeDemande') == 'CON':
                    contested_number = record.get('numeroDemandeContestee', '')
                    logger.info(f"Traitement contestation: {record.get('numeroDossier')}, conteste: {contested_number}")
                    
                    # Essayer d'abord par numeroDossier
                    enquete_originale = Donnee.query.filter_by(
                        numeroDossier=contested_number
                    ).first()

                    # Si non trouvé, essayer par numeroDemande
                    if not enquete_originale:
                        enquete_originale = Donnee.query.filter_by(
                            numeroDemande=contested_number
                        ).first()
                    
                    if enquete_originale:
                        logger.info(f"Enquête originale trouvée: {enquete_originale.numeroDossier} (ID: {enquete_originale.id})")
                        # Établir la relation
                        nouvelle_donnee.est_contestation = True
                        nouvelle_donnee.enquete_originale_id = enquete_originale.id
                        nouvelle_donnee.date_contestation = datetime.now().date()
                        nouvelle_donnee.motif_contestation_code = record.get('codeMotif', '')
                        nouvelle_donnee.motif_contestation_detail = record.get('motifDeContestation', '')
                        
                        # Récupérer l'enquêteur de l'enquête originale
                        nouvelle_donnee.enqueteurId = enquete_originale.enqueteurId
                        
                        # Ajouter à l'historique de l'enquête originale
                        if hasattr(enquete_originale, 'add_to_history'):
                            enquete_originale.add_to_history(
                                'contestation', 
                                f"Contestation reçue: {nouvelle_donnee.numeroDossier}. Motif: {nouvelle_donnee.motif_contestation_detail}",
                                'Système d\'import'
                            )
                        
                        # Commit l'enquête originale mise à jour
                        db.session.add(enquete_originale)
                    else:
                        logger.warning(f"Enquête originale non trouvée pour contestation {record.get('numeroDossier')}, dossier contesté: {contested_number}")
                    
                    # Ajouter à l'historique de la contestation
                    if hasattr(nouvelle_donnee, 'add_to_history'):
                        nouvelle_donnee.add_to_history(
                            'creation', 
                            f"Contestation de l'enquête {contested_number}",
                            'Système d\'import'
                        )

                # Ajouter l'instance à la session
                db.session.add(nouvelle_donnee)
                db.session.flush()  # Pour obtenir l'ID de l'instance
                
                # Créer une entrée DonneeEnqueteur si nécessaire
                if record.get('typeDemande') == 'CON':
                    # Pour les contestations, chercher les données enquêteur existantes
                    donnee_enqueteur = DonneeEnqueteur.query.filter_by(
                        donnee_id=nouvelle_donnee.id
                    ).first()
                    
                    if not donnee_enqueteur:
                        donnee_enqueteur = DonneeEnqueteur(
                            donnee_id=nouvelle_donnee.id,
                            client_id=nouvelle_donnee.client_id,  # AJOUT du client_id
                            # Initialiser avec les données de contestation si présentes
                            code_resultat='',
                            elements_retrouves=''
                        )
                        db.session.add(donnee_enqueteur)
                else:
                    # Pour les nouvelles enquêtes, toujours créer une entrée DonneeEnqueteur
                    donnee_enqueteur = DonneeEnqueteur(
                        donnee_id=nouvelle_donnee.id,
                        client_id=nouvelle_donnee.client_id,  # AJOUT du client_id
                        code_resultat='',
                        elements_retrouves=''
                    )
                    db.session.add(donnee_enqueteur)
                
                # Ajouter le record aux résultats
                processed_records.append(record)
                
                # Commit tous les 100 enregistrements
                if len(processed_records) % 100 == 0:
                    db.session.commit()
                    logger.info(f"Traité {len(processed_records)} enregistrements")
                
            except Exception as e:
                errors.append(f"Erreur ligne {line_number}: {str(e)}")
                logger.error(f"Erreur lors du traitement de la ligne {line_number}: {str(e)}")
                continue
        
        # Commit final
        db.session.commit()
        
        # Log des erreurs rencontrées
        if errors:
            logger.warning(f"{len(errors)} erreurs rencontrées lors du traitement")
            for error in errors[:10]:  # Limiter le log aux 10 premières erreurs
                logger.warning(error)
        
        logger.info(f"Traitement terminé. {len(processed_records)} enregistrements créés")
        return processed_records
        
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        db.session.rollback()
        logger.exception(f"Erreur lors du traitement du fichier: {str(e)}")
        raise e

def convert_date(date_str):
    """Convertit une chaîne de date au format DD/MM/YYYY en objet datetime"""
    if not date_str:
        return None
    
    try:
        # Format attendu: JJ/MM/AAAA
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        try:
            # Essayer d'autres formats courants
            formats = ['%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%m/%d/%Y', '%d %m %Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            # Si aucun format ne correspond
            logger.warning(f"Format de date non reconnu: {date_str}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de la date {date_str}: {str(e)}")
            return None

def convert_float(float_str):
    """Convertit une chaîne en float"""
    if not float_str:
        return None
    
    try:
        # Gérer à la fois le point et la virgule comme séparateur décimal
        return float(float_str.replace(',', '.'))
    except (ValueError, TypeError):
        logger.warning(f"Impossible de convertir en nombre: {float_str}")
        return None

def format_export_line(donnee, donnee_enqueteur, enqueteur=None):
    """
    Formate une ligne pour l'exportation selon le format spécifié dans le cahier des charges
    """
    # Créer une ligne vide de la longueur maximale
    line_length = RETURN_COLUMN_SPECS[-1][1] + RETURN_COLUMN_SPECS[-1][2]
    line = ' ' * line_length
    line_list = list(line)
    
    # Préparer les valeurs à insérer
    values = {
        # Informations de base
        "numeroDossier": donnee.numeroDossier or "",
        "referenceDossier": donnee.referenceDossier or "",
        "numeroInterlocuteur": donnee.numeroInterlocuteur or "",
        "guidInterlocuteur": donnee.guidInterlocuteur or "",
        "typeDemande": donnee.typeDemande or "",
        "numeroDemande": donnee.numeroDemande or "",
        "numeroDemandeContestee": donnee.numeroDemandeContestee or "",
        "numeroDemandeInitiale": donnee.numeroDemandeInitiale or "",
        "forfaitDemande": donnee.forfaitDemande or "",
        "dateRetourEspere": donnee.dateRetourEspere.strftime('%d/%m/%Y') if donnee.dateRetourEspere else "",
        "qualite": donnee.qualite or "",
        "nom": donnee.nom or "",
        "prenom": donnee.prenom or "",
        "dateNaissance": donnee.dateNaissance.strftime('%d/%m/%Y') if donnee.dateNaissance else "",
        "lieuNaissance": donnee.lieuNaissance or "",
        "codePostalNaissance": donnee.codePostalNaissance or "",
        "paysNaissance": donnee.paysNaissance or "",
        "nomPatronymique": donnee.nomPatronymique or "",
        
        # Résultats de l'enquête
        "dateRetour": datetime.now().strftime('%d/%m/%Y'),
        "codeResultat": donnee_enqueteur.code_resultat or "",
        "elementsRetrouves": donnee_enqueteur.elements_retrouves or "",
        "flagEtatCivilErrone": donnee_enqueteur.flag_etat_civil_errone or "",
        
        # Informations de facturation (laisser vides ou à 0)
        "numeroFacture": "",
        "dateFacture": "",
        "montantFacture": "0",
        "tarifApplique": "0",
        "cumulMontantsPrecedents": "0",
        "repriseFacturation": "0",
        "remiseEventuelle": "0",
        
        # Informations de décès
        "dateDeces": donnee_enqueteur.date_deces.strftime('%d/%m/%Y') if donnee_enqueteur.date_deces else "",
        "numeroActeDeces": donnee_enqueteur.numero_acte_deces or "",
        "codeInseeDeces": donnee_enqueteur.code_insee_deces or "",
        "codePostalDeces": donnee_enqueteur.code_postal_deces or "",
        "localiteDeces": donnee_enqueteur.localite_deces or "",
        
        # Informations d'adresse
        "adresse1": donnee_enqueteur.adresse1 or "",
        "adresse2": donnee_enqueteur.adresse2 or "",
        "adresse3": donnee_enqueteur.adresse3 or "",
        "adresse4": donnee_enqueteur.adresse4 or "",
        "codePostal": donnee_enqueteur.code_postal or "",
        "ville": donnee_enqueteur.ville or "",
        "paysResidence": donnee_enqueteur.pays_residence or "",
        "telephonePersonnel": donnee_enqueteur.telephone_personnel or "",
        
        # Informations employeur
        "telephoneEmployeur": donnee_enqueteur.telephone_chez_employeur or "",
        "nomEmployeur": donnee_enqueteur.nom_employeur or "",
        "telephoneEmployeur2": donnee_enqueteur.telephone_employeur or "",
        "telecopieEmployeur": donnee_enqueteur.telecopie_employeur or "",
        "adresse1Employeur": donnee_enqueteur.adresse1_employeur or "",
        "adresse2Employeur": donnee_enqueteur.adresse2_employeur or "",
        "adresse3Employeur": donnee_enqueteur.adresse3_employeur or "",
        "adresse4Employeur": donnee_enqueteur.adresse4_employeur or "",
        "codePostalEmployeur": donnee_enqueteur.code_postal_employeur or "",
        "villeEmployeur": donnee_enqueteur.ville_employeur or "",
        "paysEmployeur": donnee_enqueteur.pays_employeur or "",
        
        # Informations bancaires
        "banqueDomiciliation": donnee_enqueteur.banque_domiciliation or "",
        "libelleGuichet": donnee_enqueteur.libelle_guichet or "",
        "titulaireCompte": donnee_enqueteur.titulaire_compte or "",
        "codeBanque": donnee_enqueteur.code_banque or "",
        "codeGuichet": donnee_enqueteur.code_guichet or "",
        "numeroCompte": "",  # Laisser vide selon le cahier des charges
        "ribCompte": "",     # Laisser vide selon le cahier des charges
        
        # Informations sur les revenus
        "commentairesRevenus": donnee_enqueteur.commentaires_revenus or "",
        "montantSalaire": str(donnee_enqueteur.montant_salaire or ""),
        "periodeVersementSalaire": str(donnee_enqueteur.periode_versement_salaire or ""),
        "frequenceVersementSalaire": donnee_enqueteur.frequence_versement_salaire or "",
        
        # Mémos
        "memo1": donnee_enqueteur.memo1 or "",
        "memo2": donnee_enqueteur.memo2 or "",
        "memo3": donnee_enqueteur.memo3 or "",
        "memo4": donnee_enqueteur.memo4 or "",
        "memo5": donnee_enqueteur.memo5 or ""
    }
    
    # Insérer chaque valeur à la position correcte
    for field_name, start_pos, length in RETURN_COLUMN_SPECS:
        value = values.get(field_name, "")
        # Tronquer si la valeur est trop longue
        if len(value) > length:
            value = value[:length]
        # Insérer la valeur dans la ligne à la position correcte
        for i, char in enumerate(value):
            if i < length and start_pos + i < len(line_list):
                line_list[start_pos + i] = char
    
    # Reconvertir la liste en chaîne
    return "".join(line_list)

def generate_export_content(donnees):
    """
    Génère le contenu complet du fichier d'exportation
    """
    lines = []
    
    for donnee in donnees:
        # Récupérer les données enquêteur associées
        donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
        
        # Si pas de données enquêteur, créer un objet vide
        if not donnee_enqueteur:
            donnee_enqueteur = DonneeEnqueteur(
                donnee_id=donnee.id,
                client_id=donnee.client_id  # AJOUT du client_id
            )
        
        # Créer la ligne formatée
        line = format_export_line(donnee, donnee_enqueteur)
        lines.append(line)
    
    # Joindre toutes les lignes avec des sauts de ligne
    return "\n".join(lines)