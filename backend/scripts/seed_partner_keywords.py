"""
Script pour initialiser les mots-clés PARTNER (parsing RECHERCHE)
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from app import create_app
from models.client import Client
from models.partner_models import PartnerRequestKeyword

# Créer l'application
app = create_app()


def seed_keywords():
    """Initialise les mots-clés de base pour PARTNER"""
    with app.app_context():
        try:
            # Récupérer le client PARTNER
            partner = Client.query.filter_by(code='PARTNER').first()
            if not partner:
                print("❌ Client PARTNER non trouvé. Créez-le d'abord.")
                return
            
            print(f"🔄 Initialisation des mots-clés pour {partner.nom} (ID: {partner.id})")
            
            # Définir les mots-clés de base
            keywords_data = [
                # ADDRESS
                {'request_code': 'ADDRESS', 'pattern': 'ADRESSE', 'priority': 10},
                {'request_code': 'ADDRESS', 'pattern': 'ADR', 'priority': 5},
                
                # PHONE
                {'request_code': 'PHONE', 'pattern': 'TELEPHONE', 'priority': 10},
                {'request_code': 'PHONE', 'pattern': 'TEL', 'priority': 5},
                
                # EMPLOYER
                {'request_code': 'EMPLOYER', 'pattern': 'EMPLOYEUR', 'priority': 10},
                {'request_code': 'EMPLOYER', 'pattern': 'EMPLOI', 'priority': 5},
                
                # BANK
                {'request_code': 'BANK', 'pattern': 'BANQUE', 'priority': 10},
                {'request_code': 'BANK', 'pattern': 'COORDONNEES BANCAIRES', 'priority': 15},
                {'request_code': 'BANK', 'pattern': 'RIB', 'priority': 5},
                
                # BIRTH
                {'request_code': 'BIRTH', 'pattern': 'DATE ET LIEU DE NAISSANCE', 'priority': 20},
                {'request_code': 'BIRTH', 'pattern': 'LIEU DE NAISSANCE', 'priority': 15},
                {'request_code': 'BIRTH', 'pattern': 'DATE DE NAISSANCE', 'priority': 15},
                {'request_code': 'BIRTH', 'pattern': 'NAISSANCE', 'priority': 5},
            ]
            
            created_count = 0
            updated_count = 0
            
            for kw_data in keywords_data:
                # Vérifier si existe déjà
                existing = PartnerRequestKeyword.query.filter_by(
                    client_id=partner.id,
                    request_code=kw_data['request_code'],
                    pattern=kw_data['pattern']
                ).first()
                
                if existing:
                    # Mettre à jour la priorité si changée
                    if existing.priority != kw_data['priority']:
                        existing.priority = kw_data['priority']
                        updated_count += 1
                else:
                    # Créer nouveau
                    keyword = PartnerRequestKeyword(
                        client_id=partner.id,
                        request_code=kw_data['request_code'],
                        pattern=kw_data['pattern'],
                        is_regex=False,
                        priority=kw_data['priority']
                    )
                    db.session.add(keyword)
                    created_count += 1
            
            db.session.commit()
            
            print(f"✅ Mots-clés initialisés:")
            print(f"   - {created_count} créés")
            print(f"   - {updated_count} mis à jour")
            
            # Afficher le résumé
            total = PartnerRequestKeyword.query.filter_by(client_id=partner.id).count()
            print(f"\n📊 Total: {total} mots-clés configurés")
            
            # Afficher par type
            for code in ['ADDRESS', 'PHONE', 'EMPLOYER', 'BANK', 'BIRTH']:
                count = PartnerRequestKeyword.query.filter_by(
                    client_id=partner.id,
                    request_code=code
                ).count()
                print(f"   - {code}: {count} patterns")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")
            raise


if __name__ == '__main__':
    seed_keywords()




