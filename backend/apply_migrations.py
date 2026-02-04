"""
Script pour appliquer les migrations Alembic à la base de données PostgreSQL
Ce script garantit que DATABASE_URL est défini avant d'exécuter les migrations
"""
import os
import sys

# Définir DATABASE_URL AVANT tout import
# Note: Utilise les credentials par défaut postgres:postgres
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db'

print("✓ DATABASE_URL définie dans le processus Python")
print(f"  {os.environ['DATABASE_URL'][:50]}...")
print()

# Chemin vers le dossier migrations (relatif au script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(BASE_DIR, 'migrations')

# Importer l'application Flask
from app import create_app
from flask_migrate import stamp, upgrade, current
from extensions import db

# Créer l'application
app = create_app()

# Appliquer les migrations dans le contexte de l'application
with app.app_context():
    print(f"[INFO] Utilisation du dossier migrations : {MIGRATIONS_DIR}")
    print("[INFO] Verification de l'etat des migrations...")
    
    try:
        # Vérifier si la table alembic_version existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'alembic_version' not in tables:
            print("[WARNING] Table alembic_version manquante")
            print("[INFO] Verification de l'etat de la base de donnees...")
            
            # Vérifier si la table fichiers existe
            if 'fichiers' in tables:
                print("[OK] La table fichiers existe deja")
                
                # Vérifier si la colonne client_id existe déjà
                columns = [col['name'] for col in inspector.get_columns('fichiers')]
                
                if 'client_id' in columns:
                    print("[OK] La colonne client_id existe deja")
                    print("[INFO] Marquage de toutes les migrations comme appliquees...")
                    stamp(revision='002_multi_client', directory=MIGRATIONS_DIR)
                    print("[DONE] Base de donnees deja a jour !")
                else:
                    print("[WARNING] La colonne client_id n'existe pas")
                    print("[INFO] Marquage de la migration 001 comme appliquee...")
                    stamp(revision='001_initial', directory=MIGRATIONS_DIR)
                    print("[INFO] Application de la migration 002 (ajout support multi-client)...")
                    upgrade(directory=MIGRATIONS_DIR)
                    print("[DONE] Migration 002 appliquee avec succes !")
            else:
                print("[INFO] Base de donnees vide, application de toutes les migrations...")
                upgrade(directory=MIGRATIONS_DIR)
                print("[DONE] Toutes les migrations appliquees !")
        else:
            print("[INFO] Table alembic_version trouvee")
            print("[INFO] Application des migrations manquantes...")
            upgrade(directory=MIGRATIONS_DIR)
            print("[DONE] Migrations appliquees avec succes !")
            
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'application des migrations : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n[SUCCESS] Base de donnees mise a jour avec succes !")
print("Vous pouvez maintenant lancer l'application avec : python start_with_postgresql.py")

