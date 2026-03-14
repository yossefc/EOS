"""
Import des fichiers CSV "Reponses_EOS_*.csv" depuis le dossier "reponses_EOS backup".

Tables cibles (SQLAlchemy) :
  - fichiers          (models.Fichier)
  - donnees           (models.Donnee)
  - donnees_enqueteur (models_enqueteur.DonneeEnqueteur)

Client cible : EOS France (id = 1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE TEST (TEST_MODE = True) :
  - Lit uniquement le PREMIER fichier CSV trouvé
  - Extrait la PREMIÈRE ligne de données
  - Affiche le mapping complet vers la base (JSON structuré)
  - S'arrête sans aucun INSERT → safe à lancer en premier

MODE PRODUCTION (TEST_MODE = False) :
  - Parcourt tous les CSV du dossier
  - Détection des doublons : dossier déjà présent = ignoré
  - Commit par fichier, log complet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage :
  python import_eos_reponses.py [chemin_dossier]
  Par défaut : "reponses_EOS backup"
"""

import csv
import json
import logging
import os
import sys
from datetime import date, datetime

from sqlalchemy import create_engine, text

# ── Encodage terminal Windows ───────────────────────────────────────────────
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — modifiez ces deux constantes si nécessaire
# ════════════════════════════════════════════════════════════════════════════

TEST_MODE = False  # ← True = dry-run (aucun INSERT)  /  False = import réel

EOS_CLIENT_ID = 1  # clients.id de "EOS France"

DB_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'
)

CSV_ENCODINGS = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']
CSV_SEPARATOR = ';'

# ════════════════════════════════════════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('import_eos_reponses.log', encoding='utf-8'),
    ]
)
log = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def s(val: object, max_len: int | None = None) -> str | None:
    """Nettoie une valeur string : strip + None si vide."""
    if val is None:
        return None
    v = str(val).strip()
    if not v or v.lower() in ('nan', 'none', 'n/a'):
        return None
    return v[:max_len] if max_len else v


def d(val: object) -> date | None:
    """Parse une date au format JJ/MM/AAAA → date Python. Retourne None si invalide."""
    v = s(val)
    if not v:
        return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


def num(val: object) -> float | None:
    """Parse un montant décimal (virgule ou point). Retourne None si invalide."""
    v = s(val)
    if not v:
        return None
    try:
        return float(v.replace(',', '.'))
    except ValueError:
        return None


def integer(val: object) -> int | None:
    """Parse un entier. Retourne None si invalide."""
    v = s(val)
    if not v:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def clean_phone(val: object) -> str | None:
    """Garde uniquement chiffres et '+', max 15 caractères."""
    v = s(val)
    if not v:
        return None
    cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
    return cleaned[:15] if cleaned else None


def clean_cp(val: object) -> str | None:
    """Nettoie un code postal (zero-pad si < 5 chiffres)."""
    v = s(val)
    if not v:
        return None
    v = v.replace('.0', '')
    if v.isdigit() and len(v) < 5:
        v = v.zfill(5)
    return v[:10]


# ════════════════════════════════════════════════════════════════════════════
# MAPPING CSV → MODÈLES
# ════════════════════════════════════════════════════════════════════════════
# Colonnes CSV du fichier (séparateur ;, 81 colonnes, encodage utf-8-sig)
# Index : nom exact de la colonne CSV après strip()
# ─────────────────────────────────────────────────────────────────────────
# ⚠️  Si vos colonnes CSV ont des noms légèrement différents,
#     ajustez les clés du dictionnaire C (ligne ~170) en conséquence.
# ════════════════════════════════════════════════════════════════════════════

def normalize_headers(raw_headers: list[str]) -> dict[str, str]:
    """Construit un dict {header_normalise: header_original} pour lookup flexible."""
    return {h.strip().upper(): h.strip() for h in raw_headers}


def get(row: dict, key: str, hmap: dict[str, str]) -> str:
    """Récupère la valeur d'une colonne CSV par son nom normalisé (insensible casse)."""
    original = hmap.get(key.upper())
    return row.get(original, '') if original else ''


