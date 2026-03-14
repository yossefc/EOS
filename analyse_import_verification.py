"""
Script d'analyse et vérification de l'import des données
Analyse les tables donnees et donnees_enqueteur
Compare avec les fichiers Excel sources
Corrige le champ date_retour dans donnees_enqueteur
"""
import os
import sys
import re
import glob
import warnings
from datetime import date, datetime
from collections import defaultdict

warnings.filterwarnings('ignore')

# ── Setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db

import pandas as pd

app = create_app()

# ──────────────────────────────────────────────────────────────────────────────
# EXTRACTION DATE DEPUIS NOM DE FICHIER
# ──────────────────────────────────────────────────────────────────────────────

def extract_date_from_filename(filename):
    """
    Extrait la date depuis le nom du fichier.
    Formats connus :
      cr_DD_MM_YYYY_HH_MM_SS.xls   → date(YYYY, MM, DD)
      cr_D_M_YYYY_H_M_S.xls        → date(YYYY, MM, DD)
      crcont_DD_MM_YYYY_...xls     → idem
      Reponses_EOS_YYYY-M-D_H_M_S  → date(YYYY, M, D)
    """
    fname = os.path.splitext(os.path.basename(filename))[0]

    # Format EOS : Reponses_EOS_YYYY-M-D_H_M_S
    m = re.match(r'[Rr]eponses_EOS_(\d{4})-(\d{1,2})-(\d{1,2})_', fname)
    if m:
        y, mo, d_ = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d_)
        except ValueError:
            return None

    # Format CR / CRCONT : prefix_DD_MM_YYYY_HH_MM_SS
    # ou prefix_D_M_YYYY_H_M_S
    m = re.match(r'[a-z]+_(\d{1,2})_(\d{1,2})_(\d{4})_', fname, re.IGNORECASE)
    if m:
        d_, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d_)
        except ValueError:
            # essai inversé jour/mois
            try:
                return date(y, d_, mo)
            except ValueError:
                return None
    return None


# ──────────────────────────────────────────────────────────────────────────────
# LECTURE DES FICHIERS EXCEL
# ──────────────────────────────────────────────────────────────────────────────

def read_excel_rows(filepath):
    """Lit un fichier xls/xlsx et retourne (list_of_dicts, nb_lignes, colonnes)"""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        engine_xls = 'xlrd' if ext == '.xls' else 'openpyxl'
        df = pd.read_excel(filepath, header=0, dtype=str, engine=engine_xls)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        return None


def normalize_col(name):
    import unicodedata
    if not name:
        return ''
    nfd = unicodedata.normalize('NFD', str(name))
    without_acc = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', without_acc.upper())


def find_col(cols, *names):
    col_map = {normalize_col(c): c for c in cols}
    for name in names:
        n = normalize_col(name)
        if n in col_map:
            return col_map[n]
    return None


def extract_num_dossiers_from_row(row, cols):
    """
    Retourne une liste de candidats pour numeroDossier depuis une ligne Excel.
    - Pour CR: colonne NUM / N° Dossier / DOSSIER
    - Pour CRCONT memo (5 cols): la colonne 'reference' (ex: '10.02/50') ET la colonne 'dossier'
    - Pour CRCONT format plein: colonne 'Dossier'
    On retourne plusieurs candidats pour maximiser les chances de match.
    """
    candidates = []
    for col_name in ('NUM', 'N° Dossier', 'No Dossier', 'DOSSIER', 'reference', 'REFERENCE'):
        c = find_col(cols, col_name)
        if c and pd.notna(row.get(c)):
            val = str(row[c]).strip()
            # Nettoyer les flottants pandas (ex: '5.0' → '5') mais pas les refs (ex: '02.01/50')
            if re.match(r'^\d+\.0$', val):
                val = val[:-2]
            if val and val.lower() not in ('nan', ''):
                if val not in candidates:
                    candidates.append(val)
    return candidates


