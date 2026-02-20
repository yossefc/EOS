"""Script pour trouver JACOB VANILLE dans la base"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Chercher JACOB VANILLE
    donnees = Donnee.query.filter(
        Donnee.nom.ilike('%JACOB%'), 
        Donnee.prenom.ilike('%VANILLE%')
    ).all()
    
    if not donnees:
        # Essayer dans l'autre sens
        donnees = Donnee.query.filter(
            Donnee.nom.ilike('%VANILLE%'), 
            Donnee.prenom.ilike('%JACOB%')
        ).all()
    
    if donnees:
        print(f"\n✅ Trouvé {len(donnees)} résultat(s) :\n")
        for d in donnees:
            print(f"ID: {d.id}")
            print(f"  Numéro Dossier: {d.numeroDossier}")
            print(f"  Nom: {d.nom}")
            print(f"  Prénom: {d.prenom}")
            print(f"  Type: {d.typeDemande}")
            print(f"  Contestation: {d.est_contestation}")
            if d.est_contestation and d.enquete_originale_id:
                print(f"  Enquête originale ID: {d.enquete_originale_id}")
            print()
    else:
        print("❌ Aucun résultat trouvé pour JACOB VANILLE")
