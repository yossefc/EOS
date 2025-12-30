"""
Script de diagnostic pour vérifier l'état de la base de données PostgreSQL
"""
import os

# Définir DATABASE_URL AVANT tout import
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from sqlalchemy import inspect

# Créer l'application
app = create_app()

# Vérifier l'état de la base de données
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n" + "="*70)
    print("📊 ÉTAT DE LA BASE DE DONNÉES PostgreSQL")
    print("="*70)
    
    print(f"\n📋 Tables existantes ({len(tables)}) :")
    for table in sorted(tables):
        print(f"   - {table}")
    
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION DES COLONNES IMPORTANTES")
    print("="*70)
    
    # Vérifier les colonnes de fichiers
    if 'fichiers' in tables:
        print("\n📁 Table 'fichiers' :")
        columns = [col['name'] for col in inspector.get_columns('fichiers')]
        print(f"   Colonnes : {', '.join(columns)}")
        if 'client_id' in columns:
            print("   ✅ client_id existe")
        else:
            print("   ❌ client_id MANQUANT")
    
    # Vérifier les colonnes de donnees
    if 'donnees' in tables:
        print("\n📝 Table 'donnees' :")
        columns = [col['name'] for col in inspector.get_columns('donnees')]
        if 'client_id' in columns:
            print("   ✅ client_id existe")
        else:
            print("   ❌ client_id MANQUANT")
    
    # Vérifier les colonnes de clients
    if 'clients' in tables:
        print("\n👥 Table 'clients' :")
        columns = [col['name'] for col in inspector.get_columns('clients')]
        print(f"   Colonnes : {', '.join(columns)}")
        
        # Compter les clients
        result = db.session.execute(db.text("SELECT COUNT(*) FROM clients"))
        count = result.scalar()
        print(f"   Nombre de clients : {count}")
    
    # Vérifier la table alembic_version
    if 'alembic_version' in tables:
        print("\n🏷️  Table 'alembic_version' :")
        result = db.session.execute(db.text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        print(f"   Version actuelle : {version}")
    else:
        print("\n❌ Table 'alembic_version' n'existe pas")
        print("   → Alembic ne suit pas les migrations")
    
    print("\n" + "="*70)
    print("💡 RECOMMANDATIONS")
    print("="*70)
    
    # Recommandations basées sur l'état
    if 'alembic_version' not in tables:
        if 'clients' in tables and 'fichiers' in tables:
            fichiers_cols = [col['name'] for col in inspector.get_columns('fichiers')]
            if 'client_id' in fichiers_cols:
                print("\n✅ La base de données semble à jour mais Alembic ne le sait pas.")
                print("   → Exécuter: flask db stamp 002_multi_client")
            else:
                print("\n⚠️  La base a été créée avec db.create_all() mais sans client_id")
                print("   → Il faut appliquer manuellement la migration SQL")
        else:
            print("\n✅ Base de données neuve")
            print("   → Exécuter: flask db upgrade")
    
    print("\n" + "="*70 + "\n")





