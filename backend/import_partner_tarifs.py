"""
Script d'import des règles tarifaires PARTNER
Importe les règles depuis le fichier EXPORT_PARTNER_TARIFS.sql
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

print("📥 Import des règles tarifaires PARTNER")
print("=" * 60)

from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

# Trouver le fichier SQL
sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EXPORT_PARTNER_TARIFS.sql')

if not os.path.exists(sql_file):
    print(f"\n❌ Fichier non trouvé : {sql_file}")
    print("\n💡 Assurez-vous d'avoir :")
    print("   1. Exécuté export_partner_tarifs.py sur l'ordinateur SOURCE")
    print("   2. Copié le fichier EXPORT_PARTNER_TARIFS.sql dans D:\\EOS\\")
    sys.exit(1)

print(f"\n✓ Fichier trouvé : {sql_file}")

with app.app_context():
    try:
        # Lire le fichier SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Séparer les commandes SQL
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        print(f"\n📊 {len(commands)} commande(s) SQL à exécuter")
        
        # Exécuter chaque commande
        for i, command in enumerate(commands, 1):
            if command:
                db.session.execute(text(command))
                if i % 10 == 0:
                    print(f"   Progression : {i}/{len(commands)}")
        
        # Commit
        db.session.commit()
        
        # Vérifier le résultat
        from models.partner_models import PartnerTarifRule
        from models.client import Client
        
        partner_client = Client.query.filter(Client.code != 'EOS').first()
        if partner_client:
            count = PartnerTarifRule.query.filter_by(client_id=partner_client.id).count()
            print(f"\n✅ Import terminé !")
            print(f"📊 {count} règle(s) tarifaire(s) importée(s)")
        else:
            print(f"\n⚠️  Import terminé mais aucun client PARTNER trouvé")
        
        print("\n🔄 Redémarrez l'application pour que les changements prennent effet.")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
