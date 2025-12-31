"""
Script pour initialiser les tarifs PARTNER (lettre + combinaisons)
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from app import create_app
from models.client import Client
from models.partner_models import PartnerTarifRule

# Créer l'application
app = create_app()


def seed_tarifs():
    """Initialise les tarifs de base pour PARTNER"""
    with app.app_context():
        try:
            # Récupérer le client PARTNER
            partner = Client.query.filter_by(code='PARTNER').first()
            if not partner:
                print("❌ Client PARTNER non trouvé. Créez-le d'abord.")
                return
            
            print(f"🔄 Initialisation des tarifs pour {partner.nom} (ID: {partner.id})")
            
            # Définir les tarifs de base
            # Format: (lettre, demandes, montant)
            tarifs_data = [
                # Tarifs unitaires (lettre A)
                ('A', ['ADDRESS'], 50.00),
                ('A', ['PHONE'], 40.00),
                ('A', ['EMPLOYER'], 60.00),
                ('A', ['BANK'], 55.00),
                ('A', ['BIRTH'], 45.00),
                
                # Tarifs combinés courants (lettre A)
                ('A', ['ADDRESS', 'PHONE'], 80.00),
                ('A', ['ADDRESS', 'EMPLOYER'], 100.00),
                ('A', ['ADDRESS', 'PHONE', 'EMPLOYER'], 130.00),
                ('A', ['BANK', 'BIRTH'], 90.00),
                
                # Tarifs unitaires (lettre W - exemple)
                ('W', ['ADDRESS'], 45.00),
                ('W', ['PHONE'], 35.00),
                ('W', ['EMPLOYER'], 55.00),
                ('W', ['BANK'], 50.00),
                ('W', ['BIRTH'], 40.00),
            ]
            
            created_count = 0
            updated_count = 0
            
            for lettre, demandes, montant in tarifs_data:
                # Construire la clé normalisée
                request_key = PartnerTarifRule.build_request_key(demandes)
                
                # Vérifier si existe déjà
                existing = PartnerTarifRule.query.filter_by(
                    client_id=partner.id,
                    tarif_lettre=lettre,
                    request_key=request_key
                ).first()
                
                if existing:
                    # Mettre à jour le montant si changé
                    if float(existing.amount) != montant:
                        existing.amount = montant
                        updated_count += 1
                else:
                    # Créer nouveau
                    tarif = PartnerTarifRule(
                        client_id=partner.id,
                        tarif_lettre=lettre,
                        request_key=request_key,
                        amount=montant
                    )
                    db.session.add(tarif)
                    created_count += 1
            
            db.session.commit()
            
            print(f"✅ Tarifs initialisés:")
            print(f"   - {created_count} créés")
            print(f"   - {updated_count} mis à jour")
            
            # Afficher le résumé
            total = PartnerTarifRule.query.filter_by(client_id=partner.id).count()
            print(f"\n📊 Total: {total} règles de tarifs configurées")
            
            # Afficher par lettre
            for lettre in ['A', 'W']:
                count = PartnerTarifRule.query.filter_by(
                    client_id=partner.id,
                    tarif_lettre=lettre
                ).count()
                if count > 0:
                    print(f"   - Lettre {lettre}: {count} règles")
            
            print("\n📝 Exemples de règles:")
            examples = PartnerTarifRule.query.filter_by(
                client_id=partner.id
            ).limit(5).all()
            for rule in examples:
                print(f"   - {rule.tarif_lettre} + {rule.request_key} = {rule.amount}€")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")
            raise


if __name__ == '__main__':
    seed_tarifs()




