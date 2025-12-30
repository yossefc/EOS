"""
Script pour ajouter le champ 'instructions' pour PARTNER
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         Ajout du champ 'instructions' (PARTNER)               ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            print("► Vérification de la colonne 'instructions'...")
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = 'donnees'
                  AND column_name = 'instructions'
            """))
            
            if result.fetchone():
                print("  ⏭️  Colonne 'instructions' déjà existante (ignorée)\n")
                return 0
            
            print("  ✅ Colonne 'instructions' inexistante, ajout en cours...\n")
            
            # Ajouter la colonne
            print("► Ajout de la colonne 'instructions' dans 'donnees'...")
            db.session.execute(text("""
                ALTER TABLE donnees ADD COLUMN instructions TEXT
            """))
            db.session.commit()
            print("  ✅ Colonne 'instructions' ajoutée (TEXT, nullable)\n")
            
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║              ✅ Migration terminée avec succès !               ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())




