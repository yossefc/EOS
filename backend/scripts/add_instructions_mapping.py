"""
Script pour ajouter le mapping INSTRUCTIONS au profil PARTNER ENQUETES
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from extensions import db
from models.client import Client
from models.import_config import ImportProfile, ImportFieldMapping
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_instructions_mapping():
    """Ajoute le mapping INSTRUCTIONS au profil PARTNER ENQUETES"""
    
    # Trouver le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        logger.error("❌ Client PARTNER introuvable")
        return 1
    
    logger.info(f"✓ Client PARTNER trouvé (ID: {partner.id})")
    
    # Trouver le profil ENQUETES
    profile = ImportProfile.query.filter_by(
        client_id=partner.id,
        name='ENQUETES'
    ).first()
    
    if not profile:
        logger.error("❌ Profil ENQUETES introuvable")
        return 1
    
    logger.info(f"✓ Profil ENQUETES trouvé (ID: {profile.id})")
    
    # Vérifier si le mapping existe déjà
    existing = ImportFieldMapping.query.filter_by(
        import_profile_id=profile.id,
        internal_field='instructions'
    ).first()
    
    if existing:
        logger.info("⏭️  Mapping INSTRUCTIONS déjà existant (ignoré)")
        return 0
    
    # Créer le mapping
    mapping = ImportFieldMapping(
        import_profile_id=profile.id,
        internal_field='instructions',
        column_name='INSTRUCTIONS',
        strip_whitespace=True,
        is_required=False
    )
    db.session.add(mapping)
    db.session.commit()
    
    logger.info("✅ Mapping INSTRUCTIONS ajouté avec succès")
    return 0

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        sys.exit(add_instructions_mapping())


