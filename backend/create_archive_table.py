"""
Script pour créer la table d'archivage des enquêtes exportées
"""
from app import create_app
from extensions import db
from models.enquete_archive import EnqueteArchive

app = create_app()

with app.app_context():
    # Créer la table
    db.create_all()
    print("✅ Table 'enquete_archives' créée avec succès!")
    
    # Vérifier que la table existe
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'enquete_archives' in tables:
        print(f"✅ Vérification : La table 'enquete_archives' existe bien")
        
        # Afficher les colonnes
        columns = inspector.get_columns('enquete_archives')
        print("\nColonnes de la table :")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
    else:
        print("❌ Erreur : La table n'a pas été créée")


