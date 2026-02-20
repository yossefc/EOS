"""Trouver une contestation avec un numeroDossier valide"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Chercher une contestation avec numeroDossier valide
    contestations = Donnee.query.filter(
        Donnee.est_contestation == True,
        Donnee.numeroDossier.isnot(None),
        Donnee.numeroDossier != ''
    ).limit(10).all()
    
    if contestations:
        print(f"\n✅ {len(contestations)} contestation(s) avec numeroDossier valide :\n")
        for c in contestations[:5]:
            print(f"ID: {c.id}")
            print(f"  Numéro Dossier: {c.numeroDossier}")
            print(f"  Nom: {c.nom}")
            print(f"  Prénom: {c.prenom}")
            print(f"  Type: {c.typeDemande}")
            print(f"  Enquête originale ID: {c.enquete_originale_id}")
            print(f"  Motif: {c.motif_contestation_detail}")
            print(f"  Date contestation: {c.date_contestation}")
            
            # Tester l'API
            print(f"\n  🔗 URL test: http://localhost:5000/api/historique-enquete/{c.numeroDossier}")
            print()
    else:
        print("❌ Aucune contestation avec numeroDossier valide")
        
    # Stats
    total_contestations = Donnee.query.filter_by(est_contestation=True).count()
    with_numero = Donnee.query.filter(
        Donnee.est_contestation == True,
        Donnee.numeroDossier.isnot(None),
        Donnee.numeroDossier != ''
    ).count()
    
    print(f"\n📊 Stats: {with_numero}/{total_contestations} contestations ont un numeroDossier")