def extract_num_dossier_from_row(row, cols):
    """Retourne le premier candidat numeroDossier (compat. ancienne API)"""
    cands = extract_num_dossiers_from_row(row, cols)
    return cands[0] if cands else None


# ──────────────────────────────────────────────────────────────────────────────
# ANALYSE PRINCIPALE
# ──────────────────────────────────────────────────────────────────────────────

def run_analysis():
    with app.app_context():
        print("=" * 70)
        print("ANALYSE DE L'IMPORT - TABLES donnees et donnees_enqueteur")
        print("=" * 70)

        # ── 1. Vue d'ensemble de la base ──────────────────────────────────────
        print("\n── 1. VUE D'ENSEMBLE ──────────────────────────────────────────────")

        nb_donnees = db.session.execute(db.text('SELECT COUNT(*) FROM donnees')).scalar()
        nb_de = db.session.execute(db.text('SELECT COUNT(*) FROM donnees_enqueteur')).scalar()
        nb_fichiers = db.session.execute(db.text('SELECT COUNT(*) FROM fichiers')).scalar()
        print(f"  donnees            : {nb_donnees:>7}")
        print(f"  donnees_enqueteur  : {nb_de:>7}")
        print(f"  fichiers           : {nb_fichiers:>7}")

        # ── 2. Répartition par fichier source ─────────────────────────────────
        print("\n── 2. REPARTITION PAR FICHIER SOURCE ─────────────────────────────")
        rows = db.session.execute(db.text(
            "SELECT f.id, f.nom, COUNT(d.id) as nb "
            "FROM fichiers f LEFT JOIN donnees d ON d.fichier_id=f.id "
            "GROUP BY f.id, f.nom ORDER BY f.id"
        )).fetchall()
        for row in rows:
            print(f"  id={row[0]:>3} | {row[1][:55]:<55} | {row[2]:>5} enreg.")

        # ── 3. Qualité des données : donnees ──────────────────────────────────
        print("\n── 3. QUALITE TABLE donnees ──────────────────────────────────────")

        # Enquêtes sans nom ni prénom
        r = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees WHERE nom IS NULL AND prenom IS NULL"
        )).scalar()
        status = "✓ OK" if r == 0 else f"⚠ PROBLEME: {r} enreg."
        print(f"  Sans nom ET prénom             : {r:>6}  {status}")

        # Enquêtes sans numeroDossier (hors EOS qui utilise referenceDossier)
        r_cr = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d "
            "JOIN fichiers f ON f.id=d.fichier_id "
            "WHERE (d.\"numeroDossier\" IS NULL OR d.\"numeroDossier\"='') "
            "AND f.nom NOT LIKE '%EOS%'"
        )).scalar()
        status = "✓ OK" if r_cr == 0 else f"⚠ {r_cr} enreg. CR/CRCONT sans numéro dossier"
        print(f"  CR/CRCONT sans numeroDossier   : {r_cr:>6}  {status}")

        # EOS sans referenceDossier ni guidInterlocuteur
        r_eos = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d "
            "JOIN fichiers f ON f.id=d.fichier_id "
            "WHERE f.nom LIKE '%EOS%' "
            "AND (d.\"referenceDossier\" IS NULL OR d.\"referenceDossier\"='') "
            "AND (d.\"guidInterlocuteur\" IS NULL OR d.\"guidInterlocuteur\"='')"
        )).scalar()
        status = "✓ OK" if r_eos == 0 else f"⚠ {r_eos} enreg. EOS sans identifiant"
        print(f"  EOS sans ref/guid              : {r_eos:>6}  {status}")

        # Enquêtes tout NULL (aucun champ significatif rempli)
        r_null = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees "
            "WHERE nom IS NULL AND prenom IS NULL "
            "AND \"numeroDossier\" IS NULL AND \"referenceDossier\" IS NULL "
            "AND \"guidInterlocuteur\" IS NULL"
        )).scalar()
        status = "✓ OK" if r_null == 0 else f"⚠ PROBLEME: {r_null} enreg. sans aucune donnée!"
        print(f"  Enquêtes 100%% vides            : {r_null:>6}  {status}")

        # Doublons numeroDossier CR (même numéro, même client, hors contestations)
        r_dup = db.session.execute(db.text(
            "SELECT COUNT(*) FROM ("
            "  SELECT \"numeroDossier\" FROM donnees "
            "  WHERE \"numeroDossier\" IS NOT NULL AND est_contestation = false "
            "  AND client_id = 11 "
            "  GROUP BY \"numeroDossier\" HAVING COUNT(*) > 1"
            ") sub"
        )).scalar()
        status = "✓ OK" if r_dup == 0 else f"⚠ {r_dup} numéros dossier en double"
        print(f"  Doublons numeroDossier CR      : {r_dup:>6}  {status}")

        # ── 4. Qualité donnees_enqueteur ──────────────────────────────────────
        print("\n── 4. QUALITE TABLE donnees_enqueteur ────────────────────────────")

        r_de_orphan = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees_enqueteur de "
            "WHERE NOT EXISTS (SELECT 1 FROM donnees d WHERE d.id=de.donnee_id)"
        )).scalar()
        status = "✓ OK" if r_de_orphan == 0 else f"⚠ PROBLEME: {r_de_orphan} entrées sans donnee parente"
        print(f"  Orphelines (sans donnee)       : {r_de_orphan:>6}  {status}")

        r_no_de = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d "
            "WHERE NOT EXISTS (SELECT 1 FROM donnees_enqueteur de WHERE de.donnee_id=d.id)"
        )).scalar()
        status = "✓ OK" if r_no_de == 0 else f"⚠ {r_no_de} enquêtes sans entrée enquêteur"
        print(f"  donnees sans enquêteur         : {r_no_de:>6}  {status}")

        r_no_result = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees_enqueteur WHERE code_resultat IS NULL"
        )).scalar()
        pct = round(100 * r_no_result / max(nb_de, 1), 1)
        print(f"  Sans code_resultat             : {r_no_result:>6}  ({pct}%%)")

        r_no_date = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees_enqueteur WHERE date_retour IS NULL"
        )).scalar()
        pct = round(100 * r_no_date / max(nb_de, 1), 1)
        status = "✓ OK" if r_no_date == 0 else f"⚠ À CORRIGER: {r_no_date} entrées ({pct}%%)"
        print(f"  Sans date_retour               : {r_no_date:>6}  {status}")

        # Multi-entrées pour une même donnee
        r_multi = db.session.execute(db.text(
            "SELECT COUNT(*) FROM ("
            "  SELECT donnee_id FROM donnees_enqueteur "
            "  GROUP BY donnee_id HAVING COUNT(*) > 1"
            ") sub"
        )).scalar()
        status = "✓ OK" if r_multi == 0 else f"⚠ {r_multi} enquêtes avec plusieurs entrées enquêteur"
        print(f"  Doublons donnees_enqueteur     : {r_multi:>6}  {status}")

        # ── 5. Comptage fichiers Excel sources ────────────────────────────────
        print("\n── 5. FICHIERS EXCEL SOURCES vs BASE DE DONNEES ─────────────────")
        dirs_info = [
            ('E:/LDMEOS/reponses_cr backup', 'cr_*.xls', 'PARTNER CR', 11),
            ('E:/LDMEOS/reponses_crcont backup', 'crcont_*.xls', 'PARTNER CRCONT', 11),
        ]
        for dirpath, pattern, label, cid in dirs_info:
            files = sorted(glob.glob(os.path.join(dirpath, pattern)))
            nb_files = len(files)
            nb_rows_excel = 0
            nb_with_date = 0
            bad_dates = []
            for fp in files:
                d_from_name = extract_date_from_filename(fp)
                if d_from_name:
                    nb_with_date += 1
                else:
                    bad_dates.append(os.path.basename(fp))
                df = read_excel_rows(fp)
                if df is not None:
                    nb_rows_excel += len(df)
            print(f"\n  {label}:")
            print(f"    Fichiers Excel trouvés       : {nb_files}")
            print(f"    Lignes totales dans Excel    : {nb_rows_excel}")
            print(f"    Fichiers avec date parseable : {nb_with_date}/{nb_files}")
            if bad_dates:
                print(f"    Fichiers sans date parseable : {len(bad_dates)}")
                for b in bad_dates[:5]:
                    print(f"      - {b}")

        # Comparaison avec DB
        r_cr_db = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d JOIN fichiers f ON f.id=d.fichier_id "
            "WHERE f.nom LIKE '%cr backup%' AND f.nom NOT LIKE '%crcont%'"
        )).scalar()
        r_crcont_db = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d JOIN fichiers f ON f.id=d.fichier_id "
            "WHERE f.nom LIKE '%crcont backup%'"
        )).scalar()
        r_eos_db = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees d JOIN fichiers f ON f.id=d.fichier_id "
            "WHERE f.nom LIKE '%EOS backup%'"
        )).scalar()
        print(f"\n  Enregistrements en base:")
        print(f"    CR      : {r_cr_db}")
        print(f"    CRCONT  : {r_crcont_db}")
        print(f"    EOS     : {r_eos_db}")

        # ── 6. Analyse date_retour par source ─────────────────────────────────
        print("\n── 6. ANALYSE date_retour PAR SOURCE ─────────────────────────────")
        res = db.session.execute(db.text(
            "SELECT f.nom, "
            "COUNT(de.id) as total, "
            "SUM(CASE WHEN de.date_retour IS NULL THEN 1 ELSE 0 END) as sans_date "
            "FROM donnees d "
            "JOIN fichiers f ON f.id=d.fichier_id "
            "LEFT JOIN donnees_enqueteur de ON de.donnee_id=d.id "
            "WHERE f.nom LIKE '%ARCHIVE%' "
            "GROUP BY f.nom ORDER BY f.nom"
        )).fetchall()
        for row in res:
            pct = round(100 * (row[2] or 0) / max(row[1], 1), 1)
            print(f"  {row[0][:45]:<45} : {row[1]:>5} total, {row[2] or 0:>5} sans date ({pct}%%)")

        print("\n" + "=" * 70)
        print("ANALYSE TERMINÉE")
        print("=" * 70)

        return {
            'nb_donnees': nb_donnees,
            'nb_de': nb_de,
            'r_de_orphan': r_de_orphan,
            'r_no_de': r_no_de,
            'r_no_date': r_no_date,
            'r_dup': r_dup,
            'r_null': r_null,
        }


