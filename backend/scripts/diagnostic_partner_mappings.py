"""
Script de diagnostic pour vérifier les mappings PARTNER
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

def diagnostic_mappings():
    """Affiche tous les mappings PARTNER"""
    
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
    
    # Lister tous les mappings
    mappings = ImportFieldMapping.query.filter_by(
        import_profile_id=profile.id
    ).order_by(ImportFieldMapping.internal_field).all()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"MAPPINGS PARTNER ({len(mappings)} champs)")
    logger.info(f"{'='*60}\n")
    
    for mapping in mappings:
        logger.info(f"  {mapping.internal_field:30} -> {mapping.column_name or '(défaut)'}")
    
    logger.info(f"\n{'='*60}")
    
    # Vérifier les champs critiques
    critical_fields = {
        'dateNaissance': 'JOUR',
        'dateNaissance_mois': 'MOIS',
        'dateNaissance_annee': 'ANNEE NAISSANCE',
        'lieuNaissance': 'LIEUNAISSANCE',
        'nomPatronymique': 'NJF',
        'instructions': 'INSTRUCTIONS',
        'recherche': 'RECHERCHE'
    }
    
    logger.info(f"\n{'='*60}")
    logger.info("VÉRIFICATION DES CHAMPS CRITIQUES")
    logger.info(f"{'='*60}\n")
    
    for internal_field, expected_column in critical_fields.items():
        mapping = next((m for m in mappings if m.internal_field == internal_field), None)
        if mapping:
            if mapping.column_name == expected_column:
                logger.info(f"  ✅ {internal_field:30} -> {mapping.column_name}")
            else:
                logger.warning(f"  ⚠️  {internal_field:30} -> {mapping.column_name} (attendu: {expected_column})")
        else:
            logger.error(f"  ❌ {internal_field:30} -> MANQUANT (attendu: {expected_column})")
    
    return 0

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        sys.exit(diagnostic_mappings())

