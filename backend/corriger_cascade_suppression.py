"""
Script pour ajouter CASCADE sur la suppression des données
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║    Correction de la contrainte de suppression CASCADE         ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            print("► Suppression de l'ancienne contrainte...")
            db.session.execute(text("""
                ALTER TABLE donnees_enqueteur 
                DROP CONSTRAINT IF EXISTS donnees_enqueteur_donnee_id_fkey
            """))
            db.session.commit()
            print("  ✅ Ancienne contrainte supprimée\n")
            
            print("► Ajout de la nouvelle contrainte avec CASCADE...")
            db.session.execute(text("""
                ALTER TABLE donnees_enqueteur 
                ADD CONSTRAINT donnees_enqueteur_donnee_id_fkey 
                FOREIGN KEY (donnee_id) 
                REFERENCES donnees(id) 
                ON DELETE CASCADE
            """))
            db.session.commit()
            print("  ✅ Nouvelle contrainte ajoutée avec CASCADE\n")
            
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║              ✅ Correction terminée avec succès !              ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            print("Vous pouvez maintenant supprimer des dossiers sans erreur.")
            print("Les données enquêteur seront automatiquement supprimées.\n")
            
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