# ──────────────────────────────────────────────────────────────────────────────
# CORRECTION date_retour PAR RELECTURE DES FICHIERS EXCEL
# ──────────────────────────────────────────────────────────────────────────────

def fix_date_retour(dry_run=True):
    """
    Pour chaque fichier XLS dans les dossiers backup :
    1. Extrait la date du nom de fichier
    2. Lit le fichier, trouve les numeroDossier
    3. Construit un dict {numeroDossier: date_la_plus_ancienne}
    4. Met à jour date_retour dans donnees_enqueteur avec la date la plus ancienne trouvée
       (un dossier peut apparaître dans plusieurs fichiers hebdomadaires successifs,
        on prend toujours la première occurrence = date de retour réel)
    """
    with app.app_context():
        print("\n" + "=" * 70)
        print(f"CORRECTION date_retour ({'DRY-RUN' if dry_run else 'COMMIT REEL'})")
        print("=" * 70)

        dirs = [
            ('E:/LDMEOS/reponses_cr backup', 'cr_*.xls'),
            ('E:/LDMEOS/reponses_crcont backup', 'crcont_*.xls'),
        ]

        # ── Étape 1 : Scanner tous les fichiers, construire {numeroDossier: date_min} ──
        print("\nÉtape 1 : Scan des fichiers Excel...")
        num_to_earliest = {}   # {numeroDossier_str: date}
        errors_files = []
        total_rows_scanned = 0

        for dirpath, pattern in dirs:
            files = sorted(glob.glob(os.path.join(dirpath, pattern)))
            print(f"  {dirpath} : {len(files)} fichiers")
            for filepath in files:
                fname = os.path.basename(filepath)
                date_fichier = extract_date_from_filename(filepath)
                if not date_fichier:
                    errors_files.append(f"Date non parseable: {fname}")
                    continue

                df = read_excel_rows(filepath)
                if df is None:
                    errors_files.append(f"Lecture impossible: {fname}")
                    continue

                cols = df.columns.tolist()
                for _, row in df.iterrows():
                    candidates = extract_num_dossiers_from_row(row.to_dict(), cols)
                    if not candidates:
                        continue
                    total_rows_scanned += 1
                    for num in candidates:
                        existing = num_to_earliest.get(num)
                        if existing is None or date_fichier < existing:
                            num_to_earliest[num] = date_fichier

        print(f"  {len(num_to_earliest)} numéros de dossier uniques dans les fichiers Excel")
        print(f"  {total_rows_scanned} lignes scannées au total")
        if errors_files:
            print(f"  {len(errors_files)} fichiers en erreur:")
            for e in errors_files[:5]:
                print(f"    - {e}")

        # ── Étape 2 : Charger le mapping DB ────────────────────────────────────
        print("\nÉtape 2 : Chargement du mapping depuis la base...")
        rows_db = db.session.execute(db.text(
            "SELECT d.\"numeroDossier\", de.id as de_id, de.date_retour "
            "FROM donnees d "
            "JOIN fichiers f ON f.id=d.fichier_id "
            "JOIN donnees_enqueteur de ON de.donnee_id=d.id "
            "WHERE (f.nom LIKE '%cr backup%' OR f.nom LIKE '%crcont backup%') "
            "AND de.date_retour IS NULL "
            "AND d.\"numeroDossier\" IS NOT NULL"
        )).fetchall()

        print(f"  {len(rows_db)} entrées donnees_enqueteur à mettre à jour (date_retour NULL)")

        # ── Étape 3 : Préparer les mises à jour ────────────────────────────────
        updates = []
        not_found_in_excel = 0

        for row in rows_db:
            num = row[0]
            de_id = row[1]
            if not num:
                continue
            date_val = num_to_earliest.get(num.strip())
            if date_val:
                updates.append({'id': de_id, 'dr': date_val.isoformat()})
            else:
                not_found_in_excel += 1

        print(f"  {len(updates)} mises à jour préparées")
        print(f"  {not_found_in_excel} numéros non trouvés dans les fichiers Excel")

        # Aperçu des dates assignées
        if updates:
            dates_sample = [u['dr'] for u in updates[:20]]
            from collections import Counter
            year_months = Counter(d[:7] for d in dates_sample)
            print(f"  Exemple de dates assignées: {dict(list(year_months.items())[:5])}")

        # ── Étape 4 : Appliquer ────────────────────────────────────────────────
        if not dry_run and updates:
            print(f"\nApplication des {len(updates)} mises à jour...")
            # Batch par lots de 500
            batch_size = 500
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                for upd in batch:
                    db.session.execute(db.text(
                        "UPDATE donnees_enqueteur SET date_retour = :dr WHERE id = :id"
                    ), upd)
                db.session.commit()
                print(f"  Lot {i//batch_size + 1}/{(len(updates)-1)//batch_size + 1} commité")
            print(f"  ✓ {len(updates)} date_retour mis à jour.")
        elif dry_run:
            print(f"\n  ⚠ Mode DRY-RUN: aucune modification en base.")
            print(f"     Relancer avec --fix-date-retour --commit pour appliquer.")


