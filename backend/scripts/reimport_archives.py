"""
Supprime les archives PARTNER mal importees puis relance l'import corrige.
Corrige aussi les numeroDossier='None' (texte) en vrai NULL pour EOS.

Usage:
    python reimport_archives.py              # Dry-run
    python reimport_archives.py --commit     # Supprime + reimporte
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur

parser = argparse.ArgumentParser()
parser.add_argument('--commit', action='store_true')
args = parser.parse_args()

app = create_app()
with app.app_context():
    # 1. Compter les archives PARTNER actuelles
    partner_archives = Donnee.query.filter(
        Donnee.client_id == 11,
        Donnee.statut_validation.in_(['archive', 'archivee'])
    ).all()
    partner_ids = [d.id for d in partner_archives]

    partner_de = DonneeEnqueteur.query.filter(
        DonneeEnqueteur.donnee_id.in_(partner_ids)
    ).count() if partner_ids else 0

    print(f"Archives PARTNER actuelles: {len(partner_archives)} Donnee, {partner_de} DonneeEnqueteur")

    # 2. Corriger les numeroDossier='None' EOS
    eos_none = Donnee.query.filter(
        Donnee.client_id == 1,
        Donnee.numeroDossier == 'None'
    ).count()
    print(f"EOS avec numeroDossier='None' (texte): {eos_none}")

    # 3. Corriger referenceDossier='None' PARTNER
    partner_ref_none = Donnee.query.filter(
        Donnee.client_id == 11,
        Donnee.referenceDossier == 'None'
    ).count()
    print(f"PARTNER avec referenceDossier='None' (texte): {partner_ref_none}")

    if args.commit:
        print("\n--- MODE COMMIT ---")

        # Supprimer les enquete_facturation liees aux DonneeEnqueteur PARTNER archives
        if partner_ids:
            partner_de_ids = [de.id for de in DonneeEnqueteur.query.filter(
                DonneeEnqueteur.donnee_id.in_(partner_ids)
            ).all()]

            if partner_de_ids:
                from models.tarifs import EnqueteFacturation
                deleted_fact = EnqueteFacturation.query.filter(
                    EnqueteFacturation.donnee_enqueteur_id.in_(partner_de_ids)
                ).delete(synchronize_session=False)
                print(f"EnqueteFacturation PARTNER supprimees: {deleted_fact}")

            # Supprimer les DonneeEnqueteur PARTNER archives
            deleted_de = DonneeEnqueteur.query.filter(
                DonneeEnqueteur.donnee_id.in_(partner_ids)
            ).delete(synchronize_session=False)
            print(f"DonneeEnqueteur PARTNER supprimees: {deleted_de}")

        # Supprimer les EnqueteArchive et EnqueteArchiveFile liees
        from models.enquete_archive import EnqueteArchive
        from models.enquete_archive_file import EnqueteArchiveFile
        if partner_ids:
            deleted_af = EnqueteArchiveFile.query.filter(
                EnqueteArchiveFile.enquete_id.in_(partner_ids)
            ).delete(synchronize_session=False)
            deleted_a = EnqueteArchive.query.filter(
                EnqueteArchive.enquete_id.in_(partner_ids)
            ).delete(synchronize_session=False)
            print(f"EnqueteArchive/File supprimees: {deleted_a}/{deleted_af}")

        # Supprimer les EnqueteTerminee liees
        from models.enquetes_terminees import EnqueteTerminee
        if partner_ids:
            deleted_et = EnqueteTerminee.query.filter(
                EnqueteTerminee.donnee_id.in_(partner_ids)
            ).delete(synchronize_session=False)
            print(f"EnqueteTerminee PARTNER supprimees: {deleted_et}")

        # Detacher les enquete_originale_id qui referencent des archives PARTNER
        if partner_ids:
            detached = Donnee.query.filter(
                Donnee.enquete_originale_id.in_(partner_ids)
            ).update({'enquete_originale_id': None}, synchronize_session=False)
            print(f"Enquete_originale_id detachees: {detached}")

        # Supprimer les Donnee PARTNER archives
        deleted_d = Donnee.query.filter(
            Donnee.client_id == 11,
            Donnee.statut_validation.in_(['archive', 'archivee'])
        ).delete(synchronize_session=False)
        print(f"Donnee PARTNER archives supprimees: {deleted_d}")

        # Corriger EOS numeroDossier='None' -> NULL
        updated_eos = Donnee.query.filter(
            Donnee.client_id == 1,
            Donnee.numeroDossier == 'None'
        ).update({'numeroDossier': None}, synchronize_session=False)
        print(f"EOS numeroDossier 'None' -> NULL: {updated_eos}")

        db.session.commit()
        print("\nCOMMIT effectue. Relancez maintenant: python import_archives.py --commit")
    else:
        print("\nMode dry-run. Utilisez --commit pour appliquer.")
