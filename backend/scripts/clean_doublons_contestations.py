"""
Script pour supprimer UNIQUEMENT les doublons de contestations
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from sqlalchemy import func

app = create_app()

with app.app_context():
    print("\n" + "=" * 80)
    print("NETTOYAGE DES DOUBLONS DE CONTESTATIONS")
    print("=" * 80)
    
    # Détecter les doublons de contestations
    doublons_query = db.session.query(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance,
        func.count(Donnee.id).label('count'),
        func.array_agg(Donnee.id).label('ids')
    ).filter(
        Donnee.est_contestation == True
    ).group_by(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance
    ).having(
        func.count(Donnee.id) > 1
    ).all()
    
    if not doublons_query:
        print("\n✅ Aucun doublon de contestations !")
        sys.exit(0)
    
    nb_groupes = len(doublons_query)
    total_a_supprimer = sum(d.count - 1 for d in doublons_query)
    
    print(f"\n⚠️ Trouvé {nb_groupes} groupes de doublons")
    print(f"   Total à supprimer : {total_a_supprimer} contestations")
    
    # Afficher les exemples
    print(f"\n📋 Liste complète :")
    for i, doublon in enumerate(doublons_query, 1):
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).order_by(Donnee.updated_at.desc()).all()
        plus_recent = enquetes[0]
        a_supprimer = [e.id for e in enquetes[1:]]
        
        print(f"\n   {i}. {doublon.nom} {doublon.prenom} ({doublon.count} doublons)")
        print(f"      Garder  : ID {plus_recent.id}")
        print(f"      Supprimer : IDs {a_supprimer}")
    
    # Suppression automatique
    print(f"\n{'='*80}")
    print(f"SUPPRESSION EN COURS...")
    print(f"{'='*80}\n")
    
    nb_supprimes = 0
    rapport = []
    
    for doublon in doublons_query:
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).order_by(Donnee.updated_at.desc()).all()
        
        plus_recent = enquetes[0]
        a_supprimer = enquetes[1:]
        
        for enq in a_supprimer:
            rapport.append({
                'id': enq.id,
                'nom': enq.nom,
                'prenom': enq.prenom,
                'numeroDossier': enq.numeroDossier,
                'garde_id': plus_recent.id
            })
            
            # Supprimer d'abord les dépendances
            DonneeEnqueteur.query.filter_by(donnee_id=enq.id).delete()
            
            # Puis supprimer l'enquête
            db.session.delete(enq)
            nb_supprimes += 1
    
    # Commit
    try:
        db.session.commit()
        print(f"\n✅ {nb_supprimes} contestations supprimées avec succès !")
        
        # Rapport
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rapport_file = f"rapport_nettoyage_contestations_{timestamp}.txt"
        
        with open(rapport_file, 'w', encoding='utf-8') as f:
            f.write(f"RAPPORT DE NETTOYAGE DES DOUBLONS DE CONTESTATIONS\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Suppressions: {nb_supprimes}\n\n")
            
            for item in rapport:
                f.write(f"ID supprimé : {item['id']} - {item['nom']} {item['prenom']}\n")
                f.write(f"  → Gardé ID: {item['garde_id']}\n\n")
        
        print(f"📄 Rapport : {rapport_file}\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Erreur : {e}")
