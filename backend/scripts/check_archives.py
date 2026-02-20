"""Script de verification des archives importees dans la base de donnees."""
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
    print("VERIFICATION DES ARCHIVES IMPORTEES")
    print("=" * 60)

    # 1. Stats generales
    total = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee'])).count()
    eos = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee']), Donnee.client_id == 1).count()
    partner = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee']), Donnee.client_id == 11).count()
    print(f"\nTotal archives: {total}")
    print(f"  EOS (client_id=1): {eos}")
    print(f"  PARTNER (client_id=11): {partner}")

    # 2. DonneeEnqueteur associees
    archive_ids = [d.id for d in Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee'])).all()]
    de_count = DonneeEnqueteur.query.filter(DonneeEnqueteur.donnee_id.in_(archive_ids)).count() if archive_ids else 0
    print(f"\nDonneeEnqueteur associees: {de_count}")
    orphelins = total - de_count
    print(f"  Donnees sans DonneeEnqueteur: {orphelins}")

    # 3. Repartition statut_validation
    statuts = db.session.query(Donnee.statut_validation, func.count(Donnee.id)).group_by(Donnee.statut_validation).all()
    print("\nRepartition statut_validation:")
    for s, c in statuts:
        print(f"  '{s}': {c}")

    # 4. Echantillon EOS - verifier les champs
    print("\n" + "=" * 60)
    print("ECHANTILLON EOS (5 premiers)")
    print("=" * 60)
    eos_samples = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.client_id == 1
    ).limit(5).all()

    for d in eos_samples:
        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
        print(f"\n  ID={d.id} | Dossier={d.numeroDossier} | Ref={d.referenceDossier}")
        print(f"    Nom={d.nom} | Prenom={d.prenom} | DateNaiss={d.dateNaissance}")
        print(f"    TypeDemande={d.typeDemande} | Qualite={d.qualite}")
        print(f"    Adresse={d.adresse1} | CP={d.codePostal} | Ville={d.ville}")
        print(f"    Employeur={d.nomEmployeur} | Tel={d.telephonePersonnel}")
        if de:
            print(f"    [DE] code_resultat={de.code_resultat} | elements={de.elements_retrouves}")
            print(f"    [DE] adresse1={de.adresse1} | cp={de.code_postal} | ville={de.ville}")
            print(f"    [DE] nom_employeur={de.nom_employeur} | tel_employeur={de.telephone_employeur}")
            print(f"    [DE] notes_perso={de.notes_personnelles[:80] if de.notes_personnelles else None}")
            print(f"    [DE] montant_facture={de.montant_facture} | tarif={de.tarif_applique}")
        else:
            print(f"    [DE] AUCUNE DONNEE ENQUETEUR")

    # 5. Echantillon PARTNER - verifier les champs
    print("\n" + "=" * 60)
    print("ECHANTILLON PARTNER (5 premiers)")
    print("=" * 60)
    partner_samples = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.client_id == 11
    ).limit(5).all()

    for d in partner_samples:
        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
        print(f"\n  ID={d.id} | Dossier={d.numeroDossier} | Ref={d.referenceDossier}")
        print(f"    Nom={d.nom} | Prenom={d.prenom} | DateNaiss={d.dateNaissance}")
        print(f"    Adresse={d.adresse1} | CP={d.codePostal} | Ville={d.ville}")
        print(f"    Employeur={d.nomEmployeur} | Tel={d.telephonePersonnel}")
        print(f"    Recherche={d.recherche} | Instructions={d.instructions}")
        if de:
            print(f"    [DE] code_resultat={de.code_resultat} | elements={de.elements_retrouves}")
            print(f"    [DE] adresse1={de.adresse1} | cp={de.code_postal} | ville={de.ville}")
            print(f"    [DE] nom_employeur={de.nom_employeur}")
            print(f"    [DE] banque={de.banque_domiciliation} | code_banque={de.code_banque}")
            print(f"    [DE] notes_perso={de.notes_personnelles[:80] if de.notes_personnelles else None}")
            print(f"    [DE] montant_facture={de.montant_facture}")
        else:
            print(f"    [DE] AUCUNE DONNEE ENQUETEUR")

    # 6. Verifier champs critiques non-null
    print("\n" + "=" * 60)
    print("VERIFICATION DES CHAMPS CRITIQUES")
    print("=" * 60)

    # Donnee
    no_num = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee']), Donnee.numeroDossier == None).count()
    no_nom = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee']), Donnee.nom == None).count()
    no_client = Donnee.query.filter(Donnee.statut_validation.in_(['archive', 'archivee']), Donnee.client_id == None).count()
    print(f"  Donnees sans numeroDossier: {no_num}")
    print(f"  Donnees sans nom: {no_nom}")
    print(f"  Donnees sans client_id: {no_client}")

    # DonneeEnqueteur
    if archive_ids:
        des = DonneeEnqueteur.query.filter(DonneeEnqueteur.donnee_id.in_(archive_ids))
        no_resultat = des.filter(DonneeEnqueteur.code_resultat == None).count()
        with_notes = des.filter(DonneeEnqueteur.notes_personnelles != None).count()
        with_facture = des.filter(DonneeEnqueteur.montant_facture != None).count()
        print(f"  DE sans code_resultat: {no_resultat}")
        print(f"  DE avec notes_personnelles: {with_notes}")
        print(f"  DE avec montant_facture: {with_facture}")

    # 7. Contestations PARTNER
    contestations = Donnee.query.filter(
        Donnee.statut_validation.in_(['archive', 'archivee']),
        Donnee.client_id == 11,
        Donnee.est_contestation == True
    ).count()
    print(f"\n  Contestations PARTNER: {contestations}")

    print("\n" + "=" * 60)
    print("VERIFICATION TERMINEE")
    print("=" * 60)
