"""
Script d'import des fichiers CSV de sauvegarde depuis le dossier "reponses_cr backup".

Règles métier :
  - Toutes les enquêtes importées sont marquées NEG (code_resultat = 'N')
  - Données exclusives au client PARTNER (CLIENT_ID = 11)
  - Colonnes CSV attendues : nom, prenom, reference, dossier, memo
  - Les doublons (même numeroDossier pour PARTNER) sont détectés et ignorés

Usage :
  python import_csv_backup.py [chemin_du_dossier]

  Le chemin est optionnel ; par défaut : "reponses_cr backup" (relatif au CWD).

Exemple :
  python import_csv_backup.py "D:/EOS/reponses_cr backup"
"""

import csv
import glob
import logging
import os
import sys
from datetime import datetime

from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PARTNER_CLIENT_ID = 11
RESULT_NEG = 'N'                   # Code résultat négatif en base
STATUT_VALIDATION = 'archive'      # Statut des enquêtes importées

# Encodages à essayer dans l'ordre pour les CSV
CSV_ENCODINGS = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1', 'iso-8859-1']

# URL de connexion – priorité à la variable d'environnement DATABASE_URL
DEFAULT_DB_URL = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Sur Windows la page de code du terminal peut ne pas supporter les accents
# (ex : cp1255 hébreu). On force UTF-8 pour éviter les UnicodeEncodeError.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('import_csv_backup.log', encoding='utf-8'),
    ]
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_str(val: object, max_len: int | None = None) -> str | None:
    """Nettoie une valeur : strip, None si vide ou 'nan'."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return None
    if max_len:
        s = s[:max_len]
    return s


def normalize_col(name: str) -> str:
    """Normalise un nom de colonne pour la comparaison (majuscules, sans accents courants)."""
    return (
        str(name)
        .strip()
        .upper()
        .replace('É', 'E').replace('È', 'E').replace('Ê', 'E')
        .replace('À', 'A').replace('Â', 'A')
        .replace('Ù', 'U').replace('Û', 'U')
        .replace('Î', 'I').replace('Ï', 'I')
        .replace('Ô', 'O')
        .replace("'", '').replace('\u2019', '')
    )


def find_col(headers: list[str], *candidates: str) -> str | None:
    """Retourne le nom de colonne réel qui correspond à l'un des candidats (insensible à la casse/accents)."""
    col_map = {normalize_col(h): h for h in headers}
    for candidate in candidates:
        key = normalize_col(candidate)
        if key in col_map:
            return col_map[key]
    return None


def read_csv_with_encoding(filepath: str) -> tuple[list[dict], str]:
    """
    Essaie plusieurs encodages pour lire un CSV.
    Retourne (liste de lignes dict, encodage utilisé).
    Lève UnicodeDecodeError / csv.Error si aucun encodage ne fonctionne.
    """
    last_exc: Exception | None = None
    for enc in CSV_ENCODINGS:
        try:
            with open(filepath, newline='', encoding=enc) as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)   # force lecture complète pour détecter les erreurs d'encodage
            return rows, enc
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_exc = exc
            continue
        except csv.Error as exc:
            raise  # Erreur de format CSV → pas la peine d'essayer d'autres encodages
    raise last_exc  # type: ignore[misc]


def dossier_exists(conn, num_dossier: str) -> bool:
    """Vérifie si un enregistrement avec ce numeroDossier existe déjà pour PARTNER."""
    result = conn.execute(
        text(
            'SELECT 1 FROM donnees '
            'WHERE client_id = :cid AND "numeroDossier" = :num '
            'LIMIT 1'
        ),
        {'cid': PARTNER_CLIENT_ID, 'num': num_dossier},
    )
    return result.fetchone() is not None


