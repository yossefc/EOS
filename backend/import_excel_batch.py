"""
Script d'import batch de fichiers Excel vers PostgreSQL

Ce script permet d'importer automatiquement tous les fichiers Excel
d'un dossier vers la base de données EOS.

Usage:
    python import_excel_batch.py --folder "chemin/vers/dossier" --client-code PARTNER
    python import_excel_batch.py --folder "chemin/vers/dossier" --client-code PARTNER --dry-run
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Client, Fichier
from import_engine import ImportEngine

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_import_profile_for_client(client_id):
    """Récupère le profil d'import pour un client"""
    from models import ImportProfile
    
    # Chercher un profil d'import EXCEL pour ce client
    profile = ImportProfile.query.filter_by(
        client_id=client_id,
        file_type='EXCEL'
    ).first()
    
    if not profile:
        # Créer un profil d'import générique si aucun n'existe
        logger.warning(f"Aucun profil d'import EXCEL trouvé pour le client {client_id}")
        logger.info("Création d'un profil d'import générique...")
        
        profile = ImportProfile(
            client_id=client_id,
            name="Import Excel Générique",
            file_type='EXCEL',
            encoding='utf-8',
            sheet_name=None  # Première feuille par défaut
        )
        db.session.add(profile)
        db.session.commit()
        
        logger.info(f"✅ Profil d'import créé (ID: {profile.id})")
    
    return profile


def import_excel_file(excel_file, client, dry_run=False):
    """Importe un fichier Excel"""
    logger.info(f"\n{'='*70}")
    logger.info(f"IMPORT DU FICHIER : {os.path.basename(excel_file)}")
    logger.info(f"{'='*70}")
    
    try:
        # Récupérer le profil d'import
        profile = get_import_profile_for_client(client.id)
        
        # Créer un enregistrement Fichier
        if not dry_run:
            fichier = Fichier(
                nom=os.path.basename(excel_file),
                client_id=client.id,
                date_import=datetime.now()
            )
            db.session.add(fichier)
            db.session.commit()
            fichier_id = fichier.id
        else:
            fichier_id = None
            logger.info("[DRY-RUN] Aucun enregistrement ne sera créé")
        
        # Lire le fichier Excel
        with open(excel_file, 'rb') as f:
            content = f.read()
        
        # Créer le moteur d'import
        engine = ImportEngine(profile, filename=os.path.basename(excel_file))
        
        # Parser le contenu
        logger.info("Parsing du fichier Excel...")
        records = engine.parse_content(content)
        
        if not records:
            logger.warning("⚠️  Aucun enregistrement trouvé dans le fichier")
            return {
                'file': os.path.basename(excel_file),
                'imported': 0,
                'errors': 0,
                'status': 'empty'
            }
        
        logger.info(f"📊 {len(records)} enregistrements trouvés")
        
        # Importer les enregistrements
        imported_count = 0
        error_count = 0
        
        for i, record in enumerate(records, 1):
            try:
                if dry_run:
                    logger.info(f"[DRY-RUN] Enregistrement {i}: {record.get('numeroDossier', 'N/A')}")
                    imported_count += 1
                else:
                    # Créer la donnée
                    donnee = engine.create_donnee_from_record(
                        record,
                        fichier_id,
                        client.id
                    )
                    imported_count += 1
                    
                    # Commit par batch de 100
                    if imported_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"  → {imported_count}/{len(records)} enregistrements importés...")
            
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Erreur enregistrement {i}: {e}")
                continue
        
        # Commit final
        if not dry_run:
            db.session.commit()
        
        logger.info(f"✅ Import terminé : {imported_count} importés, {error_count} erreurs")
        
        return {
            'file': os.path.basename(excel_file),
            'imported': imported_count,
            'errors': error_count,
            'status': 'success'
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import : {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'file': os.path.basename(excel_file),
            'imported': 0,
            'errors': 1,
            'status': 'error',
            'error_message': str(e)
        }


def import_folder(folder_path, client_code, dry_run=False):
    """Importe tous les fichiers Excel d'un dossier"""
    logger.info(f"\n{'='*70}")
    logger.info(f"IMPORT BATCH DE FICHIERS EXCEL")
    logger.info(f"{'='*70}")
    logger.info(f"Dossier : {folder_path}")
    logger.info(f"Client  : {client_code}")
    logger.info(f"Mode    : {'DRY-RUN (test)' if dry_run else 'IMPORT RÉEL'}")
    logger.info(f"{'='*70}\n")
    
    with app.app_context():
        # Récupérer le client
        client = Client.query.filter_by(code=client_code).first()
        if not client:
            raise ValueError(f"Client '{client_code}' introuvable")
        
        logger.info(f"✅ Client trouvé : {client.nom} ({client.code})")
        
        # Trouver tous les fichiers Excel
        excel_files = []
        for ext in ['*.xlsx', '*.xls']:
            excel_files.extend(list(Path(folder_path).glob(ext)))
        
        if not excel_files:
            logger.error(f"❌ Aucun fichier Excel trouvé dans : {folder_path}")
            return
        
        logger.info(f"\n📁 {len(excel_files)} fichier(s) Excel trouvé(s)\n")
        
        # Afficher la liste des fichiers
        for i, file in enumerate(excel_files, 1):
            logger.info(f"  {i}. {file.name}")
        
        logger.info("")
        
        # Demander confirmation si pas en dry-run
        if not dry_run:
            response = input(f"\n⚠️  Voulez-vous importer ces {len(excel_files)} fichiers ? (O/N) : ")
            if response.upper() not in ['O', 'OUI', 'Y', 'YES']:
                logger.info("❌ Import annulé par l'utilisateur")
                return
        
        # Importer chaque fichier
        results = []
        for i, excel_file in enumerate(excel_files, 1):
            logger.info(f"\n[{i}/{len(excel_files)}] Traitement de {excel_file.name}...")
            
            result = import_excel_file(str(excel_file), client, dry_run)
            results.append(result)
        
        # Résumé
        logger.info(f"\n{'='*70}")
        logger.info("RÉSUMÉ DE L'IMPORT BATCH")
        logger.info(f"{'='*70}\n")
        
        total_imported = sum(r['imported'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = sum(1 for r in results if r['status'] == 'error')
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            logger.info(f"{status_icon} {result['file']:<40} : {result['imported']} importés, {result['errors']} erreurs")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"TOTAL : {total_imported} enregistrements importés")
        logger.info(f"        {total_errors} erreurs")
        logger.info(f"        {success_count}/{len(results)} fichiers réussis")
        logger.info(f"{'='*70}\n")
        
        if dry_run:
            logger.info("ℹ️  Mode DRY-RUN : Aucune donnée n'a été insérée")
            logger.info("   Pour un import réel, relancez sans --dry-run")


def main():
    parser = argparse.ArgumentParser(description='Import batch de fichiers Excel vers PostgreSQL')
    parser.add_argument('--folder', required=True, help='Chemin vers le dossier contenant les fichiers Excel')
    parser.add_argument('--client-code', required=True, help='Code du client (ex: PARTNER, RG_SHERLOCK)')
    parser.add_argument('--dry-run', action='store_true', help='Mode test sans insertion réelle')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        logger.error(f"❌ Dossier introuvable : {args.folder}")
        sys.exit(1)
    
    try:
        import_folder(args.folder, args.client_code, args.dry_run)
        
        logger.info(f"\n{'='*70}")
        logger.info("✅ IMPORT BATCH TERMINÉ")
        logger.info(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
