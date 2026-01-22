import sys
import os

# Configuration
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from extensions import db
from models import Client, SherlockDonnee, Fichier

def verify_cascade_deletion():
    app = create_app()
    with app.app_context():
        print("🔍 Vérification de la suppression en cascade...")
        
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        if not client:
            print("❌ Client RG_SHERLOCK introuvable")
            return

        # 1. Créer un Fichier dummy
        fichier = Fichier(nom="test_deletion.xlsx", client_id=client.id)
        db.session.add(fichier)
        db.session.commit()
        print(f"  → Fichier créé (ID: {fichier.id})")
        
        # 2. Créer une SherlockDonnee liée
        donnee = SherlockDonnee(
            fichier_id=fichier.id,
            dossier_id="TEST-DEL-001",
            ec_nom_usage="TO_BE_DELETED"
        )
        db.session.add(donnee)
        db.session.commit()
        print(f"  → SherlockDonnee créée (ID: {donnee.id})")
        
        # 3. Supprimer le fichier (doit cascade)
        try:
            print("  → Tentative de suppression du fichier...")
            db.session.delete(fichier)
            db.session.commit()
            print("✅ Suppression réussie (pas d'erreur FK)")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return
            
        # 4. Vérifier que la donnée est bien supprimée
        deleted_donnee = db.session.get(SherlockDonnee, donnee.id)
        if deleted_donnee is None:
            print("✅ SherlockDonnee bien supprimée automatiquement.")
        else:
            print("❌ ERREUR: SherlockDonnee existe toujours !")

if __name__ == "__main__":
    verify_cascade_deletion()
