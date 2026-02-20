"""Vérifier toutes les contestations PARTNER et leurs enquêtes originales"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from models.client import Client
from extensions import db

app = create_app()

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    contestations = Donnee.query.filter_by(
        client_id=partner.id,
        est_contestation=True
    ).limit(20).all()
    
    print("\n" + "="*80)
    print("VÉRIFICATION DES CONTESTATIONS PARTNER ET LEURS ENQUÊTES ORIGINALES")
    print("="*80)
    
    for c in contestations:
        print(f"\n{'─'*80}")
        print(f"CONTESTATION ID {c.id}")
        print(f"  Nom (champ nom): '{c.nom}'")
        print(f"  Prénom (champ prenom): '{c.prenom}'")
        print(f"  Numéro dossier: {c.numeroDossier}")
        print(f"  enquete_originale_id: {c.enquete_originale_id}")
        
        # Diviser le nom
        nom_parts = c.nom.split() if c.nom else []
        
        if len(nom_parts) >= 2:
            nom_recherche = nom_parts[0]
            prenom_recherche = ' '.join(nom_parts[1:])
            
            print(f"\n  Recherche: nom='{nom_recherche}' ET prenom='{prenom_recherche}'")
            
            # Chercher enquête avec nom ET prenom correspondants
            enqs = Donnee.query.filter(
                Donnee.est_contestation == False,
                Donnee.client_id == partner.id,
                db.and_(
                    Donnee.nom == nom_recherche,
                    Donnee.prenom == prenom_recherche
                )
            ).all()
            
            if enqs:
                print(f"  ✅ {len(enqs)} enquête(s) trouvée(s):")
                for e in enqs:
                    print(f"     → ID {e.id}: {e.nom} {e.prenom} (Dossier: {e.numeroDossier}, Statut: {e.statut_validation})")
            else:
                print(f"  ❌ Aucune enquête originale trouvée")
                
                # Recherche élargie
                enqs_large = Donnee.query.filter(
                    Donnee.est_contestation == False,
                    Donnee.client_id == partner.id,
                    db.or_(
                        Donnee.nom.ilike(f'%{nom_recherche}%'),
                        Donnee.prenom.ilike(f'%{prenom_recherche}%')
                    )
                ).limit(3).all()
                
                if enqs_large:
                    print(f"  💡 Enquêtes similaires:")
                    for e in enqs_large:
                        print(f"     → ID {e.id}: {e.nom} {e.prenom}")
        else:
            print(f"  ⚠️ Nom trop court pour diviser: '{c.nom}'")
    
    # Statistiques
    print(f"\n" + "="*80)
    print("STATISTIQUES")
    print("="*80)
    
    avec_lien = sum(1 for c in contestations if c.enquete_originale_id)
    sans_lien = len(contestations) - avec_lien
    
    print(f"Contestations avec lien direct: {avec_lien}")
    print(f"Contestations sans lien: {sans_lien}")
    print(f"\n⚠️ {sans_lien} contestations nécessitent une recherche dans les archives")
