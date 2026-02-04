"""
Script d'import de données depuis des fichiers MDB vers PostgreSQL

Ce script permet d'importer les données d'un fichier Microsoft Access (MDB)
vers la base de données PostgreSQL EOS.

Usage:
    python import_from_mdb.py --file "chemin/vers/fichier.mdb" --client-code PARTNER
    python import_from_mdb.py --file "chemin/vers/fichier.mdb" --client-code PARTNER --dry-run
    python import_from_mdb.py --folder "chemin/vers/dossier" --client-code PARTNER
"""

import pyodbc
import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Client, Donnee, Fichier
from utils import convert_date, convert_float

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mapping des colonnes MDB vers les champs PostgreSQL
# Ce mapping peut être personnalisé selon la structure de vos fichiers MDB
DEFAULT_COLUMN_MAPPING = {
    # Identifiants
    'NumeroDossier': 'numeroDossier',
    'ReferenceDossier': 'referenceDossier',
    'NumeroInterlocuteur': 'numeroInterlocuteur',
    'GuidInterlocuteur': 'guidInterlocuteur',
    
    # Type de demande
    'TypeDemande': 'typeDemande',
    'NumeroDemande': 'numeroDemande',
    'NumeroDemandeContestee': 'numeroDemandeContestee',
    'NumeroDemandeInitiale': 'numeroDemandeInitiale',
    
    # Informations personnelles
    'Qualite': 'qualite',
    'Nom': 'nom',
    'Prenom': 'prenom',
    'DateNaissance': 'dateNaissance',
    'LieuNaissance': 'lieuNaissance',
    'CodePostalNaissance': 'codePostalNaissance',
    'PaysNaissance': 'paysNaissance',
    'NomPatronymique': 'nomPatronymique',
    
    # Adresse
    'Adresse1': 'adresse1',
    'Adresse2': 'adresse2',
    'Adresse3': 'adresse3',
    'Adresse4': 'adresse4',
    'Ville': 'ville',
    'CodePostal': 'codePostal',
    'PaysResidence': 'paysResidence',
    
    # Contact
    'TelephonePersonnel': 'telephonePersonnel',
    'TelephoneEmployeur': 'telephoneEmployeur',
    'TelecopieEmployeur': 'telecopieEmployeur',
    
    # Employeur
    'NomEmployeur': 'nomEmployeur',
    
    # Banque
    'BanqueDomiciliation': 'banqueDomiciliation',
    'LibelleGuichet': 'libelleGuichet',
    'TitulaireCompte': 'titulaireCompte',
    'CodeBanque': 'codeBanque',
    'CodeGuichet': 'codeGuichet',
    'NumeroCompte': 'numeroCompte',
    'RibCompte': 'ribCompte',
    
    # Demande
    'DateDenvoie': 'datedenvoie',
    'DateRetourEspere': 'dateRetourEspere',
    'ElementDemandes': 'elementDemandes',
    'ElementObligatoires': 'elementObligatoires',
    'ElementContestes': 'elementContestes',
    
    # Contestation
    'CodeMotif': 'codeMotif',
    'MotifDeContestation': 'motifDeContestation',
    
    # Autres
    'CodeSociete': 'codesociete',
    'Urgence': 'urgence',
    'Commentaire': 'commentaire',
    'DateButoir': 'date_butoir',
    'ForfaitDemande': 'forfaitDemande',
    'CumulMontantsPrecedents': 'cumulMontantsPrecedents',
}


def get_mdb_connection(mdb_file):
    """Établit une connexion à un fichier MDB"""
    if not os.path.exists(mdb_file):
        raise FileNotFoundError(f"Fichier introuvable : {mdb_file}")
    
    drivers = [x for x in pyodbc.drivers() if 'Access' in x]
    if not drivers:
        raise RuntimeError("Aucun pilote Microsoft Access ODBC trouvé")
    
    driver = drivers[0]
    conn_str = f'DRIVER={{{driver}}};DBQ={mdb_file};'
    
    return pyodbc.connect(conn_str)


