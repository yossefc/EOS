"""Vérifier l'enquête originale de PEVET"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from extensions import db

app = create_app()

with app.app_context():
    c = Donnee.query.get(612)
    
    print("CONTESTATION PEVET (ID 612):")
    print(f"  nom: {c.nom}")
    print(f"  prenom: {c.prenom}")
    print(f"  enquete_originale_id: {c.enquete_originale_id}")
    print(f"  numeroDemandeContestee: {c.numeroDemandeContestee}")
    
    if c.enquete_originale_id:
        orig = Donnee.query.get(c.enquete_originale_id)
        print(f"\nENQUÊTE ORIGINALE LIÉE:")
        print(f"  ID: {orig.id}")
        print(f"  Nom: {orig.nom} {orig.prenom}")
        print(f"  Statut: {orig.statut_validation}")
    else:
        print("\n❌ PAS de lien direct enquete_originale_id")
    
    print("\n" + "="*60)
    print("RECHERCHE DANS LES ARCHIVES PAR NOM...")
    print("="*60)
    
    # Rechercher les enquêtes archivées PEVET ou ADELINE
    enqs = Donnee.query.filter(
        Donnee.est_contestation == False,
        Donnee.client_id == c.client_id,
        db.or_(
            Donnee.nom.ilike('%PEVET%'),
            Donnee.prenom.ilike('%ADELINE%'),
            db.and_(
                Donnee.nom.ilike('%ADELINE%'),
                Donnee.prenom.ilike('%PEVET%')
            )
        )
    ).limit(10).all()
    
    print(f"\nTrouvé {len(enqs)} enquêtes:")
    for e in enqs:
        print(f"  - ID {e.id}: {e.nom} {e.prenom}")
        print(f"    Statut: {e.statut_validation}, Dossier: {e.numeroDossier}")
