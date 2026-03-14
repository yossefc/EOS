"""
Compare les fichiers source (Excel/CSV) des backups avec les donnees importees en DB.
Identifie les ecarts de mapping et les donnees manquantes.
"""
import sys
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = create_app()
with app.app_context():

    # ================================================================
    # 1. PARTNER CR - Format A (65 colonnes)
    # ================================================================
    print("=" * 80)
    print("1. ANALYSE PARTNER CR - Format A (65 colonnes)")
    print("=" * 80)

    cr_dir = r'E:\LDMEOS\reponses_cr backup'
    # Prendre un fichier Format A (65 cols)
    xls_files = [f for f in os.listdir(cr_dir) if f.endswith('.xls')]

    format_a_file = None
    format_b_file = None
    for f in xls_files[:50]:
        try:
            df = pd.read_excel(os.path.join(cr_dir, f))
            if len(df.columns) >= 60:
                format_a_file = f
                break
        except:
            pass

    if format_a_file:
        print(f"\nFichier Format A: {format_a_file}")
        df = pd.read_excel(os.path.join(cr_dir, format_a_file))
        print(f"Colonnes ({len(df.columns)}): {list(df.columns)}")
        print(f"Lignes: {len(df)}")

        # Prendre la premiere ligne et comparer avec la DB
        for idx, row in df.head(3).iterrows():
            nom_fichier = str(row.get('NOM', '')).strip() if pd.notna(row.get('NOM')) else None
            prenom_fichier = str(row.get('PRENOM', '')).strip() if pd.notna(row.get('PRENOM')) else None
            num_fichier = str(row.get('NUM', '')).strip() if pd.notna(row.get('NUM')) else None

            print(f"\n  --- Ligne {idx} du fichier ---")
            print(f"  NUM: '{num_fichier}'")
            print(f"  NOM: '{nom_fichier}' | PRENOM: '{prenom_fichier}'")
            print(f"  TARIF: {row.get('TARIF')}")
            print(f"  DATE BUTOIR: {row.get('DATE BUTOIR')}")
            print(f"  ADRESSE: {row.get('ADRESSE')}")
            print(f"  CP: {row.get('CP')}")
            print(f"  VILLE: {row.get('VILLE')}")
            print(f"  EMPLOYEUR: {row.get('EMPLOYEUR')}")
            print(f"  RECHERCHE: {row.get('RECHERCHE')}")
            print(f"  INSTRUCTIONS: {row.get('INSTRUCTIONS')}")
            print(f"  Resultat: {row.get('Resultat')}")

            # Colonnes de reponse
            print(f"  [Reponse] Adresse 1: {row.get('Adresse 1')}")
            print(f"  [Reponse] Code postal: {row.get('Code postal')}")
            print(f"  [Reponse] Ville (rep): {row.get('Ville')}")
            print(f"  [Reponse] Telephone 1: {row.get('Telephone 1')}")
            print(f"  [Reponse] Nom employeur: {row.get('Nom employeur')}")
            print(f"  [Reponse] Nom banque: {row.get('Nom banque')}")
            print(f"  [Reponse] Code Banque: {row.get('Code Banque')}")
            print(f"  [Reponse] Montant facture: {row.get('Montant facture')}")
            print(f"  [Reponse] memo: {row.get('memo')}")

            # Chercher en DB
            if nom_fichier:
                db_donnees = Donnee.query.filter(
                    Donnee.client_id == 11,
                    Donnee.nom == nom_fichier,
                    Donnee.statut_validation.in_(['archive', 'archivee'])
                ).all()

                if db_donnees:
                    for d in db_donnees[:1]:
                        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
                        print(f"\n  --- DB Donnee ID={d.id} ---")
                        print(f"  numeroDossier: '{d.numeroDossier}'")
                        print(f"  nom: '{d.nom}' | prenom: '{d.prenom}'")
                        print(f"  tarif_lettre: {d.tarif_lettre}")
                        print(f"  date_butoir: {d.date_butoir}")
                        print(f"  adresse1: {d.adresse1}")
                        print(f"  codePostal: {d.codePostal}")
                        print(f"  ville: {d.ville}")
                        print(f"  nomEmployeur: {d.nomEmployeur}")
                        print(f"  recherche: {d.recherche}")
                        print(f"  instructions: {d.instructions}")
                        if de:
                            print(f"  [DE] code_resultat: {de.code_resultat}")
                            print(f"  [DE] adresse1: {de.adresse1}")
                            print(f"  [DE] code_postal: {de.code_postal}")
                            print(f"  [DE] ville: {de.ville}")
                            print(f"  [DE] telephone_personnel: {de.telephone_personnel}")
                            print(f"  [DE] nom_employeur: {de.nom_employeur}")
                            print(f"  [DE] banque_domiciliation: {de.banque_domiciliation}")
                            print(f"  [DE] code_banque: {de.code_banque}")
                            print(f"  [DE] montant_facture: {de.montant_facture}")
                            print(f"  [DE] notes_personnelles: {de.notes_personnelles[:100] if de.notes_personnelles else None}")

                        # COMPARAISON
                        print(f"\n  --- ECARTS ---")
                        if num_fichier and d.numeroDossier != num_fichier:
                            print(f"  !! numeroDossier: fichier='{num_fichier}' vs DB='{d.numeroDossier}'")
                        if de:
                            res_fichier = str(row.get('Resultat', '')).strip() if pd.notna(row.get('Resultat')) else None
                            if res_fichier and de.code_resultat != res_fichier:
                                print(f"  !! code_resultat: fichier='{res_fichier}' vs DB='{de.code_resultat}'")
                else:
                    print(f"  !! NON TROUVE en DB pour nom='{nom_fichier}' client_id=11")

    # ================================================================
    # 2. PARTNER CR - Format B (5 colonnes - memo)
    # ================================================================
    print("\n\n" + "=" * 80)
    print("2. ANALYSE PARTNER CR - Format B (5 colonnes - memo)")
    print("=" * 80)

    for f in xls_files[:50]:
        try:
            df = pd.read_excel(os.path.join(cr_dir, f))
            if len(df.columns) <= 6 and 'memo' in [c.lower() for c in df.columns]:
                format_b_file = f
                break
        except:
            pass

    if format_b_file:
        print(f"\nFichier Format B: {format_b_file}")
        df = pd.read_excel(os.path.join(cr_dir, format_b_file))
        print(f"Colonnes: {list(df.columns)}")
        print(f"Lignes: {len(df)}")

        for idx, row in df.head(3).iterrows():
            print(f"\n  --- Ligne {idx} du fichier ---")
            for col in df.columns:
                val = row.get(col)
                print(f"  {col}: {val}")

            nom_val = str(row.get('nom', '')).strip() if pd.notna(row.get('nom')) else None
            ref_val = str(row.get('reference', '')).strip() if pd.notna(row.get('reference')) else None

            if nom_val:
                db_donnees = Donnee.query.filter(
                    Donnee.client_id == 11,
                    Donnee.nom == nom_val,
                    Donnee.statut_validation.in_(['archive', 'archivee'])
                ).all()
                if db_donnees:
                    for d in db_donnees[:1]:
                        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
                        print(f"  >>> DB: ID={d.id}, numeroDossier='{d.numeroDossier}', ref='{d.referenceDossier}'")
                        if de:
                            print(f"  >>> DE notes_personnelles: {de.notes_personnelles[:100] if de.notes_personnelles else 'VIDE'}")
                        else:
                            print(f"  >>> PAS DE DonneeEnqueteur")
                else:
                    print(f"  !! NON TROUVE en DB")

    # ================================================================
    # 3. PARTNER CRCONT (contestations)
    # ================================================================
    print("\n\n" + "=" * 80)
    print("3. ANALYSE PARTNER CRCONT (contestations)")
    print("=" * 80)

    crcont_dir = r'E:\LDMEOS\reponses_crcont backup'
    crcont_files = [f for f in os.listdir(crcont_dir) if f.endswith('.xls')]

    crcont_sample = None
    for f in crcont_files[:20]:
        try:
            df = pd.read_excel(os.path.join(crcont_dir, f))
            if len(df.columns) >= 15:
                crcont_sample = f
                break
        except:
            pass

    if crcont_sample:
        print(f"\nFichier: {crcont_sample}")
        df = pd.read_excel(os.path.join(crcont_dir, crcont_sample))
        print(f"Colonnes ({len(df.columns)}): {list(df.columns)}")
        print(f"Lignes: {len(df)}")

        for idx, row in df.head(3).iterrows():
            print(f"\n  --- Ligne {idx} ---")
            for col in df.columns:
                val = row.get(col)
                if pd.notna(val):
                    print(f"  {col}: {val}")

            nom_val = str(row.get('NOM', '')).strip() if pd.notna(row.get('NOM')) else None
            dossier_val = str(row.get('Dossier', '')).strip() if pd.notna(row.get('Dossier')) else None

            print(f"\n  Recherche DB: nom='{nom_val}', dossier='{dossier_val}'")
            if nom_val:
                db_donnees = Donnee.query.filter(
                    Donnee.client_id == 11,
                    Donnee.nom == nom_val,
                    Donnee.est_contestation == True,
                    Donnee.statut_validation.in_(['archive', 'archivee'])
                ).all()
                if db_donnees:
                    for d in db_donnees[:1]:
                        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
                        print(f"  >>> DB: ID={d.id}, numeroDossier='{d.numeroDossier}', motif='{d.motif}'")
                        if de:
                            print(f"  >>> DE: adresse1={de.adresse1}, cp={de.code_postal}, ville={de.ville}")
                            print(f"  >>> DE: tel={de.telephone_personnel}, montant={de.montant_facture}")
                            print(f"  >>> DE: notes={de.notes_personnelles[:100] if de.notes_personnelles else 'VIDE'}")
                else:
                    print(f"  !! NON TROUVE en DB comme contestation")

    # ================================================================
    # 4. EOS CSV
    # ================================================================
    print("\n\n" + "=" * 80)
    print("4. ANALYSE EOS CSV")
    print("=" * 80)

    eos_dir = r'E:\LDMEOS\reponses_EOS backup'
    csv_files = [f for f in os.listdir(eos_dir) if f.endswith('.csv')]

    if csv_files:
        csv_file = csv_files[0]
        print(f"\nFichier: {csv_file}")

        df = pd.read_csv(os.path.join(eos_dir, csv_file), sep=';', encoding='latin-1', dtype=str)
        print(f"Colonnes ({len(df.columns)}): {list(df.columns)[:20]}...")
        print(f"Lignes: {len(df)}")

        for idx, row in df.head(3).iterrows():
            num_dossier = str(row.get('N DOSSIER', '')).strip() if pd.notna(row.get('N DOSSIER')) else None
            ref_dossier = str(row.get('REFERENCE DOSSIER', '')).strip() if pd.notna(row.get('REFERENCE DOSSIER')) else None
            nom = str(row.get('NOM', '')).strip() if pd.notna(row.get('NOM')) else None
            prenom = str(row.get('PRENOM', '')).strip() if pd.notna(row.get('PRENOM')) else None

            print(f"\n  --- Ligne {idx} du CSV ---")
            print(f"  N DOSSIER: '{num_dossier}'")
            print(f"  REFERENCE DOSSIER: '{ref_dossier}'")
            print(f"  NOM: '{nom}' | PRENOM: '{prenom}'")
            col_type = "TYPE DE DEMANDE D'ENQUETE"
            col_resultat = "CODE RESULTAT DE L'ENQUETE"
            print(f"  TYPE DE DEMANDE: {row.get(col_type)}")
            print(f"  QUALITE: {row.get('QUALITE')}")
            print(f"  DATE NAISSANCE: {row.get('DATE DE NAISSANCE')}")
            print(f"  CODE RESULTAT: {row.get(col_resultat)}")
            print(f"  ELEMENTS RETROUVES: {row.get('ELEMENTS RETROUVES')}")
            print(f"  ADRESSE 1 (reponse): {row.get('ADRESSE 1')}")
            print(f"  CODE POSTAL (reponse): {row.get('CODE POSTAL')}")
            print(f"  VILLE (reponse): {row.get('VILLE')}")
            print(f"  MONTANT FACTURE: {row.get('MONTANT FACTURE')}")
            print(f"  TARIF APPLIQUE: {row.get('TARIF APPLIQUE')}")
            print(f"  MEMO 1: {row.get('MEMO 1')}")

            # Chercher en DB par reference
            if ref_dossier:
                d = Donnee.query.filter(
                    Donnee.client_id == 1,
                    Donnee.referenceDossier == ref_dossier,
                    Donnee.statut_validation.in_(['archive', 'archivee'])
                ).first()

                if d:
                    de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
                    print(f"\n  --- DB Donnee ID={d.id} ---")
                    print(f"  numeroDossier: '{d.numeroDossier}'")
                    print(f"  referenceDossier: '{d.referenceDossier}'")
                    print(f"  nom: '{d.nom}' | prenom: '{d.prenom}'")
                    print(f"  typeDemande: {d.typeDemande}")
                    print(f"  qualite: {d.qualite}")
                    print(f"  dateNaissance: {d.dateNaissance}")
                    if de:
                        print(f"  [DE] code_resultat: {de.code_resultat}")
                        print(f"  [DE] elements_retrouves: {de.elements_retrouves}")
                        print(f"  [DE] adresse1: {de.adresse1}")
                        print(f"  [DE] code_postal: {de.code_postal}")
                        print(f"  [DE] ville: {de.ville}")
                        print(f"  [DE] montant_facture: {de.montant_facture}")
                        print(f"  [DE] tarif_applique: {de.tarif_applique}")
                        print(f"  [DE] memo1: {de.memo1}")

                    # Comparer
                    print(f"\n  --- ECARTS ---")
                    if num_dossier and d.numeroDossier != num_dossier:
                        print(f"  !! numeroDossier: CSV='{num_dossier}' vs DB='{d.numeroDossier}'")
                    if nom and d.nom != nom:
                        print(f"  !! nom: CSV='{nom}' vs DB='{d.nom}'")
                    if de:
                        csv_resultat = str(row.get(col_resultat, '')).strip() if pd.notna(row.get(col_resultat)) else None
                        if csv_resultat and de.code_resultat != csv_resultat:
                            print(f"  !! code_resultat: CSV='{csv_resultat}' vs DB='{de.code_resultat}'")
                else:
                    print(f"  !! NON TROUVE en DB pour ref='{ref_dossier}'")

    # ================================================================
    # 5. STATS GLOBALES - Compter fichiers vs DB
    # ================================================================
    print("\n\n" + "=" * 80)
    print("5. COMPTAGE: FICHIERS SOURCE vs DB")
    print("=" * 80)

    # Compter les lignes dans tous les fichiers XLS cr
    total_cr_rows = 0
    for f in [f for f in os.listdir(cr_dir) if f.endswith('.xls')]:
        try:
            df = pd.read_excel(os.path.join(cr_dir, f))
            total_cr_rows += len(df)
        except:
            pass
    print(f"\nPARTNER CR: {total_cr_rows} lignes dans les fichiers XLS")

    # Compter les lignes dans les fichiers crcont
    total_crcont_rows = 0
    for f in [f for f in os.listdir(crcont_dir) if f.endswith(('.xls', '.xlsx'))]:
        try:
            df = pd.read_excel(os.path.join(crcont_dir, f))
            total_crcont_rows += len(df)
        except:
            pass
    print(f"PARTNER CRCONT: {total_crcont_rows} lignes dans les fichiers XLS/XLSX")

    # Compter les lignes dans les CSV EOS
    total_eos_rows = 0
    for f in csv_files:
        try:
            df = pd.read_csv(os.path.join(eos_dir, f), sep=';', encoding='latin-1', dtype=str)
            total_eos_rows += len(df)
        except:
            pass
    print(f"EOS CSV: {total_eos_rows} lignes dans les fichiers CSV")

    # En DB
    db_partner = Donnee.query.filter(Donnee.client_id == 11, Donnee.statut_validation.in_(['archive', 'archivee'])).count()
    db_eos = Donnee.query.filter(Donnee.client_id == 1, Donnee.statut_validation.in_(['archive', 'archivee'])).count()
    print(f"\nDB PARTNER archives: {db_partner}")
    print(f"DB EOS archives: {db_eos}")
    print(f"DB TOTAL archives: {db_partner + db_eos}")

    print(f"\nDifference PARTNER: fichiers={total_cr_rows + total_crcont_rows} vs DB={db_partner}")
    print(f"Difference EOS: fichiers={total_eos_rows} vs DB={db_eos}")
