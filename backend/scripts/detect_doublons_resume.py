"""
Script pour avoir un résumé des doublons sans détails
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from models.client import Client
from sqlalchemy import func
from collections import Counter

app = create_app()

with app.app_context():
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES DOUBLONS")
    print("=" * 80)
    
    # Statistiques globales
    doublons_query = Donnee.query.with_entities(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance,
        func.count(Donnee.id).label('count'),
        func.array_agg(Donnee.id).label('ids'),
        func.array_agg(Donnee.fichier_id).label('fichiers')
    ).filter(
        Donnee.est_contestation == False
    ).group_by(
        Donnee.client_id,
        Donnee.nom,
        Donnee.prenom,
        Donnee.dateNaissance
    ).having(
        func.count(Donnee.id) > 1
    ).all()
    
    if not doublons_query:
        print("\n✅ Aucun doublon !")
        sys.exit(0)
    
    print(f"\n📊 STATISTIQUES GÉNÉRALES")
    print(f"   Groupes de doublons : {len(doublons_query)}")
    print(f"   Total enquêtes en doublon : {sum(d.count for d in doublons_query)}")
    print(f"   Enquêtes à supprimer : {sum(d.count - 1 for d in doublons_query)}")
    
    # Par client
    print(f"\n👥 PAR CLIENT")
    clients_count = Counter()
    for d in doublons_query:
        clients_count[d.client_id] += 1
    
    for client_id, count in clients_count.most_common():
        client = Client.query.get(client_id)
        nom_client = client.nom if client else f"Client ID {client_id}"
        print(f"   {nom_client:<30} : {count:>4} groupes")
    
    # Par taille de doublon
    print(f"\n📈 TAILLE DES GROUPES DE DOUBLONS")
    tailles = Counter([d.count for d in doublons_query])
    for taille in sorted(tailles.keys(), reverse=True)[:10]:
        print(f"   {taille} doublons  : {tailles[taille]:>4} groupes")
    
    # Même fichier vs fichiers différents
    print(f"\n📁 SOURCE DES DOUBLONS")
    meme_fichier = 0
    fichiers_diff = 0
    
    for d in doublons_query:
        fichiers_uniques = set(d.fichiers)
        if len(fichiers_uniques) == 1:
            meme_fichier += 1
        else:
            fichiers_diff += 1
    
    print(f"   Même fichier      : {meme_fichier:>4} groupes ({meme_fichier*100//len(doublons_query)}%)")
    print(f"   Fichiers différents : {fichiers_diff:>4} groupes ({fichiers_diff*100//len(doublons_query)}%)")
    
    if meme_fichier > len(doublons_query) * 0.5:
        print(f"\n   ⚠️ Plus de 50% des doublons viennent du même fichier !")
        print(f"   → BUG dans le script d'import à corriger")
    
    # Top 10 des fichiers problématiques
    print(f"\n🔥 TOP 10 FICHIERS AVEC DOUBLONS")
    fichiers_count = Counter()
    for d in doublons_query:
        for fichier_id in set(d.fichiers):
            fichiers_count[fichier_id] += 1
    
    for fichier_id, count in fichiers_count.most_common(10):
        print(f"   Fichier {fichier_id:<5} : {count:>4} groupes de doublons")
    
    # Exemple de doublons les plus graves
    print(f"\n⚠️ GROUPES AVEC LE PLUS DE DOUBLONS (Top 5)")
    top_doublons = sorted(doublons_query, key=lambda x: x.count, reverse=True)[:5]
    for i, d in enumerate(top_doublons, 1):
        print(f"   {i}. {d.nom} {d.prenom} : {d.count} doublons (IDs: {d.ids[:3]}...)")
    
    print(f"\n" + "=" * 80)
    print(f"💡 RECOMMANDATION")
    print(f"=" * 80)
    print(f"1. ✅ Corriger le bug d'import (éviter les doublons dans le même fichier)")
    print(f"2. 🧹 Nettoyer les {sum(d.count - 1 for d in doublons_query)} enquêtes en doublon")
    print(f"3. 🔍 Vérifier les fichiers {', '.join(map(str, [f for f, _ in fichiers_count.most_common(3)]))}")
    print()
