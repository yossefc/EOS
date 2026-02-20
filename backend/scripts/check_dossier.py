"""Diagnostic du dossier 7870181."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.enquetes_terminees import EnqueteTerminee

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DIAGNOSTIC DOSSIER 7870181")
    print("=" * 60)

    # Chercher par numeroDossier
    d = Donnee.query.filter_by(numeroDossier='7870181').first()
    if not d:
        d = Donnee.query.filter(Donnee.numeroDossier.like('%7870181%')).first()
    if not d:
        # Chercher aussi par referenceDossier
        d = Donnee.query.filter(Donnee.referenceDossier.like('%7870181%')).first()

    if not d:
        print("DOSSIER NON TROUVE!")
    else:
        print(f"\n  Donnee ID: {d.id}")
        print(f"  numeroDossier: '{d.numeroDossier}'")
        print(f"  referenceDossier: '{d.referenceDossier}'")
        print(f"  client_id: {d.client_id}")
        print(f"  statut_validation: '{d.statut_validation}' (repr={repr(d.statut_validation)})")
        print(f"  nom: {d.nom}")
        print(f"  prenom: {d.prenom}")
        print(f"  typeDemande: {d.typeDemande}")
        print(f"  enqueteurId: {d.enqueteurId}")
        print(f"  exported: {d.exported}")
        print(f"  exported_at: {d.exported_at}")
        print(f"  created_at: {d.created_at}")
        print(f"  updated_at: {d.updated_at}")

        # DonneeEnqueteur
        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
        if de:
            print(f"\n  [DonneeEnqueteur]")
            print(f"  code_resultat: {de.code_resultat}")
            print(f"  elements_retrouves: {de.elements_retrouves}")
            print(f"  date_retour: {de.date_retour}")
            print(f"  notes_personnelles: {de.notes_personnelles[:100] if de.notes_personnelles else None}")
        else:
            print(f"\n  [DonneeEnqueteur] AUCUNE")

        # EnqueteTerminee
        et = EnqueteTerminee.query.filter_by(donnee_id=d.id).first()
        if et:
            print(f"\n  [EnqueteTerminee]")
            print(f"  confirmed_at: {et.confirmed_at}")
            print(f"  confirmed_by: {et.confirmed_by}")
        else:
            print(f"\n  [EnqueteTerminee] AUCUNE")

        # Le filtre actuel l'exclut-il?
        excluded = d.statut_validation in ['validee', 'archive', 'archivee']
        print(f"\n  Exclu par le filtre actuel ['validee','archive','archivee']? {excluded}")
        print(f"  Exclu si on ajoute 'valide'? {d.statut_validation in ['validee', 'valide', 'archive', 'archivee']}")

    # Stats des statuts 'valide' vs 'validee'
    from sqlalchemy import func
    print("\n" + "=" * 60)
    print("ANALYSE 'valide' vs 'validee'")
    print("=" * 60)
    valide_count = Donnee.query.filter(Donnee.statut_validation == 'valide').count()
    validee_count = Donnee.query.filter(Donnee.statut_validation == 'validee').count()
    print(f"  'valide': {valide_count}")
    print(f"  'validee': {validee_count}")

    # Echantillon des 'valide'
    valides = Donnee.query.filter(Donnee.statut_validation == 'valide').limit(5).all()
    print(f"\n  Echantillon 'valide':")
    for v in valides:
        et = EnqueteTerminee.query.filter_by(donnee_id=v.id).first()
        print(f"    ID={v.id} Dossier={v.numeroDossier} client={v.client_id} exported={v.exported} terminee={'OUI' if et else 'NON'}")
