"""
Script pour appliquer la migration 010 : 
Suppression de date_naissance_corrigee et lieu_naissance_corrige de DonneeEnqueteur
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from sqlalchemy import text

# Importer create_app au lieu de app
from app import create_app

# Créer l'application
app = create_app()

def apply_migration():
    """Applique la migration 010"""
    with app.app_context():
        try:
            print("🔄 Application de la migration 010...")
            print("   Suppression de date_naissance_corrigee et lieu_naissance_corrige de donnees_enqueteur")
            
            # Vérifier si les colonnes existent avant de les supprimer
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'donnees_enqueteur' 
                AND column_name IN ('date_naissance_corrigee', 'lieu_naissance_corrige')
            """)
            
            result = db.session.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            if not existing_columns:
                print("✅ Les colonnes ont déjà été supprimées. Rien à faire.")
                return
            
            print(f"   Colonnes trouvées : {existing_columns}")
            
            # Supprimer les colonnes
            if 'date_naissance_corrigee' in existing_columns:
                db.session.execute(text("ALTER TABLE donnees_enqueteur DROP COLUMN date_naissance_corrigee"))
                print("   ✓ date_naissance_corrigee supprimée")
            
            if 'lieu_naissance_corrige' in existing_columns:
                db.session.execute(text("ALTER TABLE donnees_enqueteur DROP COLUMN lieu_naissance_corrige"))
                print("   ✓ lieu_naissance_corrige supprimée")
            
            db.session.commit()
            print("✅ Migration 010 appliquée avec succès!")
            print("\n📝 Note : Les données de naissance mises à jour sont maintenant stockées dans:")
            print("   - donnees.dateNaissance_maj")
            print("   - donnees.lieuNaissance_maj")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'application de la migration : {e}")
            raise

if __name__ == '__main__':
    apply_migration()

