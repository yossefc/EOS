"""
Script pour agrandir la colonne elements_retrouves
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║    Agrandissement de la colonne elements_retrouves            ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            print("► Agrandissement de elements_retrouves dans donnees_enqueteur...")
            db.session.execute(text("""
                ALTER TABLE donnees_enqueteur 
                ALTER COLUMN elements_retrouves TYPE VARCHAR(255)
            """))
            db.session.commit()
            print("  ✅ Colonne elements_retrouves agrandie (VARCHAR(255))\n")
            
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


