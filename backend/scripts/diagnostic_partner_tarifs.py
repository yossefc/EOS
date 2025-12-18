"""
Script de diagnostic pour vérifier les tarifs PARTNER
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from extensions import db
from models.client import Client
from models.tarifs import TarifClient
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnostic_tarifs():
    """Diagnostic complet des tarifs PARTNER"""
    
    # 1. Trouver le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        logger.error("❌ Client PARTNER introuvable")
        return 1
    
    logger.info(f"✓ Client PARTNER trouvé (ID: {partner.id})")
    
    # 2. Lister les tarifs configurés
    tarifs = TarifClient.query.filter_by(client_id=partner.id, actif=True).all()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TARIFS CONFIGURÉS ({len(tarifs)} tarifs)")
    logger.info(f"{'='*60}\n")
    
    if not tarifs:
        logger.error("❌ AUCUN TARIF CONFIGURÉ POUR PARTNER !")
        logger.info("\n⚠️  SOLUTION: Exécuter le script de création des tarifs PARTNER")
        return 1
    
    for tarif in tarifs:
        logger.info(f"  Lettre '{tarif.code_lettre}': {float(tarif.montant)}€ - {tarif.description or '(sans description)'}")
    
    # 3. Vérifier les enquêtes PARTNER
    enquetes = Donnee.query.filter_by(client_id=partner.id).limit(5).all()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"ÉCHANTILLON D'ENQUÊTES ({len(enquetes)} enquêtes)")
    logger.info(f"{'='*60}\n")
    
    for donnee in enquetes:
        donnee_enq = donnee.donnee_enqueteur
        tarif_lettre = donnee.tarif_lettre or '(vide)'
        montant_facture = donnee_enq.montant_facture if donnee_enq else 0
        
        # Chercher le tarif correspondant
        tarif_trouve = None
        if donnee.tarif_lettre:
            tarif_trouve = TarifClient.query.filter_by(
                client_id=partner.id,
                code_lettre=donnee.tarif_lettre.strip().upper(),
                actif=True
            ).first()
        
        status = "✅" if tarif_trouve else "❌"
        montant_attendu = float(tarif_trouve.montant) if tarif_trouve else 0
        
        logger.info(f"  Dossier {donnee.numeroDossier}:")
        logger.info(f"    - Tarif lettre: '{tarif_lettre}'")
        logger.info(f"    - Montant facturé: {montant_facture}€")
        logger.info(f"    - Tarif trouvé: {status} {montant_attendu}€ attendus")
        
        if montant_facture != montant_attendu:
            logger.warning(f"    ⚠️  ÉCART: {montant_facture}€ facturé vs {montant_attendu}€ attendu")
    
    return 0

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        sys.exit(diagnostic_tarifs())

