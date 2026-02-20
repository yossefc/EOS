"""Diagnostic approfondi des archives dans l'onglet Donnees."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from sqlalchemy import func, or_

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DIAGNOSTIC: Pourquoi les archives apparaissent dans Donnees?")
    print("=" * 60)

    # 1. Distribution exacte des statut_validation
    print("\n1. Distribution statut_validation (toutes les valeurs):")
    statuts = db.session.query(
        Donnee.statut_validation, func.count(Donnee.id)
    ).group_by(Donnee.statut_validation).all()
    for s, c in statuts:
        print(f"   '{s}' (type={type(s).__name__}, len={len(s) if s else 0}): {c}")

    # 2. Verifier les NULL
    nulls = Donnee.query.filter(Donnee.statut_validation == None).count()
    print(f"\n2. Donnees avec statut_validation NULL: {nulls}")

    # 3. Simuler la requete de /api/donnees pour chaque client
    print("\n3. Simulation requete /api/donnees (filtre notin archive/archivee/validee):")
    for client_id in [1, 11]:
        count = Donnee.query.filter(
            Donnee.client_id == client_id,
            Donnee.statut_validation.notin_(['validee', 'archive', 'archivee'])
        ).count()
        print(f"   Client {client_id}: {count} resultats retournes")

    # 4. Meme chose AVEC gestion NULL
    print("\n4. Simulation AVEC gestion NULL (or_ statut IS NULL):")
    for client_id in [1, 11]:
        count = Donnee.query.filter(
            Donnee.client_id == client_id,
            or_(
                Donnee.statut_validation.notin_(['validee', 'archive', 'archivee']),
                Donnee.statut_validation == None
            )
        ).count()
        print(f"   Client {client_id}: {count} resultats retournes")

    # 5. Verifier s'il y a des espaces ou caracteres invisibles
    print("\n5. Verification caracteres invisibles dans statut_validation:")
    archives = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee'])
    ).count()
    print(f"   Correspondance exacte 'archive'/'archivee': {archives}")

    all_non_null = Donnee.query.filter(Donnee.statut_validation != None).count()
    known_statuts = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee', 'en_attente', 'validee', 'valide'])
    ).count()
    print(f"   Total non-null: {all_non_null}, connus: {known_statuts}, inconnus: {all_non_null - known_statuts}")

    if all_non_null - known_statuts > 0:
        unknowns = db.session.query(
            Donnee.statut_validation, func.count(Donnee.id)
        ).filter(
            Donnee.statut_validation.notin_(['archive', 'archivee', 'en_attente', 'validee', 'valide'])
        ).group_by(Donnee.statut_validation).all()
        for s, c in unknowns:
            print(f"   INCONNU: '{s}' (repr={repr(s)}): {c}")

    # 6. Verifier la requete donnees-complete
    print("\n6. Simulation requete /api/donnees-complete:")
    for client_id in [1, 11]:
        count = Donnee.query.filter(
            Donnee.client_id == client_id,
            Donnee.statut_validation.notin_(['validee', 'archive', 'archivee'])
        ).count()
        print(f"   Client {client_id}: {count} resultats")

    # 7. Check si le frontend utilise donnees-complete
    print("\n7. Verifier les enquetes avec code_resultat (positif/negatif):")
    for client_id in [1, 11]:
        with_result = db.session.query(Donnee).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.client_id == client_id,
            Donnee.statut_validation.in_(['archive', 'archivee']),
            DonneeEnqueteur.code_resultat.isnot(None)
        ).count()
        print(f"   Client {client_id}: {with_result} archives avec code_resultat")

    print("\n" + "=" * 60)
