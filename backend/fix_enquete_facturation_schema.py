"""
Script de correction du schéma enquete_facturation
Convertit tarif_eos_code et tarif_enqueteur_code de VARCHAR(10) à TEXT
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

print("🔧 Script de correction du schéma enquete_facturation")
print("=" * 60)

from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("\n1️⃣ Vérification du schéma actuel...")
        
        # Vérifier les types actuels
        result = db.session.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'enquete_facturation'
            AND column_name IN ('tarif_eos_code', 'tarif_enqueteur_code')
            ORDER BY column_name
        """))
        
        print("\nTypes actuels :")
        for row in result:
            if row[2]:
                print(f"  - {row[0]}: {row[1]}({row[2]})")
            else:
                print(f"  - {row[0]}: {row[1]}")
        
        print("\n2️⃣ Application des corrections...")
        
        # Convertir tarif_eos_code en TEXT
        print("\n  Conversion de tarif_eos_code...")
        db.session.execute(text(
            "ALTER TABLE enquete_facturation ALTER COLUMN tarif_eos_code TYPE TEXT"
        ))
        print("  ✓ tarif_eos_code -> TEXT")
        
        # Convertir tarif_enqueteur_code en TEXT
        print("\n  Conversion de tarif_enqueteur_code...")
        db.session.execute(text(
            "ALTER TABLE enquete_facturation ALTER COLUMN tarif_enqueteur_code TYPE TEXT"
        ))
        print("  ✓ tarif_enqueteur_code -> TEXT")
        
        # Commit les changements
        db.session.commit()
        
        print("\n3️⃣ Vérification après correction...")
        
        # Re-vérifier les types
        result = db.session.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'enquete_facturation'
            AND column_name IN ('tarif_eos_code', 'tarif_enqueteur_code')
            ORDER BY column_name
        """))
        
        print("\nTypes après correction :")
        for row in result:
            if row[2]:
                print(f"  - {row[0]}: {row[1]}({row[2]})")
            else:
                print(f"  - {row[0]}: {row[1]}")
        
        print("\n" + "=" * 60)
        print("✅ Correction du schéma terminée avec succès !")
        print("=" * 60)
        print("\nVous pouvez maintenant redémarrer l'application.")
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        sys.exit(1)