def build_donnee_dict(row: dict, hmap: dict[str, str], fichier_id: int) -> dict:
    """
    Mappe une ligne CSV vers le dictionnaire pour la table `donnees`.
    Correspond exactement aux colonnes de models.Donnee.
    """
    return {
        # ── Clés relationnelles ──────────────────────────────────────────
        'client_id':    EOS_CLIENT_ID,
        'fichier_id':   fichier_id,
        # ── Statut ──────────────────────────────────────────────────────
        'statut_validation': 'archive',
        'est_contestation':  False,
        'exported':          False,
        # ── Identifiants EOS ────────────────────────────────────────────
        'numeroDossier':            s(get(row, 'N° DOSSIER',                          hmap), 10),
        'referenceDossier':         s(get(row, 'REFERENCE DOSSIER',                   hmap), 15),
        'numeroInterlocuteur':      s(get(row, 'NUMERO INTERLOCUTEUR',                hmap), 12),
        'guidInterlocuteur':        s(get(row, 'GUID INTERLOCUTEUR',                  hmap), 36),
        # ── Type de demande ─────────────────────────────────────────────
        'typeDemande':              s(get(row, "TYPE DE DEMANDE D'ENQUÊTE",           hmap), 3),
        'numeroDemande':            s(get(row, 'NUMERO DEMANDE ENQUETE',              hmap), 11),
        'numeroDemandeContestee':   s(get(row, 'NUMERO DEMANDE ENQUETE CONTESTEE',    hmap), 11),
        'numeroDemandeInitiale':    s(get(row, 'NUMERO DEMANDE ENQUETE INITIALE',     hmap), 11),
        'forfaitDemande':           s(get(row, 'FORFAIT DEMANDE',                     hmap), 16),
        # ── Dates ───────────────────────────────────────────────────────
        'dateRetourEspere':         d(get(row, 'DATE DE RETOUR ESPERE',               hmap)),
        # ── État civil demandé ───────────────────────────────────────────
        'qualite':                  s(get(row, 'QUALITE',                             hmap), 10),
        'nom':                      s(get(row, 'NOM',                                 hmap), 30),
        'prenom':                   s(get(row, 'PRENOM',                              hmap), 20),
        'dateNaissance':            d(get(row, 'DATE DE NAISSANCE',                   hmap)),
        'lieuNaissance':            s(get(row, 'LIEU DE NAISSANCE',                   hmap), 50),
        'codePostalNaissance':      s(get(row, 'CODE POSTAL NAISSANCE',               hmap), 10),
        'paysNaissance':            s(get(row, 'PAYS DE NAISSANCE',                   hmap), 32),
        'nomPatronymique':          s(get(row, 'NOM DE JEUNE FILLE',                  hmap), 30),
        # ── Facturation (partie demande) ─────────────────────────────────
        'cumulMontantsPrecedents':  num(get(row, 'CUMUL DES MONTANTS PRECEDEMMENT FACTURES', hmap)),
    }