def insert_fichier(conn, filename: str) -> int:
    """Crée un enregistrement dans la table fichiers et retourne son id."""
    conn.execute(
        text(
            'INSERT INTO fichiers (nom, client_id, date_upload) '
            'VALUES (:nom, :cid, NOW())'
        ),
        {'nom': filename, 'cid': PARTNER_CLIENT_ID},
    )
    fichier_id: int = conn.execute(
        text('SELECT MAX(id) FROM fichiers WHERE client_id = :cid'),
        {'cid': PARTNER_CLIENT_ID},
    ).scalar()
    return fichier_id


def insert_donnee(conn, fichier_id: int, num_dossier: str, ref_dossier: str | None,
                  nom: str, prenom: str | None) -> int:
    """Insère dans la table donnees et retourne l'id créé."""
    conn.execute(
        text(
            """INSERT INTO donnees (
                client_id, fichier_id, statut_validation,
                "typeDemande", "numeroDossier", "referenceDossier",
                nom, prenom,
                est_contestation, exported
            ) VALUES (
                :client_id, :fichier_id, :statut,
                'ENQ', :numeroDossier, :referenceDossier,
                :nom, :prenom,
                false, false
            )"""
        ),
        {
            'client_id': PARTNER_CLIENT_ID,
            'fichier_id': fichier_id,
            'statut': STATUT_VALIDATION,
            'numeroDossier': num_dossier,
            'referenceDossier': ref_dossier,
            'nom': nom,
            'prenom': prenom,
        },
    )
    donnee_id: int = conn.execute(
        text('SELECT MAX(id) FROM donnees WHERE client_id = :cid'),
        {'cid': PARTNER_CLIENT_ID},
    ).scalar()
    return donnee_id


def insert_donnee_enqueteur(conn, donnee_id: int, memo: str | None) -> None:
    """Insère dans la table donnees_enqueteur avec résultat NEG forcé."""
    conn.execute(
        text(
            """INSERT INTO donnees_enqueteur (
                client_id, donnee_id, code_resultat, notes_personnelles
            ) VALUES (
                :client_id, :donnee_id, :code_resultat, :notes
            )"""
        ),
        {
            'client_id': PARTNER_CLIENT_ID,
            'donnee_id': donnee_id,
            'code_resultat': RESULT_NEG,
            'notes': memo,
        },
    )

# ---------------------------------------------------------------------------
# Import d'un fichier CSV
# ---------------------------------------------------------------------------

