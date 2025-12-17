"""
Script pour créer la table confirmation_options
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from models.confirmation_options import ConfirmationOption

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║    Création de la table confirmation_options                  ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            print("► Création de la table confirmation_options...")
            db.create_all()
            print("  ✅ Table confirmation_options créée\n")
            
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║              ✅ Création terminée avec succès !                ║")
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