def build_enqueteur_dict(row: dict, hmap: dict[str, str], donnee_id: int) -> dict:
    """
    Mappe une ligne CSV vers le dictionnaire pour la table `donnees_enqueteur`.
    Correspond exactement aux colonnes de models_enqueteur.DonneeEnqueteur.
    """
    return {
        # ── Clés relationnelles ──────────────────────────────────────────
        'client_id':  EOS_CLIENT_ID,
        'donnee_id':  donnee_id,
        # ── Résultat ────────────────────────────────────────────────────
        'code_resultat':         s(get(row, "CODE RESULTAT DE L'ENQUETE", hmap), 1),
        'elements_retrouves':    s(get(row, 'ELEMENTS RETROUVES',         hmap), 10),
        'flag_etat_civil_errone':s(get(row, 'FLAG ÉTAT CIVIL ERRONÉ',     hmap), 1)
                               or s(get(row, "FLAG ETAT CIVIL ERRONE",    hmap), 1),
        'date_retour':           d(get(row, 'DATE DE RETOUR',             hmap)),
        # ── Décès ───────────────────────────────────────────────────────
        'date_deces':            d(get(row, 'DATE DE DECES',              hmap)),
        'numero_acte_deces':     s(get(row, "N° ACTE DE DECES",          hmap), 10),
        'code_insee_deces':      s(get(row, 'CODE INSEE DECES',           hmap), 5),
        'code_postal_deces':     s(get(row, 'CODE POSTAL DECES',          hmap), 10),
        'localite_deces':        s(get(row, 'LOCALITE DECES',             hmap), 32),
        # ── Adresse trouvée ─────────────────────────────────────────────
        'adresse1':              s(get(row, 'ADRESSE 1',                  hmap), 32),
        'adresse2':              s(get(row, 'ADRESSE 2',                  hmap), 32),
        'adresse3':              s(get(row, 'ADRESSE 3',                  hmap), 32),
        'adresse4':              s(get(row, 'ADRESSE 4',                  hmap), 32),
        'code_postal':           clean_cp(get(row, 'CODE POSTAL',         hmap)),
        'ville':                 s(get(row, 'VILLE',                      hmap), 32),
        'pays_residence':        s(get(row, 'PAYS RESIDENCE',             hmap), 32),
        # ── Téléphones ──────────────────────────────────────────────────
        'telephone_personnel':      clean_phone(get(row, 'TELEPHONE PERSONNEL',        hmap)),
        'telephone_chez_employeur': clean_phone(get(row, "TELEPHONE CHEZ L'EMPLOYEUR", hmap)),
        # ── Employeur ───────────────────────────────────────────────────
        'nom_employeur':         s(get(row, "NOM DE L'EMPLOYEUR",         hmap), 32),
        'telephone_employeur':   clean_phone(get(row, "TELEPHONE DE L'EMPLOYEUR", hmap)),
        'telecopie_employeur':   clean_phone(get(row, 'TELECOPIE EMPLOYEUR',      hmap)),
        'adresse1_employeur':    s(get(row, "ADRESSE 1 DE L'EMPLOYEUR",   hmap), 32),
        'adresse2_employeur':    s(get(row, "ADRESSE 2 DE L'EMPLOYEUR",   hmap), 32),
        'adresse3_employeur':    s(get(row, "ADRESSE 3 DE L'EMPLOYEUR",   hmap), 32),
        'adresse4_employeur':    s(get(row, "ADRESSE 4 DE L'EMPLOYEUR",   hmap), 32),
        'code_postal_employeur': clean_cp(get(row, "CODE POSTAL DE L'EMPLOYEUR", hmap)),
        'ville_employeur':       s(get(row, "VILLE DE L'EMPLOYEUR",       hmap), 32),
        'pays_employeur':        s(get(row, "PAYS DE L'EMPLOYEUR",        hmap), 32),
        # ── Banque ──────────────────────────────────────────────────────
        'banque_domiciliation':  s(get(row, 'BANQUE DE DOMICILIATION',    hmap), 32),
        'libelle_guichet':       s(get(row, 'LIBELLE GUICHET',            hmap), 30),
        'titulaire_compte':      s(get(row, 'TITULAIRE DU COMPTE',        hmap), 32),
        'code_banque':           s(get(row, 'CODE BANQUE',                hmap), 5),
        'code_guichet':          s(get(row, 'CODE GUICHET',               hmap), 5),
        # ── Revenus ─────────────────────────────────────────────────────
        'commentaires_revenus':         s(get(row, 'COMMENTAIRES SUR LES REVENUS',  hmap), 128),
        'montant_salaire':              num(get(row, 'MONTANT SALAIRE',              hmap)),
        'periode_versement_salaire':    integer(get(row, 'PERIODE VERSEMENT SALAIRE', hmap)),
        'frequence_versement_salaire':  s(get(row, 'FREQUENCE DE VERSEMENT DU SALAIRE', hmap), 2),
        'nature_revenu1':               s(get(row, 'NATURE REVENU1',                hmap), 30),
        'montant_revenu1':              num(get(row, 'MONTANT REVENU1',             hmap)),
        'periode_versement_revenu1':    integer(get(row, 'PERIODE VERSEMENT REVENU1', hmap)),
        'frequence_versement_revenu1':  s(get(row, 'FREQUENCE DE VERSEMENT DU REVENU1', hmap), 2),
        'nature_revenu2':               s(get(row, 'NATURE REVENU2',                hmap), 30),
        'montant_revenu2':              num(get(row, 'MONTANT REVENU2',             hmap)),
        'periode_versement_revenu2':    integer(get(row, 'PERIODE VERSEMENT REVENU2', hmap)),
        'frequence_versement_revenu2':  s(get(row, 'FREQUENCE DE VERSEMENT DU REVENU2', hmap), 2),
        'nature_revenu3':               s(get(row, 'NATURE REVENU3',                hmap), 30),
        'montant_revenu3':              num(get(row, 'MONTANT REVENU3',             hmap)),
        'periode_versement_revenu3':    integer(get(row, 'JOUR VERSEMENT REVENU3',  hmap)),
        'frequence_versement_revenu3':  s(get(row, 'FREQUENCE DE VERSEMENT DU REVENU3', hmap), 2),
        # ── Facturation ─────────────────────────────────────────────────
        'numero_facture':        s(get(row,   'NUMERO DE FACTURE',        hmap), 9),
        'date_facture':          d(get(row,   'DATE DE FACTURE',          hmap)),
        'montant_facture':       num(get(row, 'MONTANT FACTURé',          hmap))
                              or num(get(row, 'MONTANT FACTURE',          hmap)),
        'tarif_applique':        num(get(row, 'TARIF APPLIQUE',           hmap)),
        'reprise_facturation':   num(get(row, 'REPRISE DE FACTURATION',   hmap)),
        'remise_eventuelle':     num(get(row, 'REMISE EVENTUELLE',        hmap)),
        # ── Mémos ───────────────────────────────────────────────────────
        'memo1':  s(get(row, 'MEMO 1', hmap), 64),
        'memo2':  s(get(row, 'MEMO 2', hmap), 64),
        'memo3':  s(get(row, 'MEMO 3', hmap), 64),
        'memo4':  s(get(row, 'MEMO 4', hmap), 64),
        'memo5':  s(get(row, 'MEMO 5', hmap), 1000),
    }


