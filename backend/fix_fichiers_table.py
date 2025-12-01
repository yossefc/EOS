"""
Script pour corriger la table fichiers en ajoutant la colonne 'chemin' si elle n'existe pas
"""
from app import create_app
from extensions import db
from sqlalchemy import inspect, text
import sys

def check_and_add_chemin_column():
    """Vérifie et ajoute la colonne chemin si nécessaire"""
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Vérifier si la table fichiers existe
        if 'fichiers' not in inspector.get_table_names():
            print("❌ La table 'fichiers' n'existe pas")
            return False
        
        # Récupérer les colonnes de la table fichiers
        columns = [col['name'] for col in inspector.get_columns('fichiers')]
        print(f"Colonnes actuelles de la table 'fichiers': {columns}")
        
        # Vérifier si la colonne chemin existe
        if 'chemin' not in columns:
            print("⚠️  La colonne 'chemin' n'existe pas. Ajout en cours...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE fichiers ADD COLUMN chemin VARCHAR(500)"))
                    conn.commit()
                print("✅ Colonne 'chemin' ajoutée avec succès")
                return True
            except Exception as e:
                print(f"❌ Erreur lors de l'ajout de la colonne: {e}")
                return False
        else:
            print("✅ La colonne 'chemin' existe déjà")
            return True

if __name__ == '__main__':
    print("=== Vérification et correction de la table fichiers ===\n")
    success = check_and_add_chemin_column()
    
    if success:
        print("\n✅ La table fichiers est correctement configurée")
        sys.exit(0)
    else:
        print("\n❌ Des erreurs sont survenues")
        sys.exit(1)