# ──────────────────────────────────────────────────────────────────────────────
# SUPPRESSION DES DOUBLONS DONNEES_ENQUETEUR
# ──────────────────────────────────────────────────────────────────────────────

def fix_de_doublons(dry_run=True):
    """Supprime les doublons dans donnees_enqueteur (garde le + récent)"""
    with app.app_context():
        print("\n" + "=" * 70)
        print(f"CORRECTION DOUBLONS donnees_enqueteur ({'DRY-RUN' if dry_run else 'COMMIT'})")
        print("=" * 70)

        # Trouver les doublons
        doublons = db.session.execute(db.text(
            "SELECT donnee_id, COUNT(*) as nb, array_agg(id ORDER BY id) as ids "
            "FROM donnees_enqueteur GROUP BY donnee_id HAVING COUNT(*) > 1"
        )).fetchall()

        if not doublons:
            print("  Aucun doublon trouvé. ✓")
            return

        print(f"  {len(doublons)} donnees avec plusieurs entrées enquêteur")
        to_delete = []
        for row in doublons:
            ids = row[2]
            # Garder le dernier id (le plus récent), supprimer les autres
            to_delete.extend(ids[:-1])

        print(f"  Entrées à supprimer : {len(to_delete)}")

        if not dry_run and to_delete:
            db.session.execute(db.text(
                "DELETE FROM donnees_enqueteur WHERE id = ANY(:ids)"
            ), {'ids': to_delete})
            db.session.commit()
            print("  Suppression effectuée. ✓")
        else:
            print("  Mode DRY-RUN: aucune suppression.")


