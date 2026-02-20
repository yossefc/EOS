"""Chercher des enquêtes archivées qui correspondent à JACOB VANILLE"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Rechercher les enquêtes archivées
    nom_recherche = "JACOB"  # ou "VANILLE"
    
    print(f"\n{'='*60}")
    print(f"RECHERCHE D'ENQUÊTES ARCHIVÉES pour: {nom_recherche}")
    print(f"{'='*60}\n")
    
    # Chercher dans toutes les enquêtes (pas seulement archivées) contenant JACOB ou VANILLE
    enquetes = Donnee.query.filter(
        Donnee.est_contestation == False,
        Donnee.nom.ilike(f"%{nom_recherche}%") |
        Donnee.prenom.ilike(f"%{nom_recherche}%")
    ).limit(10).all()
    
    print(f"Trouvé {len(enquetes)} enquêtes avec '{nom_recherche}':\n")
    
    for e in enquetes:
        print(f"ID: {e.id}")
        print(f"  Nom: {e.nom}")
        print(f"  Prénom: {e.prenom}")
        print(f"  Numéro Dossier: {e.numeroDossier}")
        print(f"  Type: {e.typeDemande}")
        print(f"  Statut: {e.statut_validation}")
        print(f"  Enquêteur ID: {e.enqueteurId}")
        print()
    
    # Vérifier aussi avec VANILLE
    print(f"\n{'-'*60}\n")
    enquetes2 = Donnee.query.filter(
        Donnee.est_contestation == False,
        Donnee.nom.ilike("%VANILLE%") |
        Donnee.prenom.ilike("%VANILLE%")
    ).limit(10).all()
    
    print(f"Trouvé {len(enquetes2)} enquêtes avec 'VANILLE':\n")
    
    for e in enquetes2:
        print(f"ID: {e.id} - {e.nom} {e.prenom} - Dossier: {e.numeroDossier} - Statut: {e.statut_validation}")
