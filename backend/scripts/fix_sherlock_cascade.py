import os
import sys
from sqlalchemy import text

# Définir DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db

def fix_cascade():
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        try:
            print("🚀 Correction de la contrainte pour permettre la suppression en cascade...")
            
            # 1. Supprimer l'ancienne contrainte
            print("  → Suppression de l'ancienne contrainte...")
            conn.execute(text('ALTER TABLE sherlock_donnees DROP CONSTRAINT IF EXISTS sherlock_donnees_fichier_id_fkey'))
            
            # 2. Ajouter la nouvelle avec ON DELETE CASCADE
            print("  → Ajout de la contrainte avec ON DELETE CASCADE...")
            conn.execute(text("""
                ALTER TABLE sherlock_donnees 
                ADD CONSTRAINT sherlock_donnees_fichier_id_fkey 
                FOREIGN KEY (fichier_id) REFERENCES fichiers(id) ON DELETE CASCADE
            """))
            
            trans.commit()
            print("✅ Contrainte mise à jour avec succès.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    fix_cascade()
