"""
Corrige le statut des enquetes 'valide' et 'validee' en 'archive'.
Ces enquetes ont ete exportees et validees, elles doivent etre archivees.

Usage:
    python fix_statut_valide.py          # Dry-run (affiche sans modifier)
    python fix_statut_valide.py --commit # Applique les modifications
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

parser = argparse.ArgumentParser()
parser.add_argument('--commit', action='store_true', help='Appliquer les modifications')
args = parser.parse_args()

app = create_app()
with app.app_context():
    # Compter les enquetes 'valide' et 'validee'
    valide_count = Donnee.query.filter(Donnee.statut_validation == 'valide').count()
    validee_count = Donnee.query.filter(Donnee.statut_validation == 'validee').count()

    print(f"Enquetes avec statut 'valide': {valide_count}")
    print(f"Enquetes avec statut 'validee': {validee_count}")
    print(f"Total a archiver: {valide_count + validee_count}")

    if args.commit:
        # Mettre a jour 'valide' -> 'archive'
        updated_valide = Donnee.query.filter(
            Donnee.statut_validation == 'valide'
        ).update({'statut_validation': 'archive'}, synchronize_session=False)

        # Mettre a jour 'validee' -> 'archive'
        updated_validee = Donnee.query.filter(
            Donnee.statut_validation == 'validee'
        ).update({'statut_validation': 'archive'}, synchronize_session=False)

        db.session.commit()
        print(f"\nMis a jour: {updated_valide} 'valide' -> 'archive'")
        print(f"Mis a jour: {updated_validee} 'validee' -> 'archive'")
        print("COMMIT effectue.")
    else:
        print("\nMode dry-run. Utilisez --commit pour appliquer.")