# ──────────────────────────────────────────────────────────────────────────────
# SUPPRESSION DES ORPHELINS donnees_enqueteur
# ──────────────────────────────────────────────────────────────────────────────

def fix_de_orphans(dry_run=True):
    """Supprime les entrées donnees_enqueteur sans donnee parente"""
    with app.app_context():
        print("\n" + "=" * 70)
        print(f"CORRECTION ORPHELINS donnees_enqueteur ({'DRY-RUN' if dry_run else 'COMMIT'})")
        print("=" * 70)

        nb = db.session.execute(db.text(
            "SELECT COUNT(*) FROM donnees_enqueteur de "
            "WHERE NOT EXISTS (SELECT 1 FROM donnees d WHERE d.id=de.donnee_id)"
        )).scalar()

        print(f"  Orphelins trouvés : {nb}")
        if nb == 0:
            print("  Aucun orphelin. ✓")
            return

        if not dry_run:
            db.session.execute(db.text(
                "DELETE FROM donnees_enqueteur de "
                "WHERE NOT EXISTS (SELECT 1 FROM donnees d WHERE d.id=de.donnee_id)"
            ))
            db.session.commit()
            print(f"  {nb} orphelins supprimés. ✓")
        else:
            print("  Mode DRY-RUN: aucune suppression.")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Analyse et correction import')
    parser.add_argument('--fix-date-retour', action='store_true',
                        help='Corriger les date_retour NULL (dry-run par defaut)')
    parser.add_argument('--fix-doublons', action='store_true',
                        help='Supprimer doublons donnees_enqueteur (dry-run)')
    parser.add_argument('--fix-orphelins', action='store_true',
                        help='Supprimer orphelins donnees_enqueteur (dry-run)')
    parser.add_argument('--commit', action='store_true',
                        help='Appliquer les corrections (sinon dry-run)')
    args = parser.parse_args()

    # Toujours faire l'analyse
    run_analysis()

    dry = not args.commit

    if args.fix_date_retour:
        fix_date_retour(dry_run=dry)

    if args.fix_doublons:
        fix_de_doublons(dry_run=dry)

    if args.fix_orphelins:
        fix_de_orphans(dry_run=dry)
