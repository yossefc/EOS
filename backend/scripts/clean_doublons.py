"""
Script pour supprimer les doublons d'enquêtes et de contestations
ATTENTION : Sépare les enquêtes des contestations
Un doublon = soit toutes des enquêtes, soit toutes des contestations
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from sqlalchemy import func

app = create_app()

def detect_et_nettoyer_doublons(est_contestation_value, type_nom):
    """
    Détecte et nettoie les doublons pour un type (enquête ou contestation)
    
    Args:
        est_contestation_value: True pour contestations, False pour enquêtes
        type_nom: "contestations" ou "enquêtes" pour l'affichage
    """
    print(f"\n{'='*80}")
    print(f"TRAITEMENT DES DOUBLONS DE {type_nom.upper()}")
    print(f"{'='*80}")
    
    # Détecter les doublons
    doublons_query = db.session.query(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance,
        func.count(Donnee.id).label('count'),
        func.array_agg(Donnee.id).label('ids')
    ).filter(
        Donnee.est_contestation == est_contestation_value
    ).group_by(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance
    ).having(
        func.count(Donnee.id) > 1
    ).all()
    
    if not doublons_query:
        print(f"\n✅ Aucun doublon de {type_nom} détecté !")
        return 0, 0
    
    nb_groupes = len(doublons_query)
    total_a_supprimer = sum(d.count - 1 for d in doublons_query)
    
    print(f"\n⚠️ Trouvé {nb_groupes} groupes de doublons de {type_nom}")
    print(f"   Total à supprimer : {total_a_supprimer} {type_nom}")
    
    # Afficher les 5 premiers exemples
    print(f"\n📋 Exemples de doublons à nettoyer (5 premiers) :")
    for i, doublon in enumerate(doublons_query[:5], 1):
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).order_by(Donnee.updated_at.desc()).all()
        plus_recent = enquetes[0]
        a_supprimer = [e.id for e in enquetes[1:]]
        
        print(f"\n   {i}. {doublon.nom} {doublon.prenom} ({doublon.count} doublons)")
        print(f"      Garder  : ID {plus_recent.id} (màj: {plus_recent.updated_at})")
        print(f"      Supprimer : IDs {a_supprimer}")
    
    if nb_groupes > 5:
        print(f"\n   ... et {nb_groupes - 5} autres groupes")
    
    # Demander confirmation
    print(f"\n{'─'*80}")
    reponse = input(f"\nVoulez-vous supprimer ces {total_a_supprimer} {type_nom} en doublon ? (o/n): ")
    
    if reponse.lower() != 'o':
        print(f"❌ Nettoyage des {type_nom} annulé")
        return 0, 0
    
    # Supprimer les doublons
    print(f"\n{'='*80}")
    print(f"SUPPRESSION EN COURS...")
    print(f"{'='*80}\n")
    
    nb_supprimes = 0
    rapport = []
    
    for doublon in doublons_query:
        # Récupérer toutes les enquêtes du groupe, triées par date (plus récent en premier)
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).order_by(Donnee.updated_at.desc()).all()
        
        plus_recent = enquetes[0]
        a_supprimer = enquetes[1:]
        
        # Supprimer les doublons
        for enq in a_supprimer:
            rapport.append({
                'id': enq.id,
                'nom': enq.nom,
                'prenom': enq.prenom,
                'numeroDossier': enq.numeroDossier,
                'fichier_id': enq.fichier_id,
                'created_at': enq.created_at,
                'garde_id': plus_recent.id
            })
            
            db.session.delete(enq)
            nb_supprimes += 1
        
        if nb_supprimes % 100 == 0 and nb_supprimes > 0:
            print(f"   Progression : {nb_supprimes}/{total_a_supprimer} supprimés...")
    
    # Commit
    try:
        db.session.commit()
        print(f"\n✅ {nb_supprimes} {type_nom} supprimées avec succès !")
        print(f"   {nb_groupes} groupes nettoyés")
        
        # Générer le rapport
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rapport_file = f"rapport_nettoyage_{type_nom}_{timestamp}.txt"
        
        with open(rapport_file, 'w', encoding='utf-8') as f:
            f.write(f"RAPPORT DE NETTOYAGE DES DOUBLONS DE {type_nom.upper()}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Nombre de suppressions: {nb_supprimes}\n")
            f.write(f"Nombre de groupes: {nb_groupes}\n\n")
            f.write("=" * 80 + "\n")
            f.write("DÉTAIL DES SUPPRESSIONS\n")
            f.write("=" * 80 + "\n\n")
            
            for item in rapport:
                f.write(f"ID supprimé : {item['id']}\n")
                f.write(f"  Nom: {item['nom']} {item['prenom']}\n")
                f.write(f"  Numéro dossier: {item['numeroDossier']}\n")
                f.write(f"  Fichier ID: {item['fichier_id']}\n")
                f.write(f"  Créé le: {item['created_at']}\n")
                f.write(f"  → Gardé ID: {item['garde_id']}\n\n")
        
        print(f"\n📄 Rapport généré : {rapport_file}")
        
        return nb_groupes, nb_supprimes
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Erreur lors de la suppression : {e}")
        return 0, 0


with app.app_context():
    print("\n" + "=" * 80)
    print("NETTOYAGE DES DOUBLONS")
    print("Séparation : Enquêtes ET Contestations")
    print("=" * 80)
    
    # 1. Nettoyer les doublons d'ENQUÊTES
    groupes_enq, suppr_enq = detect_et_nettoyer_doublons(False, "enquêtes")
    
    # 2. Nettoyer les doublons de CONTESTATIONS
    groupes_cont, suppr_cont = detect_et_nettoyer_doublons(True, "contestations")
    
    # Rapport final
    print("\n" + "=" * 80)
    print("RAPPORT FINAL")
    print("=" * 80)
    print(f"\n✅ Enquêtes :")
    print(f"   Groupes nettoyés : {groupes_enq}")
    print(f"   Doublons supprimés : {suppr_enq}")
    
    print(f"\n✅ Contestations :")
    print(f"   Groupes nettoyés : {groupes_cont}")
    print(f"   Doublons supprimés : {suppr_cont}")
    
    print(f"\n📊 TOTAL :")
    print(f"   Groupes nettoyés : {groupes_enq + groupes_cont}")
    print(f"   Doublons supprimés : {suppr_enq + suppr_cont}")
    print()
