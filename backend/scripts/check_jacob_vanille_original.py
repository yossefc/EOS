"""Vérifier l'enquête originale de la contestation JACOB VANILLE"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee

app = create_app()

with app.app_context():
    # Chercher la contestation JACOB VANILLE avec enquête originale
    contestation = Donnee.query.get(39330)
    
    if contestation:
        print("=" * 60)
        print("CONTESTATION ID 39330 - JACOB VANILLE")
        print("=" * 60)
        print(f"numeroDossier: {contestation.numeroDossier}")
        print(f"Nom: {contestation.nom}")
        print(f"Prenom: {contestation.prenom}")
        print(f"Type: {contestation.typeDemande}")
        print(f"enquete_originale_id: {contestation.enquete_originale_id}")
        print(f"est_contestation: {contestation.est_contestation}")
        print(f"date_contestation: {contestation.date_contestation}")
        print(f"motif: {contestation.motif_contestation_detail}")
        print(f"numeroDemandeContestee: {contestation.numeroDemandeContestee}")
        
        if contestation.enquete_originale_id:
            print("\n" + "=" * 60)
            print(f"ENQUÊTE ORIGINALE ID {contestation.enquete_originale_id}")
            print("=" * 60)
            orig = Donnee.query.get(contestation.enquete_originale_id)
            if orig:
                print(f"numeroDossier: {orig.numeroDossier}")
                print(f"Nom: {orig.nom}")
                print(f"Prenom: {orig.prenom}")
                print(f"Type: {orig.typeDemande}")
                print(f"est_contestation: {orig.est_contestation}")
                print(f"statut_validation: {orig.statut_validation}")
                
                # Vérifier l'historique
                historique = orig.get_history()
                if historique:
                    print(f"\nHistorique de l'enquete originale ({len(historique)} evenements):")
                    for h in historique:
                        print(f"  - {h.get('date')}: {h.get('type')} - {h.get('details')}")
        else:
            print("\n⚠️ PROBLEME: La contestation n'a pas d'enquete_originale_id!")
            print(f"numeroDemandeContestee: {contestation.numeroDemandeContestee}")
            
            # Chercher l'enquête originale par numéro
            if contestation.numeroDemandeContestee:
                print(f"\nRecherche de l'enquete avec numeroDossier = '{contestation.numeroDemandeContestee}'...")
                orig = Donnee.query.filter_by(numeroDossier=contestation.numeroDemandeContestee).first()
                if orig:
                    print(f"✅ Trouvee! ID: {orig.id}")
                    print(f"   Nom: {orig.nom} {orig.prenom}")
                else:
                    print("❌ Pas trouvee")