def import_csv_file(engine, filepath: str) -> dict:
    """
    Importe un fichier CSV dans la base de données.

    Retourne un dict avec les clés :
        imported  – nombre de lignes insérées
        skipped   – lignes ignorées (vides ou doublons)
        errors    – liste de messages d'erreur par ligne
        encoding  – encodage détecté
    """
    filename = os.path.basename(filepath)
    stats = {'imported': 0, 'skipped': 0, 'errors': [], 'encoding': None}

    # --- Lecture du fichier ---
    try:
        rows, enc = read_csv_with_encoding(filepath)
        stats['encoding'] = enc
    except Exception as exc:
        msg = f"Impossible de lire le fichier ({exc})"
        log.error("  [ERREUR LECTURE] %s : %s", filename, msg)
        stats['errors'].append(msg)
        return stats

    if not rows:
        log.warning("  [VIDE] %s : aucune ligne de données.", filename)
        stats['errors'].append("Fichier vide ou sans données.")
        return stats

    # --- Détection des colonnes ---
    headers = list(rows[0].keys())
    c_nom     = find_col(headers, 'nom', 'NOM')
    c_prenom  = find_col(headers, 'prenom', 'prénom', 'PRENOM')
    c_ref     = find_col(headers, 'reference', 'référence', 'REFERENCE', 'REF')
    c_dossier = find_col(headers, 'dossier', 'DOSSIER', 'num_dossier', 'numeroDossier')
    c_memo    = find_col(headers, 'memo', 'MEMO', 'note', 'NOTE', 'notes')

    if not c_nom or not c_dossier:
        msg = (
            f"Colonnes obligatoires manquantes. "
            f"Trouvées : {headers}. "
            f"Requises : 'nom' et 'dossier'."
        )
        log.error("  [COLONNES MANQUANTES] %s : %s", filename, msg)
        stats['errors'].append(msg)
        return stats

    log.info(
        "  Colonnes détectées → nom=%s | prenom=%s | reference=%s | dossier=%s | memo=%s | encodage=%s",
        c_nom, c_prenom, c_ref, c_dossier, c_memo, enc,
    )

    # --- Insertion en base ---
    with engine.connect() as conn:
        fichier_id = insert_fichier(conn, filename)

        for line_num, row in enumerate(rows, start=2):   # start=2 : ligne 1 = en-tête
            nom       = clean_str(row.get(c_nom))
            num_dossier = clean_str(row.get(c_dossier))

            # Lignes vides / sans données obligatoires
            if not nom or not num_dossier:
                log.debug("  Ligne %d ignorée (nom ou dossier vide).", line_num)
                stats['skipped'] += 1
                continue

            # Détection des doublons
            if dossier_exists(conn, num_dossier):
                log.warning(
                    "  [DOUBLON] Ligne %d — dossier '%s' déjà présent pour PARTNER. Ignoré.",
                    line_num, num_dossier,
                )
                stats['skipped'] += 1
                continue

            try:
                prenom    = clean_str(row.get(c_prenom)  if c_prenom  else None)
                ref       = clean_str(row.get(c_ref)     if c_ref     else None)
                memo      = clean_str(row.get(c_memo)    if c_memo    else None)

                donnee_id = insert_donnee(conn, fichier_id, num_dossier, ref, nom, prenom)
                insert_donnee_enqueteur(conn, donnee_id, memo)

                stats['imported'] += 1
                log.debug("  Ligne %d importée — dossier=%s nom=%s", line_num, num_dossier, nom)

            except Exception as exc:
                msg = f"Ligne {line_num} (dossier={num_dossier}, nom={nom}) : {exc!s:.120}"
                log.error("  [ERREUR LIGNE] %s", msg)
                stats['errors'].append(msg)
                # On continue avec la ligne suivante sans rollback global

        conn.commit()

    return stats

# ---------------------------------------------------------------------------
# Parcours du dossier de sauvegarde
# ---------------------------------------------------------------------------

def scan_folder(folder: str) -> tuple[list[str], dict[str, list[str]]]:
    """
    Parcourt le dossier et retourne :
        csv_files        – liste des chemins des fichiers .csv
        other_files      – dict {extension: [chemins]} pour les autres formats
    """
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Dossier introuvable : {folder}")

    csv_files: list[str] = []
    other_files: dict[str, list[str]] = {}

    for entry in sorted(os.scandir(folder), key=lambda e: e.name):
        if not entry.is_file():
            continue
        ext = os.path.splitext(entry.name)[1].lower()
        if ext == '.csv':
            csv_files.append(entry.path)
        else:
            other_files.setdefault(ext, []).append(entry.path)

    return csv_files, other_files

# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else r'E:\LDMEOS\reponses_cr backup'
    backup_dir = os.path.abspath(backup_dir)

    log.info("=" * 70)
    log.info("Import CSV backup PARTNER — %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log.info("Dossier source : %s", backup_dir)
    log.info("=" * 70)

    # --- Connexion à la base ---
    try:
        engine = create_engine(DB_URL, echo=False)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        log.info("Connexion PostgreSQL OK.")
    except Exception as exc:
        log.critical("Impossible de se connecter à la base : %s", exc)
        log.critical("Vérifiez DATABASE_URL ou la valeur DEFAULT_DB_URL dans ce script.")
        sys.exit(1)

    # --- Vérification du client PARTNER ---
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, nom FROM clients WHERE id = :cid"),
            {'cid': PARTNER_CLIENT_ID},
        ).fetchone()
    if not row:
        log.critical(
            "Client PARTNER (id=%d) introuvable en base. "
            "Vérifiez PARTNER_CLIENT_ID dans ce script.",
            PARTNER_CLIENT_ID,
        )
        sys.exit(1)
    log.info("Client cible : %s (id=%d)", row[1], row[0])

    # --- Scan du dossier ---
    try:
        csv_files, other_files = scan_folder(backup_dir)
    except FileNotFoundError as exc:
        log.critical("%s", exc)
        sys.exit(1)

    log.info("\nFichiers CSV trouvés   : %d", len(csv_files))
    log.info("Autres formats trouvés : %d", sum(len(v) for v in other_files.values()))

    # Rapport sur les fichiers non-CSV
    if other_files:
        log.info("\n--- Fichiers ignorés (formats non-CSV) ---")
        for ext, paths in sorted(other_files.items()):
            log.info("  %s  (%d fichier%s)", ext or '[sans extension]', len(paths), 's' if len(paths) > 1 else '')
            for p in paths[:5]:            # affiche au max 5 exemples par extension
                log.info("      %s", os.path.basename(p))
            if len(paths) > 5:
                log.info("      ... et %d autres", len(paths) - 5)
        log.info(
            "\n  Ces fichiers n'ont pas été importés. "
            "Traitez-les manuellement ou adaptez ce script si nécessaire."
        )

    if not csv_files:
        log.warning("\nAucun fichier CSV trouvé dans le dossier. Fin du script.")
        sys.exit(0)

    # --- Import des CSV ---
    log.info("\n%s", "=" * 70)
    log.info("Démarrage de l'import de %d fichier(s) CSV…", len(csv_files))
    log.info("%s\n", "=" * 70)

    total_imported = 0
    total_skipped  = 0
    total_errors: list[str] = []
    failed_files: list[tuple[str, list[str]]] = []

    for i, filepath in enumerate(csv_files, start=1):
        fname = os.path.basename(filepath)
        log.info("[%d/%d] %s", i, len(csv_files), fname)

        stats = import_csv_file(engine, filepath)

        total_imported += stats['imported']
        total_skipped  += stats['skipped']
        total_errors.extend(stats['errors'])

        if stats['errors']:
            failed_files.append((fname, stats['errors']))

        log.info(
            "  → importées=%d  ignorées=%d  erreurs=%d",
            stats['imported'], stats['skipped'], len(stats['errors']),
        )

    # --- Résumé final ---
    log.info("\n%s", "=" * 70)
    log.info("RÉSULTAT FINAL")
    log.info("%s", "=" * 70)
    log.info("Fichiers CSV traités  : %d", len(csv_files))
    log.info("Enquêtes importées    : %d  (toutes marquées NEG)", total_imported)
    log.info("Lignes ignorées       : %d  (vides ou doublons)", total_skipped)
    log.info("Erreurs totales       : %d", len(total_errors))

    if failed_files:
        log.info("\n--- Fichiers avec erreurs (%d) ---", len(failed_files))
        for fname, errs in failed_files:
            log.info("  %s :", fname)
            for e in errs[:3]:
                log.info("    • %s", e)
            if len(errs) > 3:
                log.info("    … et %d autre(s) erreur(s)", len(errs) - 3)

    # --- Vérification en base ---
    with engine.connect() as conn:
        d_count = conn.execute(
            text('SELECT COUNT(*) FROM donnees WHERE client_id = :cid'),
            {'cid': PARTNER_CLIENT_ID},
        ).scalar()
        e_count = conn.execute(
            text('SELECT COUNT(*) FROM donnees_enqueteur WHERE client_id = :cid'),
            {'cid': PARTNER_CLIENT_ID},
        ).scalar()
        f_count = conn.execute(
            text('SELECT COUNT(*) FROM fichiers WHERE client_id = :cid'),
            {'cid': PARTNER_CLIENT_ID},
        ).scalar()

    log.info(
        "\nEn base (PARTNER) : fichiers=%d | donnees=%d | donnees_enqueteur=%d",
        f_count, d_count, e_count,
    )
    log.info("Log complet enregistré dans : import_csv_backup.log")
    log.info("Import terminé.")


if __name__ == '__main__':
    main()
