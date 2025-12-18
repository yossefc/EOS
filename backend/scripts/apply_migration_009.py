"""
Script pour appliquer la migration 009 : 
Ajout de dateNaissance_maj et lieuNaissance_maj dans la table Donnee
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
    """Applique la migration 009"""
    with app.app_context():
        try:
            print("🔄 Application de la migration 009...")
            print("   Ajout de dateNaissance_maj et lieuNaissance_maj dans la table donnees")
            
            # Vérifier si les colonnes existent déjà
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'donnees' 
                AND column_name IN ('dateNaissance_maj', 'lieuNaissance_maj')
            """)
            
            result = db.session.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            if len(existing_columns) == 2:
                print("✅ Les colonnes existent déjà. Rien à faire.")
                return
            
            print(f"   Colonnes existantes : {existing_columns}")
            
            # Ajouter les colonnes si elles n'existent pas
            if 'dateNaissance_maj' not in existing_columns:
                db.session.execute(text("ALTER TABLE donnees ADD COLUMN \"dateNaissance_maj\" DATE"))
                print("   ✓ dateNaissance_maj ajoutée")
            
            if 'lieuNaissance_maj' not in existing_columns:
                db.session.execute(text("ALTER TABLE donnees ADD COLUMN \"lieuNaissance_maj\" VARCHAR(50)"))
                print("   ✓ lieuNaissance_maj ajoutée")
            
            # Créer l'index
            try:
                db.session.execute(text('CREATE INDEX idx_donnee_dateNaissance_maj ON donnees ("dateNaissance_maj")'))
                print("   ✓ Index idx_donnee_dateNaissance_maj créé")
            except Exception as e:
                if "already exists" in str(e):
                    print("   ℹ Index idx_donnee_dateNaissance_maj existe déjà")
                else:
                    raise
            
            db.session.commit()
            print("✅ Migration 009 appliquée avec succès!")
            print("\n📝 Note : Les champs suivants ont été ajoutés à la table donnees:")
            print("   - dateNaissance_maj (DATE) : Date de naissance mise à jour par l'enquêteur")
            print("   - lieuNaissance_maj (VARCHAR(50)) : Lieu de naissance mis à jour par l'enquêteur")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'application de la migration : {e}")
            raise

if __name__ == '__main__':
    apply_migration()

