"""Tester FORGET YOANN"""
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
    
    print("\n" + "="*80)
    print("RECHERCHE FORGET YOANN")
    print("="*80)
    
    # Chercher la contestation
    contestation = Donnee.query.filter(
        Donnee.client_id == partner.id,
        Donnee.est_contestation == True,
        db.or_(
            Donnee.nom.ilike('%FORGET%YOANN%'),
            db.and_(
                Donnee.nom.ilike('%FORGET%'),
                Donnee.prenom.ilike('%YOANN%')
            )
        )
    ).first()
    
    if contestation:
        print(f"\n✅ CONTESTATION TROUVÉE:")
        print(f"   ID: {contestation.id}")
        print(f"   Nom: '{contestation.nom}'")
        print(f"   Prénom: '{contestation.prenom}'")
        print(f"   Numéro dossier: {contestation.numeroDossier}")
        print(f"   enquete_originale_id: {contestation.enquete_originale_id}")
        
        # Diviser le nom
        if contestation.nom:
            parts = contestation.nom.split()
            if len(parts) >= 2:
                nom_part = parts[0]
                prenom_part = ' '.join(parts[1:])
                
                print(f"\n🔍 RECHERCHE ENQUÊTE ORIGINALE:")
                print(f"   nom = '{nom_part}'")
                print(f"   prenom = '{prenom_part}'")
                
                # Chercher l'enquête avec nom exact ET prenom exact
                enquetes = Donnee.query.filter(
                    Donnee.est_contestation == False,
                    Donnee.client_id == partner.id,
                    Donnee.nom == nom_part,
                    Donnee.prenom == prenom_part
                ).all()
                
                if enquetes:
                    print(f"\n   ✅ {len(enquetes)} enquête(s) trouvée(s):")
                    for e in enquetes:
                        print(f"      → ID {e.id}")
                        print(f"        Nom: {e.nom}")
                        print(f"        Prénom: {e.prenom}")
                        print(f"        Numéro dossier: {e.numeroDossier}")
                        print(f"        Statut: {e.statut_validation}")
                        print(f"        Créé: {e.created_at}")
                        print()
                else:
                    print(f"\n   ❌ Aucune enquête exacte trouvée")
                    
                    # Recherche ILIKE
                    print(f"\n   🔍 Recherche avec ILIKE...")
                    enquetes_like = Donnee.query.filter(
                        Donnee.est_contestation == False,
                        Donnee.client_id == partner.id,
                        Donnee.nom.ilike(f'%{nom_part}%'),
                        Donnee.prenom.ilike(f'%{prenom_part}%')
                    ).all()
                    
                    if enquetes_like:
                        print(f"   ✅ {len(enquetes_like)} enquête(s) similaire(s):")
                        for e in enquetes_like:
                            print(f"      → ID {e.id}: {e.nom} {e.prenom} (Statut: {e.statut_validation})")
                    else:
                        print(f"   ❌ Aucune enquête similaire")
            else:
                # Nom simple, utiliser le prenom du champ prenom
                print(f"\n🔍 RECHERCHE ENQUÊTE ORIGINALE (nom simple):")
                print(f"   nom = '{contestation.nom}'")
                print(f"   prenom = '{contestation.prenom}'")
                
                enquetes = Donnee.query.filter(
                    Donnee.est_contestation == False,
                    Donnee.client_id == partner.id,
                    Donnee.nom == contestation.nom,
                    Donnee.prenom == contestation.prenom
                ).all()
                
                if enquetes:
                    print(f"\n   ✅ {len(enquetes)} enquête(s) trouvée(s):")
                    for e in enquetes:
                        print(f"      → ID {e.id}: {e.nom} {e.prenom} (Dossier: {e.numeroDossier})")
                else:
                    print(f"\n   ❌ Aucune enquête trouvée")
    else:
        print("\n❌ Aucune contestation FORGET YOANN trouvée")
        
        # Chercher toutes les contestations avec FORGET ou YOANN
        print("\n🔍 Recherche élargie...")
        contestations_all = Donnee.query.filter(
            Donnee.client_id == partner.id,
            Donnee.est_contestation == True,
            db.or_(
                Donnee.nom.ilike('%FORGET%'),
                Donnee.nom.ilike('%YOANN%')
            )
        ).limit(10).all()
        
        if contestations_all:
            print(f"\nContestations trouvées avec FORGET ou YOANN:")
            for c in contestations_all:
                print(f"  - ID {c.id}: '{c.nom}' '{c.prenom}'")
