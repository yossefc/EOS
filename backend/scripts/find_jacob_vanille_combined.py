"""Trouver JACOB VANILLE avec nom+prenom combinés"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Chercher JACOB VANILLE dans le champ nom (nom+prenom combinés)
    donnees = Donnee.query.filter(
        Donnee.nom.ilike('%JACOB%VANILLE%')
    ).all()
    
    if not donnees:
        # Essayer l'inverse
        donnees = Donnee.query.filter(
            Donnee.nom.ilike('%VANILLE%JACOB%')
        ).all()
    
    if donnees:
        print(f"\n✅ Trouvé {len(donnees)} résultat(s) avec nom combiné :\n")
        for d in donnees:
            print(f"ID: {d.id}")
            print(f"  Numéro Dossier: {d.numeroDossier}")
            print(f"  Nom (combiné): '{d.nom}'")
            print(f"  Prénom: '{d.prenom}'")
            print(f"  Type: {d.typeDemande}")
            print(f"  Contestation: {d.est_contestation}")
            if d.est_contestation:
                print(f"  Enquête originale ID: {d.enquete_originale_id}")
                print(f"  Motif: {d.motif_contestation_detail}")
                if d.numeroDossier:
                    print(f"\n  🔗 URL test: http://localhost:5000/api/historique-enquete/{d.numeroDossier}")
            print()
    else:
        print("❌ Aucun résultat trouvé")
        
        # Chercher tous les noms qui contiennent JACOB ou VANILLE
        print("\n🔍 Recherche élargie...\n")
        jacob_results = Donnee.query.filter(
            Donnee.nom.ilike('%JACOB%')
        ).limit(5).all()
        
        vanille_results = Donnee.query.filter(
            Donnee.nom.ilike('%VANILLE%')
        ).limit(5).all()
        
        if jacob_results:
            print("Noms contenant JACOB:")
            for d in jacob_results:
                print(f"  - ID {d.id}: '{d.nom}' (Prénom: '{d.prenom}')")
        
        if vanille_results:
            print("\nNoms contenant VANILLE:")
            for d in vanille_results:
                print(f"  - ID {d.id}: '{d.nom}' (Prénom: '{d.prenom}')")