def get_table_columns(cursor, table_name):
    """Récupère les colonnes d'une table"""
    columns = []
    for column in cursor.columns(table=table_name):
        columns.append(column.column_name)
    return columns


def map_mdb_row_to_donnee(row, columns, column_mapping):
    """Mappe une ligne MDB vers un dictionnaire de champs Donnee"""
    record = {}
    
    for i, col_name in enumerate(columns):
        # Trouver le champ interne correspondant
        internal_field = column_mapping.get(col_name)
        
        if internal_field:
            value = row[i]
            
            # Nettoyer les valeurs None/NULL
            if value is None or (isinstance(value, str) and value.strip() == ''):
                value = None
            
            record[internal_field] = value
    
    return record


def import_mdb_table(mdb_file, table_name, client_id, fichier_id, column_mapping, dry_run=False):
    """Importe les données d'une table MDB"""
    logger.info(f"Import de la table '{table_name}' depuis {os.path.basename(mdb_file)}")
    
    conn = get_mdb_connection(mdb_file)
    cursor = conn.cursor()
    
    # Récupérer les colonnes
    columns = get_table_columns(cursor, table_name)
    logger.info(f"Colonnes trouvées : {', '.join(columns)}")
    
    # Récupérer les données
    cursor.execute(f"SELECT * FROM [{table_name}]")
    
    imported_count = 0
    error_count = 0
    
    for row in cursor.fetchall():
        try:
            # Mapper la ligne vers un dictionnaire
            record = map_mdb_row_to_donnee(row, columns, column_mapping)
            
            if dry_run:
                logger.info(f"[DRY-RUN] Enregistrement : {record.get('numeroDossier', 'N/A')}")
                imported_count += 1
                continue
            
            # Créer l'objet Donnee
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
                dateRetourEspere=convert_date(record.get('dateRetourEspere')),
                qualite=record.get('qualite', ''),
                nom=record.get('nom', ''),
                prenom=record.get('prenom', ''),
                dateNaissance=convert_date(record.get('dateNaissance')),
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
                datedenvoie=convert_date(record.get('datedenvoie')),
                elementDemandes=record.get('elementDemandes', ''),
                elementObligatoires=record.get('elementObligatoires', ''),
                elementContestes=record.get('elementContestes', ''),
                codeMotif=record.get('codeMotif', ''),
                motifDeContestation=record.get('motifDeContestation', ''),
                cumulMontantsPrecedents=convert_float(record.get('cumulMontantsPrecedents')),
                codesociete=record.get('codesociete', ''),
                urgence=record.get('urgence', ''),
                commentaire=record.get('commentaire', ''),
                date_butoir=convert_date(record.get('date_butoir'))
            )
            
            db.session.add(nouvelle_donnee)
            imported_count += 1
            
            # Commit par batch de 100
            if imported_count % 100 == 0:
                db.session.commit()
                logger.info(f"  → {imported_count} enregistrements importés...")
        
        except Exception as e:
            error_count += 1
            logger.error(f"Erreur lors de l'import d'un enregistrement : {e}")
            continue
    
    # Commit final
    if not dry_run:
        db.session.commit()
    
    conn.close()
    
    logger.info(f"✅ Import terminé : {imported_count} importés, {error_count} erreurs")
    return imported_count, error_count


