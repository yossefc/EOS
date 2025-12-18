"""
Script pour ajouter un tarif PARTNER
Usage: python scripts/add_tarif_partner.py <CODE_LETTRE> <MONTANT>
Exemple: python scripts/add_tarif_partner.py A 25.00
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from extensions import db
from models.client import Client
from models.tarifs import TarifClient
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_tarif_partner(code_lettre, montant):
    """Ajoute ou met à jour un tarif PARTNER"""
    
    # Trouver le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        logger.error("❌ Client PARTNER introuvable")
        return 1
    
    logger.info(f"✓ Client PARTNER trouvé (ID: {partner.id})")
    
    # Normaliser le code
    code_lettre = code_lettre.strip().upper()
    
    # Valider le montant
    try:
        montant_decimal = Decimal(str(montant))
        if montant_decimal < 0:
            logger.error(f"❌ Montant invalide: {montant} (doit être >= 0)")
            return 1
    except Exception as e:
        logger.error(f"❌ Montant invalide: {montant} - {e}")
        return 1
    
    # Vérifier si le tarif existe déjà
    existing = TarifClient.query.filter_by(
        client_id=partner.id,
        code_lettre=code_lettre
    ).first()
    
    if existing:
        # Mettre à jour
        existing.montant = montant_decimal
        existing.actif = True
        db.session.commit()
        logger.info(f"✅ Tarif {code_lettre} mis à jour: {float(montant_decimal)}€")
    else:
        # Créer
        tarif = TarifClient(
            client_id=partner.id,
            code_lettre=code_lettre,
            montant=montant_decimal,
            actif=True
        )
        db.session.add(tarif)
        db.session.commit()
        logger.info(f"✅ Tarif {code_lettre} créé: {float(montant_decimal)}€")
    
    return 0

if __name__ == '__main__':
    from app import create_app
    
    if len(sys.argv) != 3:
        print("Usage: python scripts/add_tarif_partner.py <CODE_LETTRE> <MONTANT>")
        print("Exemple: python scripts/add_tarif_partner.py A 25.00")
        sys.exit(1)
    
    code_lettre = sys.argv[1]
    montant = sys.argv[2]
    
    app = create_app()
    with app.app_context():
        sys.exit(add_tarif_partner(code_lettre, montant))

