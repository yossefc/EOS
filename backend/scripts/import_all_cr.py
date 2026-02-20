"""Script d'import de TOUS les fichiers CR .xls avec mapping complet des 65 colonnes"""
import pandas as pd
import os
import sys
import glob
import traceback
from sqlalchemy import create_engine, text
from datetime import datetime

db_url = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db')
engine = create_engine(db_url)

PARTNER_CLIENT_ID = 11


def clean_str(val, max_len=None):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if s == '' or s.lower() == 'nan':
        return None
    if max_len:
        s = s[:max_len]
    return s


def clean_cp(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip().replace('.0', '')
    if s == '' or s.lower() == 'nan':
        return None
    if s.isdigit() and len(s) < 5:
        s = s.zfill(5)
    return s[:10]


def combine_date(jour, mois, annee):
    """Combine jour/mois/annee into a valid date string YYYY-MM-DD, or None if invalid"""
    from datetime import date as dt_date
    try:
        j = int(float(str(jour))) if pd.notna(jour) else None
        m = int(float(str(mois))) if pd.notna(mois) else None
        a = int(float(str(annee))) if pd.notna(annee) else None
        if j and m and a:
            # Swap day/month if month > 12 but day <= 12
            if m > 12 and j <= 12:
                j, m = m, j
            try:
                d = dt_date(a, m, j)
                return d.isoformat()
            except ValueError:
                # Invalid date - return None rather than crash
                return None
    except:
        pass
    return None


def parse_date(val):
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime('%Y-%m-%d')
    return None


def parse_decimal(val):
    if pd.isna(val) or val is None:
        return None
    try:
        return float(val)
    except:
        return None


def clean_phone(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if s in ('0', '0.0', '', 'nan'):
        return None
    cleaned = ''.join(c for c in s if c.isdigit() or c == '+')
    return cleaned[:15] if cleaned else None


def resultat_convert(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip().upper()
    mapping = {'POS': 'P', 'NEG': 'N', 'HOR': 'H'}
    if s in mapping:
        return mapping[s]
    return s[0] if s else None


# Column name normalization for matching
def normalize_col(col):
    return str(col).strip().upper().replace("'", "").replace("\u2019", "")


def find_col(df_columns, *names):
    """Find a column by trying multiple name variants"""
    col_map = {normalize_col(c): c for c in df_columns}
    for name in names:
        n = normalize_col(name)
        if n in col_map:
            return col_map[n]
    return None


def find_col_exact(df_columns, name):
    """Find a column by EXACT name match (case-sensitive)"""
    for c in df_columns:
        if str(c).strip() == name:
            return c
    return None


def import_memo_file(df, filepath):
    """Import memo simple format (5 cols: nom, prenom, reference, dossier, memo).
    These are memo-only updates - we try to match to existing donnees by dossier number,
    or create minimal records if no match."""
    cols = df.columns.tolist()
    c_nom = find_col(cols, 'nom')
    c_prenom = find_col(cols, 'prenom')
    c_ref = find_col(cols, 'reference')
    c_dossier = find_col(cols, 'dossier')
    c_memo = find_col(cols, 'memo')

    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO fichiers (nom, client_id, date_upload) VALUES (:nom, :cid, NOW())"
        ), {'nom': os.path.basename(filepath), 'cid': PARTNER_CLIENT_ID})
        fichier_id = conn.execute(text("SELECT MAX(id) FROM fichiers")).scalar()

        imported = 0
        skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                nom = clean_str(row.get(c_nom)) if c_nom else None
                if not nom:
                    skipped += 1
                    continue

                num_dossier = clean_str(row.get(c_dossier)) if c_dossier else None
                if not num_dossier:
                    skipped += 1
                    continue

                prenom = clean_str(row.get(c_prenom)) if c_prenom else None
                memo_val = clean_str(row.get(c_memo)) if c_memo else None

                # Create minimal donnee record
                donnee_sql = """INSERT INTO donnees (
                    client_id, fichier_id, statut_validation, "typeDemande", "numeroDossier",
                    nom, prenom, est_contestation, exported
                ) VALUES (
                    :client_id, :fichier_id, 'archive', 'ENQ', :numeroDossier,
                    :nom, :prenom, false, false
                )"""
                conn.execute(text(donnee_sql), {
                    'client_id': PARTNER_CLIENT_ID,
                    'fichier_id': fichier_id,
                    'numeroDossier': num_dossier,
                    'nom': nom,
                    'prenom': prenom,
                })
                donnee_id = conn.execute(text("SELECT MAX(id) FROM donnees")).scalar()

                # Create enqueteur record with memo
                enq_sql = """INSERT INTO donnees_enqueteur (
                    client_id, donnee_id, notes_personnelles
                ) VALUES (:client_id, :donnee_id, :notes)"""
                conn.execute(text(enq_sql), {
                    'client_id': PARTNER_CLIENT_ID,
                    'donnee_id': donnee_id,
                    'notes': memo_val,
                })

                imported += 1
            except Exception as e:
                errors.append(f"Row {idx} ({nom}): {str(e)[:100]}")

        conn.commit()

    return imported, skipped, errors


def import_file(filepath):
    """Import a single CR .xls file. Returns (imported, skipped, errors)"""
    try:
        df = pd.read_excel(filepath, header=0)
    except Exception as e:
        return 0, 0, [f"Cannot read file: {e}"]

    if len(df) == 0 or len(df.columns) < 5:
        return 0, 0, [f"File too small: {len(df)} rows, {len(df.columns)} cols"]

    # Map columns - try to find them by name
    cols = df.columns.tolist()

    # Check if this looks like a CR file (has at least NUM, NOM, Resultat)
    c_num = find_col(cols, 'NUM', 'N° Dossier', 'No Dossier')
    c_nom = find_col(cols, 'NOM')
    c_resultat = find_col(cols, 'Resultat', 'RESULTAT')

    # Check for memo simple format (5 cols: nom, prenom, reference, dossier, memo)
    c_memo_nom = find_col(cols, 'nom')
    c_memo_ref = find_col(cols, 'reference')
    c_memo_dossier = find_col(cols, 'dossier')
    is_memo_format = (not c_num) and c_memo_nom and c_memo_dossier and len(cols) <= 6

    if is_memo_format:
        return import_memo_file(df, filepath)

    if not c_num or not c_nom:
        return 0, 0, [f"Missing required columns NUM/NOM. Cols: {cols[:10]}"]

    with engine.connect() as conn:
        # Create fichier entry
        conn.execute(text(
            "INSERT INTO fichiers (nom, client_id, date_upload) VALUES (:nom, :cid, NOW())"
        ), {'nom': os.path.basename(filepath), 'cid': PARTNER_CLIENT_ID})
        fichier_id = conn.execute(text("SELECT MAX(id) FROM fichiers")).scalar()

        imported = 0
        skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                nom = clean_str(row.get(c_nom))
                num_dossier = clean_str(row.get(c_num))
                if not nom or not num_dossier:
                    skipped += 1
                    continue

                # Find columns dynamically
                c_prenom = find_col(cols, 'PRENOM')
                c_njf = find_col(cols, 'NJF')
                c_jour = find_col(cols, 'JOUR')
                c_mois = find_col(cols, 'MOIS')
                c_annee = find_col(cols, 'ANNEE NAISSANCE')
                c_lieu = find_col(cols, 'LIEUNAISSANCE')
                c_paysnais = find_col(cols, 'PAYSNAISSANCE')
                c_adresse = find_col(cols, 'ADRESSE')
                c_cp = find_col(cols, 'CP')
                # VILLE (majuscule) = ville demande, Ville (minuscule) = ville reponse
                c_ville = find_col_exact(cols, 'VILLE') or find_col(cols, 'VILLE')
                c_pays = find_col_exact(cols, 'PAYS') or find_col(cols, 'PAYS')
                c_tel = find_col(cols, 'TEL')
                c_tel2 = find_col(cols, 'TEL2')
                c_titulaire = find_col(cols, 'TITULAIRE')
                c_codebanque = find_col(cols, 'CODEBANQUE')
                c_compte = find_col(cols, 'COMPTE')
                c_employeur = find_col(cols, 'EMPLOYEUR')
                c_tarif = find_col(cols, 'TARIF')
                c_recherche = find_col(cols, 'RECHERCHE')
                c_instructions = find_col(cols, 'INSTRUCTIONS')
                c_datebutoir = find_col(cols, 'DATE BUTOIR')
                c_dateenvoi = find_col(cols, 'DATE ENVOI', 'DATE DU JOUR')

                date_naissance = combine_date(
                    row.get(c_jour) if c_jour else None,
                    row.get(c_mois) if c_mois else None,
                    row.get(c_annee) if c_annee else None
                )

                donnee_sql = """INSERT INTO donnees (
                    client_id, fichier_id, statut_validation, "typeDemande", "numeroDossier",
                    nom, prenom, "nomPatronymique", "dateNaissance", "lieuNaissance", "paysNaissance",
                    adresse1, "codePostal", ville, "paysResidence",
                    "telephonePersonnel", "telephoneEmployeur",
                    "titulaireCompte", "codeBanque", "numeroCompte", "nomEmployeur",
                    tarif_lettre, recherche, instructions, date_butoir, datedenvoie,
                    est_contestation, exported
                ) VALUES (
                    :client_id, :fichier_id, :statut_validation, :typeDemande, :numeroDossier,
                    :nom, :prenom, :nomPatronymique, :dateNaissance, :lieuNaissance, :paysNaissance,
                    :adresse1, :codePostal, :ville, :paysResidence,
                    :telephonePersonnel, :telephoneEmployeur,
                    :titulaireCompte, :codeBanque, :numeroCompte, :nomEmployeur,
                    :tarif_lettre, :recherche, :instructions, :date_butoir, :datedenvoie,
                    false, false
                )"""

                conn.execute(text(donnee_sql), {
                    'client_id': PARTNER_CLIENT_ID,
                    'fichier_id': fichier_id,
                    'statut_validation': 'archive',
                    'typeDemande': 'ENQ',
                    'numeroDossier': num_dossier,
                    'nom': nom,
                    'prenom': clean_str(row.get(c_prenom)) if c_prenom else None,
                    'nomPatronymique': clean_str(row.get(c_njf)) if c_njf else None,
                    'dateNaissance': date_naissance,
                    'lieuNaissance': clean_str(row.get(c_lieu)) if c_lieu else None,
                    'paysNaissance': clean_str(row.get(c_paysnais)) if c_paysnais else None,
                    'adresse1': clean_str(row.get(c_adresse)) if c_adresse else None,
                    'codePostal': clean_cp(row.get(c_cp)) if c_cp else None,
                    'ville': clean_str(row.get(c_ville)) if c_ville else None,
                    'paysResidence': clean_str(row.get(c_pays)) if c_pays else None,
                    'telephonePersonnel': clean_phone(row.get(c_tel)) if c_tel else None,
                    'telephoneEmployeur': clean_phone(row.get(c_tel2)) if c_tel2 else None,
                    'titulaireCompte': clean_str(row.get(c_titulaire)) if c_titulaire else None,
                    'codeBanque': clean_str(row.get(c_codebanque), 5) if c_codebanque else None,
                    'numeroCompte': clean_str(row.get(c_compte), 11) if c_compte else None,
                    'nomEmployeur': clean_str(row.get(c_employeur)) if c_employeur else None,
                    'tarif_lettre': clean_str(row.get(c_tarif), 10) if c_tarif else None,
                    'recherche': clean_str(row.get(c_recherche)) if c_recherche else None,
                    'instructions': clean_str(row.get(c_instructions)) if c_instructions else None,
                    'date_butoir': parse_date(row.get(c_datebutoir)) if c_datebutoir else None,
                    'datedenvoie': parse_date(row.get(c_dateenvoi)) if c_dateenvoi else None,
                })

                donnee_id = conn.execute(text("SELECT MAX(id) FROM donnees")).scalar()

                # === DONNEES_ENQUETEUR ===
                c_adr1 = find_col(cols, 'Adresse 1')
                c_adr2 = find_col(cols, 'Adresse 2')
                c_adr3 = find_col(cols, 'Adresse 3')
                c_adr4 = find_col(cols, 'Adresse 4')
                c_cp_resp = find_col(cols, 'Code postal')
                # Ville (minuscule) = ville reponse enqueteur
                c_ville_resp = find_col_exact(cols, 'Ville') or find_col(cols, 'Ville')
                c_pays_resp = find_col_exact(cols, 'Pays') or find_col(cols, 'Pays')
                c_tel1_resp = find_col(cols, 'Telephone 1')
                c_tel2_resp = find_col(cols, 'Telephone 2')
                c_port1 = find_col(cols, 'Portable 1')
                c_port2 = find_col(cols, 'Portable 2')
                c_montant = find_col(cols, 'Montant facture')
                c_memo = find_col(cols, 'memo', 'MEMO')
                c_nombanque = find_col(cols, 'Nom banque')
                c_codebanque_resp = find_col(cols, 'Code Banque')
                c_codeguichet = find_col(cols, 'Code guichet')
                c_nomemp = find_col(cols, 'Nom employeur')
                c_telemp = find_col(cols, 'Telephone employeur')
                c_telbanque = find_col(cols, 'Telepone banque')
                c_memobanque = find_col(cols, 'memo banque')
                c_memoemp = find_col(cols, 'Memo employeur')
                c_proximite = find_col(cols, 'Proximite')
                c_adr1emp = find_col(cols, 'Adresse 1 employeur')
                c_adr2emp = find_col(cols, 'Adresse 2 employeur')
                c_adr3emp = find_col(cols, 'Adresse 3 employeur')
                c_adr4emp = find_col(cols, 'Adresse 4 employeur')

                tel_perso = (clean_phone(row.get(c_tel1_resp)) if c_tel1_resp else None) or \
                            (clean_phone(row.get(c_port1)) if c_port1 else None)
                tel_emp = (clean_phone(row.get(c_tel2_resp)) if c_tel2_resp else None) or \
                          (clean_phone(row.get(c_port2)) if c_port2 else None)

                notes_parts = []
                memo_val = clean_str(row.get(c_memo)) if c_memo else None
                if memo_val:
                    notes_parts.append(memo_val)
                memo_banque = clean_str(row.get(c_memobanque)) if c_memobanque else None
                if memo_banque:
                    notes_parts.append(f"[Banque] {memo_banque}")
                memo_employeur = clean_str(row.get(c_memoemp)) if c_memoemp else None
                if memo_employeur:
                    notes_parts.append(f"[Employeur] {memo_employeur}")

                enq_sql = """INSERT INTO donnees_enqueteur (
                    client_id, donnee_id, code_resultat, proximite,
                    adresse1, adresse2, adresse3, adresse4, code_postal, ville, pays_residence,
                    telephone_personnel, telephone_chez_employeur,
                    montant_facture, notes_personnelles,
                    banque_domiciliation, code_banque, code_guichet,
                    nom_employeur, telephone_employeur,
                    adresse1_employeur, adresse2_employeur, adresse3_employeur, adresse4_employeur
                ) VALUES (
                    :client_id, :donnee_id, :code_resultat, :proximite,
                    :adresse1, :adresse2, :adresse3, :adresse4, :code_postal, :ville, :pays_residence,
                    :telephone_personnel, :telephone_chez_employeur,
                    :montant_facture, :notes_personnelles,
                    :banque_domiciliation, :code_banque, :code_guichet,
                    :nom_employeur, :telephone_employeur,
                    :adresse1_employeur, :adresse2_employeur, :adresse3_employeur, :adresse4_employeur
                )"""

                conn.execute(text(enq_sql), {
                    'client_id': PARTNER_CLIENT_ID,
                    'donnee_id': donnee_id,
                    'code_resultat': resultat_convert(row.get(c_resultat)) if c_resultat else None,
                    'proximite': clean_str(row.get(c_proximite), 50) if c_proximite else None,
                    'adresse1': clean_str(row.get(c_adr1), 32) if c_adr1 else None,
                    'adresse2': clean_str(row.get(c_adr2), 32) if c_adr2 else None,
                    'adresse3': clean_str(row.get(c_adr3), 32) if c_adr3 else None,
                    'adresse4': clean_str(row.get(c_adr4), 32) if c_adr4 else None,
                    'code_postal': clean_cp(row.get(c_cp_resp)) if c_cp_resp else None,
                    'ville': clean_str(row.get(c_ville_resp), 32) if c_ville_resp else None,
                    'pays_residence': clean_str(row.get(c_pays_resp), 32) if c_pays_resp else None,
                    'telephone_personnel': tel_perso,
                    'telephone_chez_employeur': tel_emp,
                    'montant_facture': parse_decimal(row.get(c_montant)) if c_montant else None,
                    'notes_personnelles': '\n'.join(notes_parts) if notes_parts else None,
                    'banque_domiciliation': clean_str(row.get(c_nombanque), 32) if c_nombanque else None,
                    'code_banque': clean_str(row.get(c_codebanque_resp), 5) if c_codebanque_resp else None,
                    'code_guichet': clean_str(row.get(c_codeguichet), 5) if c_codeguichet else None,
                    'nom_employeur': clean_str(row.get(c_nomemp), 32) if c_nomemp else None,
                    'telephone_employeur': (clean_phone(row.get(c_telemp)) if c_telemp else None) or \
                                           (clean_phone(row.get(c_telbanque)) if c_telbanque else None),
                    'adresse1_employeur': clean_str(row.get(c_adr1emp), 32) if c_adr1emp else None,
                    'adresse2_employeur': clean_str(row.get(c_adr2emp), 32) if c_adr2emp else None,
                    'adresse3_employeur': clean_str(row.get(c_adr3emp), 32) if c_adr3emp else None,
                    'adresse4_employeur': clean_str(row.get(c_adr4emp), 32) if c_adr4emp else None,
                })

                imported += 1

            except Exception as e:
                errors.append(f"Row {idx} ({nom}): {str(e)[:100]}")
                continue

        conn.commit()

    return imported, skipped, errors


if __name__ == '__main__':
    # Clean database first
    print("=== Nettoyage de la base ===")
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM partner_case_requests'))
        conn.execute(text('DELETE FROM enquete_facturation'))
        conn.execute(text('DELETE FROM enquete_archives'))
        conn.execute(text('DELETE FROM enquete_archive_files'))
        conn.execute(text('DELETE FROM export_batches'))
        conn.execute(text('DELETE FROM donnees_enqueteur'))
        conn.execute(text('DELETE FROM donnees'))
        conn.execute(text('DELETE FROM fichiers'))
        conn.commit()
    print("Base nettoyee.\n")

    # Find all .xls files
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else 'reponses_cr backup'
    files = sorted(glob.glob(os.path.join(backup_dir, 'cr_*.xls')))
    print(f"=== Import de {len(files)} fichiers .xls ===\n")

    total_imported = 0
    total_skipped = 0
    total_errors = []
    failed_files = []

    for i, filepath in enumerate(files):
        fname = os.path.basename(filepath)
        imported, skipped, errors = import_file(filepath)
        total_imported += imported
        total_skipped += skipped
        if errors:
            total_errors.extend(errors)
            failed_files.append((fname, errors))

        if (i + 1) % 50 == 0 or i == len(files) - 1:
            print(f"  [{i+1}/{len(files)}] Total: {total_imported} importees, {total_skipped} ignorees, {len(total_errors)} erreurs")

    print(f"\n=== RESULTAT FINAL ===")
    print(f"Fichiers traites: {len(files)}")
    print(f"Enquetes importees: {total_imported}")
    print(f"Lignes ignorees (vides): {total_skipped}")
    print(f"Erreurs: {len(total_errors)}")

    if failed_files:
        print(f"\n=== FICHIERS AVEC ERREURS ({len(failed_files)}) ===")
        for fname, errs in failed_files:
            print(f"\n  {fname}:")
            for e in errs[:3]:
                print(f"    - {e}")
            if len(errs) > 3:
                print(f"    ... et {len(errs)-3} autres erreurs")

    # Verify counts
    with engine.connect() as conn:
        d_count = conn.execute(text("SELECT COUNT(*) FROM donnees")).scalar()
        e_count = conn.execute(text("SELECT COUNT(*) FROM donnees_enqueteur")).scalar()
        f_count = conn.execute(text("SELECT COUNT(*) FROM fichiers")).scalar()
        print(f"\nEn base: fichiers={f_count}, donnees={d_count}, donnees_enqueteur={e_count}")