def import_mdb_file(mdb_file, client_code, table_name=None, dry_run=False):
    """Importe un fichier MDB complet"""
    logger.info(f"\n{'='*70}")
    logger.info(f"IMPORT DU FICHIER : {os.path.basename(mdb_file)}")
    logger.info(f"{'='*70}")
    
    with app.app_context():
        # Récupérer le client
        client = Client.query.filter_by(code=client_code).first()
        if not client:
            raise ValueError(f"Client '{client_code}' introuvable")
        
        logger.info(f"Client : {client.nom} ({client.code})")
        
        # Créer un enregistrement Fichier
        if not dry_run:
            fichier = Fichier(
                nom=os.path.basename(mdb_file),
                client_id=client.id,
                date_import=datetime.now()
            )
            db.session.add(fichier)
            db.session.commit()
            fichier_id = fichier.id
        else:
            fichier_id = None
            logger.info("[DRY-RUN] Aucun enregistrement ne sera créé")
        
        # Si aucune table spécifiée, lister les tables disponibles
        if not table_name:
            conn = get_mdb_connection(mdb_file)
            cursor = conn.cursor()
            tables = [t.table_name for t in cursor.tables(tableType='TABLE') 
                     if not t.table_name.startswith('MSys') and not t.table_name.startswith('~')]
            conn.close()
            
            if len(tables) == 0:
                raise ValueError("Aucune table trouvée dans le fichier MDB")
            elif len(tables) == 1:
                table_name = tables[0]
                logger.info(f"Table détectée automatiquement : {table_name}")
            else:
                logger.info(f"Tables disponibles : {', '.join(tables)}")
                table_name = tables[0]
                logger.info(f"⚠️  Utilisation de la première table : {table_name}")
                logger.info("   Pour spécifier une table : --table NomTable")
        
        # Importer la table
        imported, errors = import_mdb_table(
            mdb_file, 
            table_name, 
            client.id, 
            fichier_id, 
            DEFAULT_COLUMN_MAPPING,
            dry_run
        )
        
        return {
            'file': os.path.basename(mdb_file),
            'client': client.code,
            'table': table_name,
            'imported': imported,
            'errors': errors
        }


def import_folder(folder_path, client_code, dry_run=False):
    """Importe tous les fichiers MDB d'un dossier"""
    mdb_files = list(Path(folder_path).glob('*.mdb'))
    
    if not mdb_files:
        logger.error(f"Aucun fichier .mdb trouvé dans : {folder_path}")
        return
    
    logger.info(f"\n📁 {len(mdb_files)} fichier(s) .mdb trouvé(s)")
    
    results = []
    for mdb_file in mdb_files:
        try:
            result = import_mdb_file(str(mdb_file), client_code, dry_run=dry_run)
            results.append(result)
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'import de {mdb_file.name} : {e}")
    
    # Résumé
    logger.info(f"\n{'='*70}")
    logger.info("RÉSUMÉ DE L'IMPORT")
    logger.info(f"{'='*70}")
    
    total_imported = sum(r['imported'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    
    for result in results:
        logger.info(f"  {result['file']:<30} : {result['imported']} importés, {result['errors']} erreurs")
    
    logger.info(f"\n  TOTAL : {total_imported} enregistrements importés, {total_errors} erreurs")


def main():
    parser = argparse.ArgumentParser(description='Importe des données MDB vers PostgreSQL')
    parser.add_argument('--file', help='Chemin vers un fichier MDB à importer')
    parser.add_argument('--folder', help='Chemin vers un dossier contenant des fichiers MDB')
    parser.add_argument('--client-code', required=True, help='Code du client (ex: PARTNER, RG_SHERLOCK)')
    parser.add_argument('--table', help='Nom de la table à importer (optionnel)')
    parser.add_argument('--dry-run', action='store_true', help='Mode test sans insertion réelle')
    
    args = parser.parse_args()
    
    if not args.file and not args.folder:
        logger.error("❌ Erreur : Spécifiez --file ou --folder")
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.file:
            import_mdb_file(args.file, args.client_code, args.table, args.dry_run)
        elif args.folder:
            import_folder(args.folder, args.client_code, args.dry_run)
        
        logger.info(f"\n{'='*70}")
        logger.info("✅ IMPORT TERMINÉ")
        logger.info(f"{'='*70}")
        
    except Exception as e:
        logger.error(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
