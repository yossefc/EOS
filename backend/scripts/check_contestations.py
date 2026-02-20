"""Diagnostic des contestations dans les archives."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from sqlalchemy import func

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DIAGNOSTIC CONTESTATIONS DANS LES ARCHIVES")
    print("=" * 60)

    # 1. Toutes les contestations archivees
    contestations = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.est_contestation == True
    ).all()
    print(f"\nContestations archivees (est_contestation=True): {len(contestations)}")

    # 2. Enquetes CON (typeDemande)
    con_enquetes = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.typeDemande == 'CON'
    ).all()
    print(f"Enquetes avec typeDemande='CON': {len(con_enquetes)}")

    # 3. Enquetes ENQ archivees
    enq_enquetes = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.typeDemande == 'ENQ'
    ).count()
    print(f"Enquetes avec typeDemande='ENQ': {enq_enquetes}")

    # 4. Echantillon contestations
    print("\n" + "=" * 60)
    print("ECHANTILLON CONTESTATIONS (10 premiers)")
    print("=" * 60)

    all_contestations = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        db.or_(
            Donnee.est_contestation == True,
            Donnee.typeDemande == 'CON'
        )
    ).limit(10).all()

    for d in all_contestations:
        print(f"\n  ID={d.id} | client_id={d.client_id}")
        print(f"  numeroDossier: '{d.numeroDossier}'")
        print(f"  referenceDossier: '{d.referenceDossier}'")
        print(f"  nom: {d.nom} | prenom: {d.prenom}")
        print(f"  typeDemande: {d.typeDemande}")
        print(f"  est_contestation: {d.est_contestation}")
        print(f"  enquete_originale_id: {d.enquete_originale_id}")
        print(f"  numeroDemandeContestee: {d.numeroDemandeContestee}")
        print(f"  numeroDemandeInitiale: {d.numeroDemandeInitiale}")
        print(f"  motif: {d.motif}")
        print(f"  motif_contestation_code: {d.motif_contestation_code}")

        # Chercher l'enquete originale par numeroDossier
        if d.numeroDossier:
            originales = Donnee.query.filter(
                Donnee.numeroDossier == d.numeroDossier,
                Donnee.id != d.id,
                Donnee.statut_validation.in_(['archive', 'archivee'])
            ).all()
            if originales:
                print(f"  >>> ENQUETE ORIGINALE TROUVEE: {[o.id for o in originales]} (typeDemande={[o.typeDemande for o in originales]})")
            else:
                # Chercher dans toutes les donnees (pas seulement archives)
                originales_all = Donnee.query.filter(
                    Donnee.numeroDossier == d.numeroDossier,
                    Donnee.id != d.id
                ).all()
                if originales_all:
                    print(f"  >>> ORIGINALE HORS ARCHIVES: {[(o.id, o.statut_validation, o.typeDemande) for o in originales_all]}")
                else:
                    print(f"  >>> AUCUNE ENQUETE ORIGINALE TROUVEE avec numeroDossier='{d.numeroDossier}'")

    # 5. Stats numeroDossier NULL dans les archives
    print("\n" + "=" * 60)
    print("STATS NUMERO DOSSIER")
    print("=" * 60)

    total_archives = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee'])).count()
    no_num = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        db.or_(Donnee.numeroDossier == None, Donnee.numeroDossier == '')
    ).count()
    print(f"  Total archives: {total_archives}")
    print(f"  Sans numeroDossier: {no_num}")
    print(f"  Avec numeroDossier: {total_archives - no_num}")

    # 6. Doublons de numeroDossier
    print("\n  Doublons numeroDossier (meme numero, plusieurs enquetes):")
    doublons = db.session.query(
        Donnee.numeroDossier, func.count(Donnee.id).label('cnt')
    ).filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.numeroDossier != None,
        Donnee.numeroDossier != ''
    ).group_by(Donnee.numeroDossier).having(func.count(Donnee.id) > 1).limit(10).all()

    for num, cnt in doublons:
        enquetes = Donnee.query.filter(
            Donnee.numeroDossier == num,
            Donnee.statut_validation.in_(['archive', 'archivee'])
        ).all()
        types = [(e.id, e.typeDemande, e.est_contestation, e.client_id) for e in enquetes]
        print(f"    '{num}': {cnt} enquetes -> {types}")

    print("\n" + "=" * 60)
