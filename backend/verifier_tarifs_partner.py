"""
Script de vérification des règles tarifaires PARTNER
"""
import os
import sys
import codecs

# Fixer l'encodage
if hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
if hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Définir DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db'

print("🔍 Vérification des règles tarifaires PARTNER")
print("=" * 60)

from app import create_app
from models.partner_models import PartnerTarifRule
from models.client import Client
from extensions import db

app = create_app()

with app.app_context():
    try:
        # Trouver le client PARTNER
        partner_client = Client.query.filter(Client.code != 'EOS').first()
        
        if not partner_client:
            print("\n❌ Aucun client PARTNER trouvé dans la base de données")
            print("\nAssurez-vous que le client PARTNER a été importé.")
            sys.exit(1)
        
        print(f"\n✓ Client trouvé : {partner_client.nom} (ID: {partner_client.id})")
        
        # Compter les règles tarifaires
        total_rules = PartnerTarifRule.query.filter_by(client_id=partner_client.id).count()
        
        print(f"\n📊 Nombre de règles tarifaires : {total_rules}")
        
        if total_rules == 0:
            print("\n❌ PROBLÈME : Aucune règle tarifaire PARTNER trouvée !")
            print("\n💡 Solution :")
            print("   Sur l'ordinateur SOURCE, exécutez :")
            print("   python backend/export_partner_tarifs.py")
            print("\n   Puis copiez le fichier généré vers ce PC et exécutez :")
            print("   python backend/import_partner_tarifs.py")
        else:
            print("\n✓ Règles tarifaires présentes")
            print("\n📋 Détails par lettre :")
            
            # Grouper par lettre
            from sqlalchemy import func
            results = db.session.query(
                PartnerTarifRule.tarif_lettre,
                func.count(PartnerTarifRule.id)
            ).filter_by(client_id=partner_client.id)\
             .group_by(PartnerTarifRule.tarif_lettre)\
             .order_by(PartnerTarifRule.tarif_lettre)\
             .all()
            
            for lettre, count in results:
                print(f"   Lettre {lettre}: {count} règle(s)")
            
            # Vérifier si W existe
            w_rules = PartnerTarifRule.query.filter_by(
                client_id=partner_client.id,
                tarif_lettre='W'
            ).count()
            
            if w_rules == 0:
                print(f"\n⚠️  ATTENTION : Aucune règle pour la lettre W")
                print("   Cette lettre est utilisée dans vos dossiers mais n'a pas de tarif configuré.")
            
            # Afficher quelques exemples de règles W si elles existent
            if w_rules > 0:
                print(f"\n📝 Exemples de règles W :")
                examples = PartnerTarifRule.query.filter_by(
                    client_id=partner_client.id,
                    tarif_lettre='W'
                ).limit(5).all()
                
                for rule in examples:
                    print(f"   W + {rule.request_key}: {rule.amount}€")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
