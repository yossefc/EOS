"""
Script pour créer toutes les tables manquantes dans PostgreSQL
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         Création des tables manquantes PostgreSQL            ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Liste toutes les tables existantes
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            existing_tables = [row[0] for row in result]
            print(f"► Tables existantes ({len(existing_tables)}) :")
            for table in existing_tables:
                print(f"  - {table}")
            print()
            
            # Créer toutes les tables manquantes
            print("► Création des tables manquantes...")
            db.create_all()
            print("  ✅ Toutes les tables ont été créées/vérifiées")
            print()
            
            # Re-vérifier
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            new_tables = [row[0] for row in result]
            added = set(new_tables) - set(existing_tables)
            
            if added:
                print(f"► Tables ajoutées ({len(added)}) :")
                for table in sorted(added):
                    print(f"  + {table}")
            else:
                print("► Aucune nouvelle table ajoutée (toutes existaient déjà)")
            
            print()
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║                  ✅ TERMINÉ AVEC SUCCÈS                        ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())


