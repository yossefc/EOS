"""Tester toutes les contestations PARTNER avec l'API"""
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from models.client import Client

app = create_app()

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    contestations = Donnee.query.filter_by(
        client_id=partner.id,
        est_contestation=True
    ).limit(15).all()
    
    print("\n" + "="*80)
    print("TEST DE L'API POUR TOUTES LES CONTESTATIONS PARTNER")
    print("="*80)
    
    succes = 0
    avec_enquete = 0
    sans_enquete = 0
    erreurs = 0
    
    for c in contestations:
        if not c.numeroDossier:
            print(f"\n⚠️ ID {c.id} ({c.nom}): Pas de numeroDossier, skip")
            continue
        
        try:
            # Appeler l'API
            url = f"http://localhost:5000/api/historique-enquete/{c.numeroDossier}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            if data.get('success'):
                succes += 1
                has_original = data.get('data', {}).get('enquete_originale') is not None
                
                if has_original:
                    avec_enquete += 1
                    orig = data['data']['enquete_originale']
                    print(f"\n✅ ID {c.id} - {c.nom}")
                    print(f"   → Enquête trouvée: {orig.get('nom')} {orig.get('prenom')} (ID {orig.get('id')})")
                else:
                    sans_enquete += 1
                    print(f"\n⚠️ ID {c.id} - {c.nom}")
                    print(f"   → Aucune enquête originale trouvée")
            else:
                erreurs += 1
                print(f"\n❌ ID {c.id} - {c.nom}")
                print(f"   → Erreur: {data.get('error')}")
                
        except Exception as e:
            erreurs += 1
            print(f"\n❌ ID {c.id} - {c.nom}")
            print(f"   → Exception: {str(e)[:50]}")
    
    # Rapport
    print(f"\n" + "="*80)
    print("RAPPORT FINAL")
    print("="*80)
    print(f"✅ Succès: {succes}")
    print(f"   Avec enquête originale: {avec_enquete}")
    print(f"   Sans enquête originale: {sans_enquete}")
    print(f"❌ Erreurs: {erreurs}")
    print()
    
    if avec_enquete > 0:
        print(f"🎉 {avec_enquete} contestations afficheront leur historique complet !")
    
    if sans_enquete > 0:
        print(f"⚠️ {sans_enquete} contestations n'ont pas d'enquête originale dans les archives")
