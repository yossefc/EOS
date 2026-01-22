import os
import sys
import yaml

# Définir DATABASE_URL et PYTHONPATH
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import Client, ImportProfile, ImportFieldMapping

def seed_rg_sherlock():
    app = create_app()
    with app.app_context():
        print("🚀 Initialisation du client RG_SHERLOCK (Isolation)...")
        
        # 1. Créer le client
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        if not client:
            client = Client(code='RG_SHERLOCK', nom="RG Sherlock", actif=True)
            db.session.add(client)
            db.session.flush()
            print(f"  → Client créé (ID: {client.id})")
        else:
            print(f"  → Client existant (ID: {client.id})")

        # 2. Créer le profil d'import (Horizontal standard désormais)
        profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL').first()
        if not profile:
            profile = ImportProfile(
                client_id=client.id,
                name="Sherlock Import Standard",
                file_type="EXCEL", # Passage en horizontal
                sheet_name="Sheet1",
                encoding="utf-8",
                actif=True
            )
            db.session.add(profile)
            db.session.flush()
            print(f"  → Profil d'import EXCEL créé (ID: {profile.id})")
        else:
            print(f"  → Profil d'import EXCEL existant (ID: {profile.id})")
            
        # Désactiver l'ancien profil vertical si présent
        old_profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL_VERTICAL').first()
        if old_profile:
            old_profile.actif = False
            print("  → Ancien profil EXCEL_VERTICAL désactivé")

        # 3. Charger le YAML pour peupler les mappings
        base_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(base_dir, '..', 'clients', 'rg_sherlock', 'mapping_import.yaml')
        
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Supprimer anciens mappings pour ce profil
            ImportFieldMapping.query.filter_by(import_profile_id=profile.id).delete()
            
            for m in config.get('mappings', []):
                source_key = m.get('source_key')
                if not source_key or source_key.startswith('__'):
                    continue
                
                mapping = ImportFieldMapping(
                    import_profile_id=profile.id,
                    column_name=source_key,
                    internal_field=m.get('candidate_fields')[0],
                    is_required=m.get('required', False)
                )
                db.session.add(mapping)
            
            print(f"  → {len(config.get('mappings', []))} mappings enregistrés")
        
        db.session.commit()
        print("✅ Client RG_SHERLOCK configuré avec succès.")

if __name__ == "__main__":
    seed_rg_sherlock()