# ════════════════════════════════════════════════════════════════════════════
# LECTURE CSV
# ════════════════════════════════════════════════════════════════════════════

def read_csv(filepath: str) -> tuple[list[dict], str]:
    """Lit un CSV avec détection automatique d'encodage. Retourne (rows, encoding)."""
    last_exc = None
    for enc in CSV_ENCODINGS:
        try:
            with open(filepath, newline='', encoding=enc) as fh:
                reader = csv.DictReader(fh, delimiter=CSV_SEPARATOR)
                rows = list(reader)
            return rows, enc
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_exc = exc
    raise last_exc  # type: ignore[misc]


# ════════════════════════════════════════════════════════════════════════════
# DOUBLON
# ════════════════════════════════════════════════════════════════════════════

def dossier_exists(conn, num_dossier: str) -> bool:
    row = conn.execute(
        text('SELECT 1 FROM donnees WHERE client_id=:cid AND "numeroDossier"=:num LIMIT 1'),
        {'cid': EOS_CLIENT_ID, 'num': num_dossier}
    ).fetchone()
    return row is not None


# ════════════════════════════════════════════════════════════════════════════
# INSERT
# ════════════════════════════════════════════════════════════════════════════

def insert_fichier(conn, filename: str) -> int:
    conn.execute(
        text('INSERT INTO fichiers (nom, client_id, date_upload) VALUES (:nom, :cid, NOW())'),
        {'nom': filename, 'cid': EOS_CLIENT_ID}
    )
    return conn.execute(
        text('SELECT MAX(id) FROM fichiers WHERE client_id=:cid'),
        {'cid': EOS_CLIENT_ID}
    ).scalar()


def insert_donnee(conn, data: dict) -> int:
    """Insère dans `donnees` et retourne l'id créé.
    Toutes les colonnes sont quotées pour gérer le camelCase PostgreSQL."""
    cols   = ', '.join(f'"{k}"' for k in data)   # ← quotes ALL (camelCase safe)
    params = ', '.join(f':{k}' for k in data)
    conn.execute(text(f'INSERT INTO donnees ({cols}) VALUES ({params})'), data)
    return conn.execute(
        text('SELECT MAX(id) FROM donnees WHERE client_id=:cid'),
        {'cid': EOS_CLIENT_ID}
    ).scalar()


def insert_donnee_enqueteur(conn, data: dict) -> None:
    cols   = ', '.join(f'"{k}"' for k in data)   # ← quotes ALL
    params = ', '.join(f':{k}' for k in data)
    conn.execute(text(f'INSERT INTO donnees_enqueteur ({cols}) VALUES ({params})'), data)


# ════════════════════════════════════════════════════════════════════════════
# AFFICHAGE TEST MODE
# ════════════════════════════════════════════════════════════════════════════

