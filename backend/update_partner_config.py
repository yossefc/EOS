import os

# Forcer DATABASE_URL pour PostgreSQL
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app, db
from models import Client, ImportProfile, ImportFieldMapping

app = create_app()

def update_mapping(profile_id, field, alias=None, is_required=None, default_value=None, remove_default=False):
    mapping = ImportFieldMapping.query.filter_by(
        import_profile_id=profile_id,
        internal_field=field
    ).first()
    if mapping:
        if alias is not None:
            mapping.column_name = alias
        if is_required is not None:
            mapping.is_required = is_required
        if remove_default:
            mapping.default_value = None
        elif default_value is not None:
            mapping.default_value = default_value
            
        print(f"  ✅ Mis à jour: {field} -> {mapping.column_name} (Required: {mapping.is_required}, Default: {mapping.default_value})")
    else:
        print(f"  ❌ Non trouvé: {field}")

with app.app_context():
    client = Client.query.filter_by(code='PARTNER').first()
    if not client:
        print("Client PARTNER non trouvé")
        exit()
    
    print(f"Client: {client.nom} (ID: {client.id})")
    
    # Profil Excel
    profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL').first()
    if not profile:
        print("Profil d'import EXCEL non trouvé")
        exit()
        
    print(f"Profil: {profile.name} (ID: {profile.id})")
    
    print("\nMise à jour finale des mappings...")
    
    # 1. Alias et flexibilité
    update_mapping(profile.id, 'numeroDossier', alias='NUM|N° Dossier', is_required=True)
    update_mapping(profile.id, 'instructions', alias='INSTRUCTIONS|MOTIF')
    update_mapping(profile.id, 'datedenvoie', alias='DATE ENVOI|DATE DU JOUR')
    
    # 2. SUPPRIMER LE DÉFAUT "ENQ" pour permettre la détection automatique
    update_mapping(profile.id, 'typeDemande', alias='', remove_default=True)
    
    db.session.commit()
    print("\n✅ Configuration PARTNER finalisée avec succès.")
