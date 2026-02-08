"""
Script de correction du schéma donnees_enqueteur
Convertit les colonnes VARCHAR(10) en TEXT pour éviter les erreurs de troncation
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

print("🔧 Script de correction du schéma donnees_enqueteur")
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
            WHERE table_name = 'donnees_enqueteur'
            AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone')
            ORDER BY column_name
        """))
        
        print("\nTypes actuels :")
        for row in result:
            if row[2]:
                print(f"  - {row[0]}: {row[1]}({row[2]})")
            else:
                print(f"  - {row[0]}: {row[1]}")
        
        print("\n2️⃣ Application des corrections...")
        
        # Convertir elements_retrouves en TEXT
        print("\n  Conversion de elements_retrouves...")
        db.session.execute(text(
            "ALTER TABLE donnees_enqueteur ALTER COLUMN elements_retrouves TYPE TEXT"
        ))
        print("  ✓ elements_retrouves -> TEXT")
        
        # Convertir code_resultat en TEXT
        print("\n  Conversion de code_resultat...")
        db.session.execute(text(
            "ALTER TABLE donnees_enqueteur ALTER COLUMN code_resultat TYPE TEXT"
        ))
        print("  ✓ code_resultat -> TEXT")
        
        # Convertir flag_etat_civil_errone en TEXT
        print("\n  Conversion de flag_etat_civil_errone...")
        db.session.execute(text(
            "ALTER TABLE donnees_enqueteur ALTER COLUMN flag_etat_civil_errone TYPE TEXT"
        ))
        print("  ✓ flag_etat_civil_errone -> TEXT")
        
        # Commit les changements
        db.session.commit()
        
        print("\n3️⃣ Vérification après correction...")
        
        # Re-vérifier les types
        result = db.session.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'donnees_enqueteur'
            AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone')
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
