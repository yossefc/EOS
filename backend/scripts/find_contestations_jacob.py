"""Script pour trouver les contestations de JACOB VANILLE"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Chercher les enquêtes JACOB VANILLE
    donnees = Donnee.query.filter(
        Donnee.nom.ilike('%JACOB%'), 
        Donnee.prenom.ilike('%VANILLE%')
    ).all()
    
    if donnees:
        print(f"\n✅ Enquêtes JACOB VANILLE trouvées :\n")
        for d in donnees:
            print(f"ID: {d.id} - Dossier: {d.numeroDossier} - Type: {d.typeDemande}")
            
            # Chercher les contestations liées
            contestations = Donnee.query.filter_by(
                enquete_originale_id=d.id,
                est_contestation=True
            ).all()
            
            if contestations:
                print(f"  🔥 {len(contestations)} contestation(s) trouvée(s) :")
                for c in contestations:
                    print(f"    - ID: {c.id}")
                    print(f"      Numéro Dossier: {c.numeroDossier}")
                    print(f"      Type: {c.typeDemande}")
                    print(f"      Date contestation: {c.date_contestation}")
                    print(f"      Motif code: {c.motif_contestation_code}")
                    print(f"      Motif détail: {c.motif_contestation_detail}")
            else:
                print("  ℹ️  Aucune contestation liée")
            print()
    
    # Chercher aussi toutes les contestations avec JACOB VANILLE
    print("\n--- Recherche directe des contestations ---\n")
    contestations_directes = Donnee.query.filter(
        Donnee.nom.ilike('%JACOB%'),
        Donnee.prenom.ilike('%VANILLE%'),
        Donnee.est_contestation == True
    ).all()
    
    if contestations_directes:
        print(f"✅ {len(contestations_directes)} contestation(s) directe(s) :")
        for c in contestations_directes:
            print(f"  ID: {c.id}")
            print(f"  Numéro Dossier: {c.numeroDossier}")
            print(f"  Type: {c.typeDemande}")
            print(f"  Enquête originale ID: {c.enquete_originale_id}")
    else:
        print("❌ Aucune contestation directe trouvée")