def _json_serial(obj):
    """Sérialiseur JSON pour date/datetime."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f'Type non sérialisable : {type(obj)}')


def display_test(donnee_data: dict, enqueteur_data: dict, filename: str, encoding: str):
    sep = '━' * 70
    print(f'\n{sep}')
    print(f'  MODE TEST — Premier fichier : {filename}  (encodage : {encoding})')
    print(f'  Première enquête — mapping complet vers la base de données')
    print(f'{sep}\n')

    print('┌─ TABLE : donnees ──────────────────────────────────────────────┐')
    for k, v in donnee_data.items():
        marker = '  ' if v is not None else '○ '   # ○ = champ vide
        print(f'  {marker}{k:<30} = {json.dumps(v, ensure_ascii=False, default=_json_serial)}')

    print('\n┌─ TABLE : donnees_enqueteur ────────────────────────────────────┐')
    for k, v in enqueteur_data.items():
        marker = '  ' if v is not None else '○ '
        print(f'  {marker}{k:<30} = {json.dumps(v, ensure_ascii=False, default=_json_serial)}')

    filled_d = sum(1 for v in donnee_data.values()   if v is not None)
    filled_e = sum(1 for v in enqueteur_data.values() if v is not None)
    print(f'\n{sep}')
    print(f'  donnees          : {filled_d}/{len(donnee_data)} champs renseignés')
    print(f'  donnees_enqueteur: {filled_e}/{len(enqueteur_data)} champs renseignés')
    print(f'{sep}')
    print('\n  ✓  Vérifiez le mapping ci-dessus.')
    print('  → Pour lancer le vrai import : passez TEST_MODE = False\n')


# ════════════════════════════════════════════════════════════════════════════
# IMPORT D'UN FICHIER CSV
# ════════════════════════════════════════════════════════════════════════════

def import_csv_file(engine, filepath: str) -> dict:
    filename = os.path.basename(filepath)
    stats = {'imported': 0, 'skipped': 0, 'errors': []}

    try:
        rows, enc = read_csv(filepath)
    except Exception as exc:
        stats['errors'].append(f'Lecture impossible : {exc}')
        return stats

    if not rows:
        stats['errors'].append('Fichier vide.')
        return stats

    hmap = normalize_headers(list(rows[0].keys()))

    with engine.connect() as conn:
        fichier_id = insert_fichier(conn, filename)

        for line_num, row in enumerate(rows, start=2):
            num_dossier = s(get(row, 'N° DOSSIER', hmap))
            if not num_dossier:
                stats['skipped'] += 1
                continue

            if dossier_exists(conn, num_dossier):
                log.debug('  [DOUBLON] dossier=%s', num_dossier)
                stats['skipped'] += 1
                continue

            try:
                # Savepoint par ligne : une erreur n'annule pas les lignes déjà insérées
                with conn.begin_nested():
                    donnee_data    = build_donnee_dict(row, hmap, fichier_id)
                    donnee_id      = insert_donnee(conn, donnee_data)
                    enqueteur_data = build_enqueteur_dict(row, hmap, donnee_id)
                    insert_donnee_enqueteur(conn, enqueteur_data)
                stats['imported'] += 1
            except Exception as exc:
                stats['errors'].append(f'Ligne {line_num} ({num_dossier}) : {str(exc)[:120]}')

        if stats['imported'] == 0:
            conn.execute(text('DELETE FROM fichiers WHERE id=:fid'), {'fid': fichier_id})

        conn.commit()

    return stats


# ════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ════════════════════════════════════════════════════════════════════════════

def main():
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else r'E:\LDMEOS\reponses_EOS backup'
    backup_dir = os.path.abspath(backup_dir)

    # ── Connexion ────────────────────────────────────────────────────────
    try:
        engine = create_engine(DB_URL, echo=False)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
    except Exception as exc:
        log.critical('Connexion PostgreSQL impossible : %s', exc)
        sys.exit(1)

    # ── Vérification client EOS ──────────────────────────────────────────
    with engine.connect() as conn:
        client = conn.execute(
            text('SELECT id, nom FROM clients WHERE id=:cid'),
            {'cid': EOS_CLIENT_ID}
        ).fetchone()
    if not client:
        log.critical('Client EOS (id=%d) introuvable en base.', EOS_CLIENT_ID)
        sys.exit(1)

    # ── Scan du dossier ──────────────────────────────────────────────────
    if not os.path.isdir(backup_dir):
        log.critical('Dossier introuvable : %s', backup_dir)
        sys.exit(1)

    all_files  = list(os.scandir(backup_dir))
    csv_files  = sorted(f.path for f in all_files if f.is_file() and f.name.lower().endswith('.csv'))
    other_exts: dict[str, int] = {}
    for f in all_files:
        if f.is_file() and not f.name.lower().endswith('.csv'):
            ext = os.path.splitext(f.name)[1].lower() or '(aucune)'
            other_exts[ext] = other_exts.get(ext, 0) + 1

    # ════════════════════════════════════════════════════════════════════
    # MODE TEST
    # ════════════════════════════════════════════════════════════════════
    if TEST_MODE:
        print('\n' + '═' * 70)
        print(f'  CLIENT : {client[1]} (id={client[0]})')
        print(f'  DOSSIER : {backup_dir}')
        print(f'  Fichiers CSV trouvés : {len(csv_files)}')
        if other_exts:
            print(f'  Autres formats (ignorés) : ' +
                  ', '.join(f'{ext} ×{n}' for ext, n in sorted(other_exts.items())))
        print('═' * 70)

        if not csv_files:
            print('\n  Aucun fichier CSV trouvé. Fin du mode test.')
            return

        first_file = csv_files[0]
        try:
            rows, enc = read_csv(first_file)
        except Exception as exc:
            log.error('Impossible de lire %s : %s', first_file, exc)
            return

        if not rows:
            print(f'\n  Le fichier {os.path.basename(first_file)} est vide.')
            return

        hmap = normalize_headers(list(rows[0].keys()))

        # Première ligne avec un N° DOSSIER valide
        first_valid = next(
            (r for r in rows if s(get(r, 'N° DOSSIER', hmap))),
            rows[0]
        )

        donnee_data    = build_donnee_dict(first_valid, hmap, fichier_id='<sera_généré>')
        enqueteur_data = build_enqueteur_dict(first_valid, hmap, donnee_id='<sera_généré>')
        display_test(donnee_data, enqueteur_data, os.path.basename(first_file), enc)
        return

    # ════════════════════════════════════════════════════════════════════
    # MODE PRODUCTION
    # ════════════════════════════════════════════════════════════════════
    log.info('=' * 70)
    log.info('Import EOS Réponses — %s', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log.info('Client : %s (id=%d) | Dossier : %s', client[1], client[0], backup_dir)
    log.info('Fichiers CSV : %d', len(csv_files))
    log.info('=' * 70)

    if not csv_files:
        log.warning('Aucun fichier CSV trouvé. Fin.')
        return

    if other_exts:
        log.info('Formats ignorés : %s',
                 ', '.join(f'{ext} ×{n}' for ext, n in sorted(other_exts.items())))

    with engine.connect() as conn:
        nb_avant = conn.execute(
            text('SELECT COUNT(*) FROM donnees WHERE client_id=:cid'),
            {'cid': EOS_CLIENT_ID}
        ).scalar()
    log.info('Enregistrements EOS avant import : %d\n', nb_avant)

    total_imported = 0
    total_skipped  = 0
    total_errors: list[str] = []
    failed_files:  list[tuple] = []

    for i, filepath in enumerate(csv_files, start=1):
        fname = os.path.basename(filepath)
        stats = import_csv_file(engine, filepath)
        total_imported += stats['imported']
        total_skipped  += stats['skipped']
        total_errors.extend(stats['errors'])
        if stats['errors']:
            failed_files.append((fname, stats['errors']))
        if i % 10 == 0 or i == len(csv_files):
            log.info('[%d/%d] importées=%d  ignorées=%d  erreurs=%d',
                     i, len(csv_files), total_imported, total_skipped, len(total_errors))

    log.info('\n' + '=' * 70)
    log.info('RÉSULTAT FINAL')
    log.info('=' * 70)
    log.info('Fichiers CSV traités : %d', len(csv_files))
    log.info('Enquêtes importées   : %d', total_imported)
    log.info('Lignes ignorées      : %d  (vides ou doublons)', total_skipped)
    log.info('Erreurs              : %d', len(total_errors))

    if failed_files:
        log.info('\n--- Fichiers avec erreurs ---')
        for fname, errs in failed_files:
            log.info('  %s :', fname)
            for e in errs[:3]:
                log.info('    • %s', e)
            if len(errs) > 3:
                log.info('    … +%d autre(s)', len(errs) - 3)

    with engine.connect() as conn:
        nb_apres = conn.execute(
            text('SELECT COUNT(*) FROM donnees WHERE client_id=:cid'),
            {'cid': EOS_CLIENT_ID}
        ).scalar()
    log.info('\nEOS avant : %d  |  après : %d  (+%d)',
             nb_avant, nb_apres, nb_apres - nb_avant)
    log.info('Log : import_eos_reponses.log')
    log.info('Import terminé.')


if __name__ == '__main__':
    main()
