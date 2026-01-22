import sys
import os
import pandas as pd
from io import BytesIO

# Configuration
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from extensions import db
from models import Client, ImportProfile, SherlockDonnee, Fichier
from import_engine import ImportEngine

def verify_sherlock_isolation():
    app = create_app()
    with app.app_context():
        print("🔍 Vérification de l'isolation Sherlock...")
        
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL', actif=True).first()
        
        if not profile:
            print("❌ Profil EXCEL actif non trouvé pour RG_SHERLOCK")
            return

        # 1. Simuler un fichier horizontal Sherlock (2 lignes de données + header)
        data = [
            ['DossierId', 'RéférenceInterne', 'Demande', 'EC-Prénom', 'EC-Nom Usage', 'AD-L6 Localité'],
            ['SH-999', 'REF-999', 'RECH', 'Sherlock', 'HOLMES', 'London'],
            ['SH-888', 'REF-888', 'RECH', 'John', 'WATSON', 'London']
        ]
        df = pd.DataFrame(data[1:], columns=data[0])
        output = BytesIO()
        df.to_excel(output, index=False)
        content = output.getvalue()
        
        # 2. Importer via ImportEngine
        engine = ImportEngine(profile)
        records = engine.parse_content(content)
        
        print(f"  → {len(records)} enregistrements parsés")
        
        # 3. Créer un Fichier mock
        fichier = Fichier(nom="test_isolation.xlsx", client_id=client.id)
        db.session.add(fichier)
        db.session.flush()
        
        for r in records:
            obj = engine.create_donnee_from_record(r, fichier_id=fichier.id, client_id=client.id)
            print(f"  → Objet créé: {type(obj).__name__}")
            if isinstance(obj, SherlockDonnee):
                print(f"    - Dossier: {obj.dossier_id}, Nom: {obj.ec_nom_usage}")
            else:
                print(f"    ❌ TYPE INCORRECT: {type(obj).__name__}")
        
        db.session.commit()
        print("✅ Vérification Sherlock Isolation terminée.")

if __name__ == "__main__":
    verify_sherlock_isolation()
