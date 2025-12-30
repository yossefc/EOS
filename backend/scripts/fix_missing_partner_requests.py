"""
Script de rattrapage pour créer les PartnerCaseRequest manquants
Pour les dossiers PARTNER déjà importés
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models.models import Donnee
from models.client import Client
from models.partner_models import PartnerCaseRequest
from services.partner_request_parser import PartnerRequestParser

def fix_missing_requests():
    """Crée les PartnerCaseRequest manquants pour les dossiers existants"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("SCRIPT DE RATTRAPAGE - PARTNER CASE REQUESTS")
        print("=" * 60)
        
        # 1. Trouver le client PARTNER
        client = Client.query.filter_by(code='PARTNER').first()
        if not client:
            print("❌ Client PARTNER introuvable !")
            return
        
        print(f"\n✅ Client PARTNER trouvé (ID: {client.id})")
        
        # 2. Récupérer tous les dossiers PARTNER avec RECHERCHE
        donnees = Donnee.query.filter_by(
            client_id=client.id
        ).filter(
            Donnee.recherche.isnot(None),
            Donnee.recherche != ''
        ).all()
        
        print(f"✅ {len(donnees)} dossiers PARTNER avec RECHERCHE trouvés")
        
        if len(donnees) == 0:
            print("\n⚠️  Aucun dossier à traiter")
            return
        
        # 3. Traiter chaque dossier
        created_count = 0
        skipped_count = 0
        
        print("\n" + "=" * 60)
        print("TRAITEMENT EN COURS...")
        print("=" * 60)
        
        for i, donnee in enumerate(donnees, 1):
            # Vérifier si les demandes existent déjà
            existing_requests = PartnerCaseRequest.query.filter_by(
                donnee_id=donnee.id
            ).count()
            
            if existing_requests > 0:
                skipped_count += 1
                continue
            
            # Parser le champ RECHERCHE
            detected_requests = PartnerRequestParser.parse_recherche(
                donnee.recherche, 
                client.id
            )
            
            if not detected_requests:
                continue
            
            # Créer les PartnerCaseRequest
            for request_code in detected_requests:
                new_request = PartnerCaseRequest(
                    donnee_id=donnee.id,
                    request_code=request_code,
                    requested=True,
                    found=False,  # Sera calculé par le calculateur
                    status='NEG'  # Sera calculé par le calculateur
                )
                db.session.add(new_request)
                created_count += 1
            
            # Afficher progression tous les 10 dossiers
            if i % 10 == 0:
                print(f"  Progression : {i}/{len(donnees)} dossiers traités...")
        
        # 4. Commit
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("✅ TRAITEMENT TERMINÉ")
            print("=" * 60)
            print(f"  • {created_count} demandes créées")
            print(f"  • {skipped_count} dossiers ignorés (déjà traités)")
            print(f"  • {len(donnees)} dossiers au total")
            print("\n⚠️  IMPORTANT : Les statuts POS/NEG seront calculés")
            print("   automatiquement lors de la mise à jour ou de l'export")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERREUR lors du commit : {e}")
            raise

if __name__ == '__main__':
    fix_missing_requests()



