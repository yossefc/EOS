"""
Script pour appliquer les migrations Alembic à la base de données PostgreSQL
Ce script garantit que DATABASE_URL est défini avant d'exécuter les migrations
"""
import os
import sys

# Définir DATABASE_URL AVANT tout import
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

print("✓ DATABASE_URL définie")
print(f"  {os.environ['DATABASE_URL'][:50]}...")
print()

# Importer l'application Flask
from app import create_app
from flask_migrate import stamp, upgrade, current
from extensions import db

# Créer l'application
app = create_app()

# Appliquer les migrations dans le contexte de l'application
with app.app_context():
    print("📦 Vérification de l'état des migrations...")
    
    try:
        # Vérifier si la table alembic_version existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'alembic_version' not in tables:
            print("⚠️  Table alembic_version manquante")
            print("📝 Vérification de l'état de la base de données...")
            
            # Vérifier si la table fichiers existe
            if 'fichiers' in tables:
                print("✓ La table fichiers existe déjà")
                
                # Vérifier si la colonne client_id existe déjà
                columns = [col['name'] for col in inspector.get_columns('fichiers')]
                
                if 'client_id' in columns:
                    print("✓ La colonne client_id existe déjà")
                    print("📝 Marquage de toutes les migrations comme appliquées...")
                    stamp(revision='002_multi_client', directory='migrations')
                    print("✅ Base de données déjà à jour !")
                else:
                    print("⚠️  La colonne client_id n'existe pas")
                    print("📝 Marquage de la migration 001 comme appliquée...")
                    stamp(revision='001_initial', directory='migrations')
                    print("📦 Application de la migration 002 (ajout support multi-client)...")
                    upgrade(directory='migrations')
                    print("✅ Migration 002 appliquée avec succès !")
            else:
                print("ℹ️  Base de données vide, application de toutes les migrations...")
                upgrade(directory='migrations')
                print("✅ Toutes les migrations appliquées !")
        else:
            print("ℹ️  Table alembic_version trouvée")
            print("📦 Application des migrations manquantes...")
            upgrade(directory='migrations')
            print("✅ Migrations appliquées avec succès !")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'application des migrations : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n🎉 Base de données mise à jour avec succès !")
print("Vous pouvez maintenant lancer l'application avec : python start_with_postgresql.py")

