"""
Script d'export des règles tarifaires PARTNER
Génère un fichier SQL pour transférer vers un autre ordinateur
"""
import os
import sys
import codecs
from datetime import datetime

# Fixer l'encodage
if hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
if hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Définir DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db'

print("📤 Export des règles tarifaires PARTNER")
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
            print("\n❌ Aucun client PARTNER trouvé")
            sys.exit(1)
        
        print(f"\n✓ Client : {partner_client.nom} (code: {partner_client.code})")
        
        # Récupérer toutes les règles
        rules = PartnerTarifRule.query.filter_by(client_id=partner_client.id).all()
        
        if not rules:
            print("\n❌ Aucune règle tarifaire à exporter")
            sys.exit(1)
        
        print(f"✓ {len(rules)} règle(s) trouvée(s)")
        
        # Générer le fichier SQL
        output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EXPORT_PARTNER_TARIFS.sql')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Export des règles tarifaires PARTNER\n")
            f.write(f"-- Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Client: {partner_client.nom} (code: {partner_client.code})\n\n")
            
            f.write("-- Supprimer les règles existantes pour ce client PARTNER\n")
            f.write("DELETE FROM partner_tarif_rules WHERE client_id = (SELECT id FROM clients WHERE code != 'EOS' LIMIT 1);\n\n")
            
            f.write("-- Insérer les règles tarifaires\n")
            for rule in rules:
                amount = float(rule.amount) if rule.amount else 0
                f.write(
                    f"INSERT INTO partner_tarif_rules (client_id, tarif_lettre, request_key, amount, created_at, updated_at) "
                    f"VALUES ((SELECT id FROM clients WHERE code != 'EOS' LIMIT 1), '{rule.tarif_lettre}', '{rule.request_key}', {amount}, NOW(), NOW());\n"
                )
        
        print(f"\n✅ Export terminé !")
        print(f"📁 Fichier créé : {output_file}")
        print(f"\n📋 Instructions :")
        print(f"   1. Copiez ce fichier sur l'autre ordinateur (clé USB, email, etc.)")
        print(f"   2. Placez-le dans D:\\EOS\\")
        print(f"   3. Exécutez : python backend\\import_partner_tarifs.py")
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
