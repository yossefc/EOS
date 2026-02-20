"""Script d'import CR avec mapping complet des 65 colonnes"""
import pandas as pd
import os
import sys
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
    try:
        j = int(float(str(jour))) if pd.notna(jour) else None
        m = int(float(str(mois))) if pd.notna(mois) else None
        a = int(float(str(annee))) if pd.notna(annee) else None
        if j and m and a:
            return f"{j:02d}/{m:02d}/{a:04d}"
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


def import_file(filepath):
    df = pd.read_excel(filepath, header=0)
    print(f"Fichier: {filepath}")
    print(f"Lignes: {len(df)}, Colonnes: {len(df.columns)}")

    with engine.connect() as conn:
        # Create fichier entry
        conn.execute(text(
            "INSERT INTO fichiers (nom, client_id, date_upload) VALUES (:nom, :cid, NOW())"
        ), {'nom': os.path.basename(filepath), 'cid': PARTNER_CLIENT_ID})
        fichier_id = conn.execute(text("SELECT MAX(id) FROM fichiers")).scalar()

        imported = 0
        skipped = 0

        for idx, row in df.iterrows():
            nom = clean_str(row.get('NOM'))
            num_dossier = clean_str(row.get('NUM'))
            if not nom or not num_dossier:
                skipped += 1
                continue

            date_naissance = combine_date(row.get('JOUR'), row.get('MOIS'), row.get('ANNEE NAISSANCE'))

            # === DONNEES ===
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
                'prenom': clean_str(row.get('PRENOM')),
                'nomPatronymique': clean_str(row.get('NJF')),
                'dateNaissance': date_naissance,
                'lieuNaissance': clean_str(row.get('LIEUNAISSANCE')),
                'paysNaissance': clean_str(row.get('PAYSNAISSANCE')),
                'adresse1': clean_str(row.get('ADRESSE')),
                'codePostal': clean_cp(row.get('CP')),
                'ville': clean_str(row.get('VILLE')),
                'paysResidence': clean_str(row.get('PAYS')),
                'telephonePersonnel': clean_phone(row.get('TEL')),
                'telephoneEmployeur': clean_phone(row.get('TEL2')),
                'titulaireCompte': clean_str(row.get('TITULAIRE')),
                'codeBanque': clean_str(row.get('CODEBANQUE'), 5),
                'numeroCompte': clean_str(row.get('COMPTE'), 11),
                'nomEmployeur': clean_str(row.get('EMPLOYEUR')),
                'tarif_lettre': clean_str(row.get('TARIF'), 10),
                'recherche': clean_str(row.get('RECHERCHE')),
                'instructions': clean_str(row.get('INSTRUCTIONS')),
                'date_butoir': parse_date(row.get('DATE BUTOIR')),
                'datedenvoie': parse_date(row.get('DATE ENVOI')),
            })

            donnee_id = conn.execute(text("SELECT MAX(id) FROM donnees")).scalar()

            # === DONNEES_ENQUETEUR ===
            tel_perso = clean_phone(row.get('Telephone 1')) or clean_phone(row.get('Portable 1'))
            tel_emp = clean_phone(row.get('Telephone 2')) or clean_phone(row.get('Portable 2'))

            notes_parts = []
            memo_val = clean_str(row.get('memo'))
            if memo_val:
                notes_parts.append(memo_val)
            memo_banque = clean_str(row.get('memo banque'))
            if memo_banque:
                notes_parts.append(f"[Banque] {memo_banque}")
            memo_employeur = clean_str(row.get('Memo employeur'))
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
                'code_resultat': resultat_convert(row.get('Resultat')),
                'proximite': clean_str(row.get('Proximite'), 50),
                'adresse1': clean_str(row.get('Adresse 1'), 32),
                'adresse2': clean_str(row.get('Adresse 2'), 32),
                'adresse3': clean_str(row.get('Adresse 3'), 32),
                'adresse4': clean_str(row.get('Adresse 4'), 32),
                'code_postal': clean_cp(row.get('Code postal')),
                'ville': clean_str(row.get('Ville'), 32),
                'pays_residence': clean_str(row.get('Pays'), 32),
                'telephone_personnel': tel_perso,
                'telephone_chez_employeur': tel_emp,
                'montant_facture': parse_decimal(row.get('Montant facture')),
                'notes_personnelles': '\n'.join(notes_parts) if notes_parts else None,
                'banque_domiciliation': clean_str(row.get('Nom banque'), 32),
                'code_banque': clean_str(row.get('Code Banque'), 5),
                'code_guichet': clean_str(row.get('Code guichet'), 5),
                'nom_employeur': clean_str(row.get('Nom employeur'), 32),
                'telephone_employeur': clean_phone(row.get('Telephone employeur')) or clean_phone(row.get('Telepone banque')),
                'adresse1_employeur': clean_str(row.get('Adresse 1 employeur'), 32),
                'adresse2_employeur': clean_str(row.get('Adresse 2 employeur'), 32),
                'adresse3_employeur': clean_str(row.get('Adresse 3 employeur'), 32),
                'adresse4_employeur': clean_str(row.get('Adresse 4 employeur'), 32),
            })

            imported += 1

        conn.commit()

    return imported, skipped


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'reponses_cr backup/cr_9_9_2025_21_33_10.xls'
    imported, skipped = import_file(filepath)
    print(f"\nResultat: {imported} importees, {skipped} ignorees")

    with engine.connect() as conn:
        d_count = conn.execute(text("SELECT COUNT(*) FROM donnees")).scalar()
        e_count = conn.execute(text("SELECT COUNT(*) FROM donnees_enqueteur")).scalar()
        print(f"En base: donnees={d_count}, donnees_enqueteur={e_count}")
