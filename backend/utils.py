
import logging
from datetime import datetime
from models import db, Donnee

logger = logging.getLogger(__name__)

# Définition des positions des colonnes
COLUMN_SPECS = [
    ("numeroDossier", 0, 10),
    ("referenceDossier", 10, 25),
    ("numeroInterlocuteur", 25, 37),
    ("guidInterlocuteur", 37, 73),
    ("typeDemande", 73, 76),
    ("numeroDemande", 76, 87),
    ("numeroDemandeContestee", 87, 98),
    ("numeroDemandeInitiale", 98, 109),
    ("forfaitDemande", 109, 125),
    ("dateRetourEspere", 125, 135),
    ("qualite", 135, 145),
    ("nom", 145, 175),
    ("prenom", 175, 195),
    ("dateNaissance", 195, 205),
    ("lieuNaissance", 205, 255),
    # Ajoutez tous les autres champs avec leurs positions...
]

def parse_line(line):
    """Parse une ligne selon les spécifications exactes"""
    try:
        if len(line.strip()) == 0:
            return None
            
        record = {}
        for name, start, end in COLUMN_SPECS:
            try:
                # S'assurer que la ligne est assez longue
                if len(line) >= end:
                    value = line[start:end].strip()
                else:
                    value = line[start:].strip() if len(line) > start else ""
                record[name] = value
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du champ {name}: {str(e)}")
                record[name] = ""

        # Vérifier si on a un numéro de dossier valide
        if not record.get("numeroDossier"):
            return None

        logger.debug(f"Ligne parsée avec succès: {record['numeroDossier']}")
        return record

    except Exception as e:
        logger.error(f"Erreur lors du parsing de la ligne: {str(e)}")
        return None

def process_file_content(content, fichier_id):
    """Traite le contenu du fichier et crée les enregistrements"""
    try:
        text_content = content.decode('utf-8', errors='ignore')
        lines = text_content.split('\n')
        
        logger.info(f"Traitement de {len(lines)} lignes pour le fichier {fichier_id}")
        processed_records = []
        errors = []

        for line_number, line in enumerate(lines, 1):
            try:
                if not line.strip():
                    continue

                # Parse la ligne
                record = parse_line(line)
                if not record:
                    continue

                logger.debug(f"Création d'un enregistrement pour le dossier {record['numeroDossier']}")

                # Convertir les dates
                date_fields = ['dateRetourEspere', 'dateNaissance', 'dateRetour', 
                             'dateFacture', 'dateDeces']
                for field in date_fields:
                    if field in record and record[field]:
                        try:
                            record[field] = datetime.strptime(record[field].strip(), '%d/%m/%Y').date()
                        except ValueError:
                            record[field] = None

                # Création de l'enregistrement
                # Créer l'objet Donnee avec les données nettoyées
                donnee = Donnee(
                    fichier_id=fichier_id,
                    numeroDossier=record.get('numeroDossier'),
                    referenceDossier=record.get('referenceDossier'),
                    numeroInterlocuteur=record.get('numeroInterlocuteur'),
                    guidInterlocuteur=record.get('guidInterlocuteur'),
                    typeDemande=record.get('typeDemande'),
                    numeroDemande=record.get('numeroDemande'),
                    numeroDemandeContestee=record.get('numeroDemandeContestee'),
                    numeroDemandeInitiale=record.get('numeroDemandeInitiale'),
                    forfaitDemande=record.get('forfaitDemande'),
                    dateRetourEspere=record.get('dateRetourEspere'),
                    qualite=record.get('qualite'),
                    nom=record.get('nom'),
                    prenom=record.get('prenom'),
                    dateNaissance=record.get('dateNaissance'),
                    lieuNaissance=record.get('lieuNaissance'),
                    codePostalNaissance=record.get('codePostalNaissance'),
                    paysNaissance=record.get('paysNaissance'),
                    nomPatronymique=record.get('nomPatronymique'),
                    dateRetour=record.get('dateRetour'),
                    codeResultat=record.get('codeResultat'),
                    elementsRetrouves=record.get('elementsRetrouves'),
                    flagEtatCivilErrone=record.get('flagEtatCivilErrone'),
                    numeroFacture=record.get('numeroFacture'),
                    dateFacture=record.get('dateFacture'),
                    montantFacture=record.get('montantFacture'),
                    tarifApplique=record.get('tarifApplique'),
                    cumulMontantsPrecedents=record.get('cumulMontantsPrecedents'),
                    repriseFacturation=record.get('repriseFacturation'),
                    remiseEventuelle=record.get('remiseEventuelle'),
                    dateDeces=record.get('dateDeces'),
                    numeroActeDeces=record.get('numeroActeDeces'),
                    codeInseeDeces=record.get('codeInseeDeces'),
                    codePostalDeces=record.get('codePostalDeces'),
                    localiteDeces=record.get('localiteDeces'),
                    adresse1=record.get('adresse1'),
                    adresse2=record.get('adresse2'),
                    adresse3=record.get('adresse3'),
                    adresse4=record.get('adresse4'),
                    codePostal=record.get('codePostal'),
                    ville=record.get('ville'),
                    paysResidence=record.get('paysResidence'),
                    telephonePersonnel=record.get('telephonePersonnel'),
                    telephoneEmployeur=record.get('telephoneEmployeur'),
                    nomEmployeur=record.get('nomEmployeur'),
                    telephoneDeEmployeur=record.get('telephoneDeEmployeur'),
                    telecopieEmployeur=record.get('telecopieEmployeur'),
                    adresse1Employeur=record.get('adresse1Employeur'),
                    adresse2Employeur=record.get('adresse2Employeur'),
                    adresse3Employeur=record.get('adresse3Employeur'),
                    adresse4Employeur=record.get('adresse4Employeur'),
                    codePostalEmployeur=record.get('codePostalEmployeur'),
                    villeEmployeur=record.get('villeEmployeur'),
                    paysEmployeur=record.get('paysEmployeur'),
                    banqueDomiciliation=record.get('banqueDomiciliation'),
                    libelleGuichet=record.get('libelleGuichet'),
                    titulaireCompte=record.get('titulaireCompte'),
                    codeBanque=record.get('codeBanque'),
                    codeGuichet=record.get('codeGuichet'),
                    numeroCompte=record.get('numeroCompte'),
                    ribCompte=record.get('ribCompte')
                )

                db.session.add(donnee)
                processed_records.append(record)

                if len(processed_records) % 100 == 0:
                    db.session.commit()
                    logger.info(f"{len(processed_records)} enregistrements traités")

            except Exception as e:
                errors.append(f"Erreur ligne {line_number}: {str(e)}")
                continue

        # Commit final
        try:
            db.session.commit()
            count = Donnee.query.filter_by(fichier_id=fichier_id).count()
            logger.info(f"Import terminé. {count} enregistrements créés")
            
            if errors:
                logger.warning(f"{len(errors)} erreurs rencontrées pendant l'import")
                
            return processed_records
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors du commit final: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")
        db.session.rollback()
        raise