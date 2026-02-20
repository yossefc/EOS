"""
Script pour détecter les doublons d'enquêtes dans la base de données
Critères : même client_id + nom + prénom + date de naissance
"""
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from sqlalchemy import func

app = create_app()

with app.app_context():
    print("\n" + "=" * 80)
    print("DÉTECTION DES DOUBLONS D'ENQUÊTES")
    print("=" * 80)
    
    # Chercher les enquêtes avec même nom, prénom, date de naissance et client
    # en regroupant par ces critères et en comptant combien il y en a
    doublons_query = Donnee.query.with_entities(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance,
        func.count(Donnee.id).label('count'),
        func.array_agg(Donnee.id).label('ids')
    ).filter(
        Donnee.est_contestation == False  # Seulement les enquêtes, pas les contestations
    ).group_by(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance
    ).having(
        func.count(Donnee.id) > 1  # Plus d'une enquête avec ces critères
    ).order_by(
        func.count(Donnee.id).desc()
    ).all()
    
    if not doublons_query:
        print("\n✅ Aucun doublon détecté !")
        print("\nTous les enquêtes ont une identité unique (client + nom + prénom + date naissance)")
        sys.exit(0)
    
    print(f"\n⚠️ Trouvé {len(doublons_query)} groupes de doublons")
    print(f"   Total d'enquêtes en doublon : {sum(d.count for d in doublons_query)}")
    print()
    
    total_doublons = 0
    
    for i, doublon in enumerate(doublons_query, 1):
        client_id = doublon.client_id
        nom = doublon.nom
        prenom = doublon.prenom
        date_naissance = doublon.dateNaissance
        count = doublon.count
        ids = doublon.ids
        
        print(f"\n{'─' * 80}")
        print(f"GROUPE #{i} - {count} doublons")
        print(f"{'─' * 80}")
        print(f"Client ID: {client_id}")
        print(f"Nom: {nom}")
        print(f"Prénom: {prenom}")
        print(f"Date naissance: {date_naissance}")
        print(f"\nEnquêtes trouvées (IDs): {ids}")
        
        # Récupérer les détails de chaque enquête du doublon
        enquetes = Donnee.query.filter(Donnee.id.in_(ids)).order_by(Donnee.created_at).all()
        
        print(f"\nDétails des doublons:")
        print(f"{'ID':<8} {'Dossier':<15} {'Fichier':<10} {'Statut':<15} {'Créé le':<20} {'Màj le':<20}")
        print("─" * 100)
        
        for enq in enquetes:
            print(f"{enq.id:<8} "
                  f"{str(enq.numeroDossier)[:14]:<15} "
                  f"{enq.fichier_id:<10} "
                  f"{enq.statut_validation[:14]:<15} "
                  f"{str(enq.created_at)[:19]:<20} "
                  f"{str(enq.updated_at)[:19]:<20}")
        
        # Recommandation
        plus_recent = max(enquetes, key=lambda x: x.updated_at)
        print(f"\n💡 Recommandation : Garder ID {plus_recent.id} (le plus récent)")
        print(f"   À supprimer/archiver : {[e.id for e in enquetes if e.id != plus_recent.id]}")
        
        total_doublons += count - 1  # -1 car on garde un exemplaire
    
    # Statistiques finales
    print("\n" + "=" * 80)
    print("STATISTIQUES")
    print("=" * 80)
    print(f"Groupes de doublons trouvés : {len(doublons_query)}")
    print(f"Enquêtes en doublon (à nettoyer) : {total_doublons}")
    print(f"Enquêtes à conserver : {len(doublons_query)}")
    
    # Vérifier si les doublons viennent du même fichier
    print("\n" + "=" * 80)
    print("ANALYSE DES SOURCES")
    print("=" * 80)
    
    meme_fichier = 0
    fichiers_differents = 0
    
    for doublon in doublons_query:
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).all()
        fichiers = set([e.fichier_id for e in enquetes])
        
        if len(fichiers) == 1:
            meme_fichier += 1
        else:
            fichiers_differents += 1
    
    print(f"Doublons du même fichier : {meme_fichier}")
    print(f"Doublons de fichiers différents : {fichiers_differents}")
    
    if meme_fichier > 0:
        print("\n⚠️ ATTENTION : Certains doublons proviennent du même fichier !")
        print("   → Cela indique un problème dans le processus d'import")
    
    # Générer un script de nettoyage
    print("\n" + "=" * 80)
    print("SCRIPT SQL DE NETTOYAGE (à exécuter avec précaution)")
    print("=" * 80)
    print("\n-- Commandes pour supprimer les doublons (garder le plus récent)")
    print("-- ATTENTION : Vérifiez avant d'exécuter !\n")
    
    for i, doublon in enumerate(doublons_query[:5], 1):  # Limiter à 5 exemples
        enquetes = Donnee.query.filter(Donnee.id.in_(doublon.ids)).order_by(Donnee.updated_at).all()
        plus_recent = enquetes[-1]
        a_supprimer = [e.id for e in enquetes[:-1]]
        
        print(f"-- Groupe #{i}: {doublon.nom} {doublon.prenom}")
        print(f"-- Garder: ID {plus_recent.id}")
        print(f"DELETE FROM donnees WHERE id IN ({', '.join(map(str, a_supprimer))});")
        print()
    
    if len(doublons_query) > 5:
        print(f"... et {len(doublons_query) - 5} autres groupes")
