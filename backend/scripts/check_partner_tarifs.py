"""
Script pour vérifier les tarifs PARTNER configurés
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from extensions import db
from models.client import Client
from models.tarifs import TarifClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_partner_tarifs():
    """Vérifie et affiche les tarifs PARTNER"""
    
    # Trouver le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        logger.error("❌ Client PARTNER introuvable")
        return 1
    
    logger.info(f"✓ Client PARTNER trouvé (ID: {partner.id})")
    
    # Lister tous les tarifs PARTNER
    tarifs = TarifClient.query.filter_by(client_id=partner.id).all()
    
    if not tarifs:
        logger.warning("⚠️ Aucun tarif configuré pour PARTNER")
        logger.info("\n📝 Pour ajouter un tarif, exécutez:")
        logger.info("   python scripts/add_tarif_partner.py A 25.00")
        return 1
    
    logger.info(f"\n📋 {len(tarifs)} tarif(s) PARTNER trouvé(s):")
    logger.info("-" * 60)
    for tarif in tarifs:
        statut = "✅ ACTIF" if tarif.actif else "❌ INACTIF"
        logger.info(f"  Lettre: {tarif.code_lettre:3s} | Montant: {float(tarif.montant):7.2f}€ | {statut}")
    logger.info("-" * 60)
    
    # Vérifier spécifiquement le tarif A
    tarif_a = TarifClient.query.filter_by(
        client_id=partner.id,
        code_lettre='A',
        actif=True
    ).first()
    
    if tarif_a:
        logger.info(f"\n✅ Tarif A ACTIF trouvé: {float(tarif_a.montant)}€")
    else:
        logger.warning("\n⚠️ Tarif A non trouvé ou inactif !")
        logger.info("   Pour l'ajouter: python scripts/add_tarif_partner.py A 25.00")
    
    return 0

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        sys.exit(check_partner_tarifs())

