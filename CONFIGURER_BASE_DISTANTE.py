#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURER_BASE_DISTANTE.py
============================
Analyse la base de données EOS locale, applique les migrations Alembic
sur le poste distant, puis synchronise toutes les tables de configuration.

Usage:
    python CONFIGURER_BASE_DISTANTE.py [--dry-run] [--skip-migrations] [--skip-sync]

Prérequis:
    pip install psycopg2-binary paramiko tabulate
    (paramiko pour SSH, tabulate pour l'affichage)
"""

import sys
import os
import time
import socket

# Forcer UTF-8 sur la console Windows pour éviter les erreurs d'encodage
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import subprocess
import argparse
import textwrap
from contextlib import contextmanager
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — À MODIFIER
# ─────────────────────────────────────────────────────────────────────────────

CONFIG = {

    # ── BASE DE DONNÉES LOCALE (SOURCE) ───────────────────────────────────────
    "local": {
        "host":     "localhost",
        "port":     5432,
        "dbname":   "eos_db",
        "user":     "eos_user",
        "password": "eos_password",
    },

    # ── BASE DE DONNÉES DISTANTE (CIBLE) ──────────────────────────────────────
    # Utilisée via un tunnel SSH local → distant:5432
    "remote": {
        "host":     "localhost",   # Ne pas changer (tunnel SSH)
        "port":     5433,          # Port LOCAL du tunnel SSH (différent de 5432)
        "dbname":   "eos_db",
        "user":     "postgres",
        "password": "postgres",
    },

    # ── SSH (via Tailscale) ────────────────────────────────────────────────────
    "ssh": {
        "host":        "100.X.X.X",      # ← IP Tailscale du poste distant (tailscale ip -4)
        "port":        22,
        "user":        "Utilisateur",    # ← Nom d'utilisateur Windows du poste distant
        "key_path":    os.path.join(os.path.expanduser("~"), ".ssh", "eos_sync_key"),
        # Chemin d'EOS sur le distant (pour lancer alembic)
        "eos_path":    "C:/EOS",
        "python_path": "C:/EOS/backend/venv/Scripts/python.exe",
    },

    # ── OPTIONS ───────────────────────────────────────────────────────────────
    "alembic_dir": os.path.join(os.path.dirname(__file__), "backend"),
}

# ─────────────────────────────────────────────────────────────────────────────
# TABLES DE CONFIGURATION — ordre respectant les clés étrangères
# ─────────────────────────────────────────────────────────────────────────────
#
# Pour chaque table :
#   "conflict_key" : colonne(s) servant d'identifiant unique pour UPSERT
#                    None = stratégie DELETE+INSERT (pas de contrainte unique)
#   "label"        : nom lisible pour les logs
#
CONFIG_TABLES = [
    {
        "table":        "clients",
        "label":        "Clients",
        "conflict_key": ["code"],          # UNIQUE sur clients.code
    },
    {
        "table":        "enqueteurs",
        "label":        "Enquêteurs",
        "conflict_key": ["email"],         # UNIQUE sur enqueteurs.email
    },
    {
        "table":        "tarifs_eos",
        "label":        "Tarifs EOS",
        "conflict_key": ["code"],          # UNIQUE sur tarifs_eos.code
    },
    {
        "table":        "import_profiles",
        "label":        "Profils d'import",
        "conflict_key": None,              # Pas de UNIQUE → DELETE+INSERT par client
        "fk_col":       "client_id",
    },
    {
        "table":        "import_field_mappings",
        "label":        "Mappings de champs",
        "conflict_key": None,              # Lié aux profils → DELETE+INSERT par profil
        "fk_col":       "import_profile_id",
    },
    {
        "table":        "tarifs_client",
        "label":        "Tarifs client",
        "conflict_key": None,              # DELETE+INSERT par client
        "fk_col":       "client_id",
    },
    {
        "table":        "tarifs_enqueteur",
        "label":        "Tarifs enquêteur",
        "conflict_key": None,              # DELETE+INSERT par client
        "fk_col":       "client_id",
    },
    {
        "table":        "confirmation_options",
        "label":        "Options de confirmation (PARTNER)",
        "conflict_key": ["client_id", "option_text"],   # UNIQUE (client_id, option_text)
    },
    {
        "table":        "partner_request_keywords",
        "label":        "Mots-clés PARTNER",
        "conflict_key": None,              # DELETE+INSERT par client
        "fk_col":       "client_id",
    },
    {
        "table":        "partner_tarif_rules",
        "label":        "Règles tarifaires PARTNER",
        "conflict_key": ["client_id", "tarif_lettre", "request_key"],  # UNIQUE composite
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# COULEURS CONSOLE (Windows compatible)
# ─────────────────────────────────────────────────────────────────────────────

def _enable_color():
    """Active les codes ANSI sur Windows 10+."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

_enable_color()

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
GRAY   = "\033[90m"

def ok(msg):   print(f"  {GREEN}[OK]{RESET}  {msg}")
def info(msg): print(f"  {GRAY}[--]{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}[!!]{RESET}  {msg}")
def fail(msg): print(f"  {RED}[XX]{RESET}  {msg}")
def step(n, title): print(f"\n{CYAN}{'-'*70}\n  ETAPE {n} : {title}\n{'-'*70}{RESET}")
def header(title): print(f"\n{BOLD}{CYAN}{'='*70}\n  {title}\n{'='*70}{RESET}")


# ─────────────────────────────────────────────────────────────────────────────
# GESTION DU TUNNEL SSH
# ─────────────────────────────────────────────────────────────────────────────

_ssh_tunnel_process = None

def start_ssh_tunnel():
    """
    Ouvre un tunnel SSH en arrière-plan :
        localhost:5433  →  distant:5432
    Utilise OpenSSH intégré à Windows (ssh.exe).
    """
    global _ssh_tunnel_process
    ssh = CONFIG["ssh"]
    remote = CONFIG["remote"]

    local_port  = remote["port"]   # 5433
    remote_port = 5432

    cmd = [
        "ssh",
        "-i",  ssh["key_path"],
        "-p",  str(ssh["port"]),
        "-L",  f"{local_port}:localhost:{remote_port}",
        "-N",                          # Ne pas exécuter de commande
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=30",
        f"{ssh['user']}@{ssh['host']}",
    ]

    info(f"Ouverture du tunnel SSH {ssh['host']}:{ssh['port']} → localhost:{local_port}")
    try:
        _ssh_tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except FileNotFoundError:
        fail("ssh.exe introuvable. Installe OpenSSH ou ajoute-le au PATH.")
        sys.exit(1)

    # Attendre que le tunnel soit disponible (max 15s)
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", local_port), timeout=1):
                ok(f"Tunnel SSH actif sur localhost:{local_port}")
                return
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)

    # Vérifier si le processus SSH a planté
    retcode = _ssh_tunnel_process.poll()
    if retcode is not None:
        err = _ssh_tunnel_process.stderr.read().decode(errors="replace")
        fail(f"Le tunnel SSH a échoué (code {retcode}).")
        fail(f"Erreur SSH : {err.strip()}")
        fail("Vérifie : IP distante, clé SSH, service sshd actif sur le distant.")
        sys.exit(1)

    fail(f"Timeout : le tunnel SSH n'est pas disponible après 15s sur le port {local_port}.")
    stop_ssh_tunnel()
    sys.exit(1)


def stop_ssh_tunnel():
    """Ferme le tunnel SSH proprement."""
    global _ssh_tunnel_process
    if _ssh_tunnel_process and _ssh_tunnel_process.poll() is None:
        _ssh_tunnel_process.terminate()
        try:
            _ssh_tunnel_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _ssh_tunnel_process.kill()
        _ssh_tunnel_process = None
        info("Tunnel SSH fermé.")


# ─────────────────────────────────────────────────────────────────────────────
# CONNEXIONS POSTGRESQL
# ─────────────────────────────────────────────────────────────────────────────

def get_connection(cfg_key: str):
    """Retourne une connexion psycopg2 (local ou remote)."""
    try:
        import psycopg2
    except ImportError:
        fail("psycopg2 non installé. Lance : pip install psycopg2-binary")
        sys.exit(1)

    c = CONFIG[cfg_key]
    return psycopg2.connect(
        host=c["host"], port=c["port"], dbname=c["dbname"],
        user=c["user"], password=c["password"],
        connect_timeout=10,
    )


@contextmanager
def db_cursor(cfg_key: str):
    """Context manager qui fournit un cursor autocommit."""
    conn = get_connection(cfg_key)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSE DU SCHÉMA
# ─────────────────────────────────────────────────────────────────────────────

SCHEMA_QUERY = """
SELECT
    t.table_name,
    c.column_name,
    c.data_type,
    c.character_maximum_length,
    c.numeric_precision,
    c.numeric_scale,
    c.is_nullable,
    c.column_default,
    c.ordinal_position
FROM information_schema.tables t
JOIN information_schema.columns c
    ON c.table_schema = t.table_schema
    AND c.table_name  = t.table_name
WHERE t.table_schema = 'public'
  AND t.table_type   = 'BASE TABLE'
ORDER BY t.table_name, c.ordinal_position;
"""

CONSTRAINTS_QUERY = """
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name  AS fk_table,
    ccu.column_name AS fk_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage  AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema   = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema   = tc.table_schema
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;
"""

INDEXES_QUERY = """
SELECT
    t.relname  AS table_name,
    i.relname  AS index_name,
    ix.indisunique,
    ix.indisprimary,
    array_to_string(array_agg(a.attname ORDER BY x.ordinality), ', ') AS columns
FROM pg_class t
JOIN pg_index  ix ON t.oid = ix.indrelid
JOIN pg_class  i  ON i.oid = ix.indexrelid
JOIN unnest(ix.indkey) WITH ORDINALITY AS x(attnum, ordinality)
    ON TRUE
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = x.attnum
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = 'public'
  AND t.relkind = 'r'
GROUP BY t.relname, i.relname, ix.indisunique, ix.indisprimary
ORDER BY t.relname, i.relname;
"""

SEQUENCES_QUERY = """
SELECT
    sequence_name,
    data_type,
    start_value,
    minimum_value,
    maximum_value,
    increment
FROM information_schema.sequences
WHERE sequence_schema = 'public'
ORDER BY sequence_name;
"""

ALEMBIC_VERSION_QUERY = """
SELECT version_num FROM alembic_version;
"""


def analyze_schema(cfg_key: str) -> dict:
    """Retourne un dictionnaire complet du schéma de la base."""
    result = {
        "tables":      {},    # {table_name: {col_name: {...}}}
        "constraints": {},    # {table_name: [constraint_dict, ...]}
        "indexes":     {},    # {table_name: [index_dict, ...]}
        "sequences":   [],
        "alembic":     None,
    }

    with db_cursor(cfg_key) as cur:
        # ── Colonnes ──────────────────────────────────────────────────────────
        cur.execute(SCHEMA_QUERY)
        for row in cur.fetchall():
            tbl, col, dtype, maxlen, prec, scale, nullable, default, pos = row
            if tbl not in result["tables"]:
                result["tables"][tbl] = {}
            result["tables"][tbl][col] = {
                "type":     dtype,
                "maxlen":   maxlen,
                "prec":     prec,
                "scale":    scale,
                "nullable": nullable,
                "default":  default,
                "pos":      pos,
            }

        # ── Contraintes ───────────────────────────────────────────────────────
        cur.execute(CONSTRAINTS_QUERY)
        for row in cur.fetchall():
            tbl, cname, ctype, col, fk_tbl, fk_col = row
            if tbl not in result["constraints"]:
                result["constraints"][tbl] = []
            result["constraints"][tbl].append({
                "name": cname, "type": ctype,
                "column": col, "fk_table": fk_tbl, "fk_column": fk_col,
            })

        # ── Index ─────────────────────────────────────────────────────────────
        cur.execute(INDEXES_QUERY)
        for row in cur.fetchall():
            tbl, iname, uniq, prim, cols = row
            if tbl not in result["indexes"]:
                result["indexes"][tbl] = []
            result["indexes"][tbl].append({
                "name": iname, "unique": uniq, "primary": prim, "columns": cols,
            })

        # ── Séquences ─────────────────────────────────────────────────────────
        cur.execute(SEQUENCES_QUERY)
        result["sequences"] = cur.fetchall()

        # ── Version Alembic ───────────────────────────────────────────────────
        try:
            cur.execute(ALEMBIC_VERSION_QUERY)
            row = cur.fetchone()
            result["alembic"] = row[0] if row else None
        except Exception:
            result["alembic"] = None

    return result


def format_col_type(col: dict) -> str:
    """Retourne la représentation du type de colonne (ex: varchar(255))."""
    dtype = col["type"]
    if col["maxlen"]:
        return f"{dtype}({col['maxlen']})"
    if col["prec"] and col["scale"]:
        return f"{dtype}({col['prec']},{col['scale']})"
    if col["prec"]:
        return f"{dtype}({col['prec']})"
    return dtype


# ─────────────────────────────────────────────────────────────────────────────
# COMPARAISON DES SCHÉMAS
# ─────────────────────────────────────────────────────────────────────────────

def compare_schemas(local: dict, remote: dict) -> dict:
    """
    Compare schéma local vs distant.
    Retourne un rapport avec :
        - tables_missing_remote : tables présentes en local mais absentes en distant
        - tables_extra_remote   : tables présentes en distant mais absentes en local
        - column_diffs          : {table: {col: (local_type, remote_type)}}
        - columns_missing       : {table: [col, ...]}  (absent en distant)
    """
    report = {
        "tables_missing_remote": [],
        "tables_extra_remote":   [],
        "column_diffs":          {},
        "columns_missing":       {},
        "ok":                    True,
    }

    local_tables  = set(local["tables"].keys())
    remote_tables = set(remote["tables"].keys())

    report["tables_missing_remote"] = sorted(local_tables - remote_tables)
    report["tables_extra_remote"]   = sorted(remote_tables - local_tables)

    for tbl in local_tables & remote_tables:
        local_cols  = local["tables"][tbl]
        remote_cols = remote["tables"][tbl]

        missing = [c for c in local_cols if c not in remote_cols]
        if missing:
            report["columns_missing"][tbl] = missing

        diffs = {}
        for col, lcol in local_cols.items():
            if col in remote_cols:
                lt = format_col_type(lcol)
                rt = format_col_type(remote_cols[col])
                if lt != rt:
                    diffs[col] = (lt, rt)
        if diffs:
            report["column_diffs"][tbl] = diffs

    if (report["tables_missing_remote"] or report["column_diffs"] or
            report["columns_missing"]):
        report["ok"] = False

    return report


def print_schema_report(local: dict, remote: dict, report: dict):
    """Affiche un rapport coloré de la comparaison des schémas."""
    try:
        from tabulate import tabulate
        use_tabulate = True
    except ImportError:
        use_tabulate = False

    local_tables  = sorted(local["tables"].keys())
    remote_tables = sorted(remote["tables"].keys())

    print(f"\n  {BOLD}Tables en local  : {len(local_tables)}{RESET}")
    print(f"  {BOLD}Tables en distant: {len(remote_tables)}{RESET}")
    print(f"  {BOLD}Version Alembic locale  : {local['alembic'] or 'inconnue'}{RESET}")
    print(f"  {BOLD}Version Alembic distante: {remote['alembic'] or 'inconnue'}{RESET}")

    if report["tables_missing_remote"]:
        warn(f"Tables ABSENTES sur le distant ({len(report['tables_missing_remote'])}) :")
        for t in report["tables_missing_remote"]:
            print(f"      {RED}[x] {t}{RESET}")

    if report["tables_extra_remote"]:
        info(f"Tables uniquement sur le distant ({len(report['tables_extra_remote'])}) :")
        for t in report["tables_extra_remote"]:
            print(f"      {YELLOW}[?] {t}{RESET}")

    if report["columns_missing"]:
        warn("Colonnes manquantes sur le distant :")
        for tbl, cols in report["columns_missing"].items():
            print(f"      {RED}[x] {tbl}: {', '.join(cols)}{RESET}")

    if report["column_diffs"]:
        warn("Différences de type de colonnes :")
        rows = []
        for tbl, diffs in report["column_diffs"].items():
            for col, (lt, rt) in diffs.items():
                rows.append([tbl, col, lt, rt])
        if use_tabulate:
            print(tabulate(rows, headers=["Table", "Colonne", "Local", "Distant"],
                           tablefmt="simple", stralign="left"))
        else:
            for r in rows:
                print(f"      {YELLOW}{r[0]}.{r[1]}: local={r[2]} distant={r[3]}{RESET}")

    if report["ok"] and local["alembic"] == remote["alembic"]:
        ok("Schémas identiques. Aucune différence structurelle détectée.")
    elif report["ok"] and local["alembic"] != remote["alembic"]:
        warn("Versions Alembic différentes mais aucune différence de colonnes détectée.")
        warn("Les migrations doivent être appliquées sur le distant.")


# ─────────────────────────────────────────────────────────────────────────────
# MIGRATIONS ALEMBIC VIA SSH
# ─────────────────────────────────────────────────────────────────────────────

def run_alembic_remote(dry_run: bool = False) -> bool:
    """
    Exécute 'alembic upgrade head' sur le poste distant via SSH.
    Retourne True si succès.
    """
    ssh = CONFIG["ssh"]

    alembic_cmd = (
        f'cmd /c "cd /d {ssh["eos_path"]}\\backend && '
        f'venv\\Scripts\\activate.bat && '
        f'alembic upgrade head 2>&1"'
    )

    ssh_cmd = [
        "ssh",
        "-i", ssh["key_path"],
        "-p", str(ssh["port"]),
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        f"{ssh['user']}@{ssh['host']}",
        alembic_cmd,
    ]

    if dry_run:
        info(f"[DRY-RUN] Commande SSH : {' '.join(ssh_cmd)}")
        return True

    info("Exécution de 'alembic upgrade head' sur le distant...")
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        fail("Timeout : alembic n'a pas répondu en 120s.")
        return False
    except FileNotFoundError:
        fail("ssh.exe introuvable dans le PATH.")
        return False

    output = result.stdout + result.stderr
    if output.strip():
        for line in output.strip().splitlines():
            info(f"  alembic: {line}")

    if result.returncode == 0:
        ok("Migrations Alembic appliquées avec succès.")
        return True
    else:
        fail(f"alembic upgrade head a échoué (code {result.returncode}).")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# SYNCHRONISATION DES DONNÉES DE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

def get_all_columns(cur, table_name: str) -> list:
    """Retourne la liste ordonnée des colonnes d'une table."""
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    return [row[0] for row in cur.fetchall()]


def sync_table_upsert(
    table: str,
    conflict_cols: list,
    dry_run: bool = False,
) -> tuple:
    """
    Synchronise une table via INSERT ... ON CONFLICT DO UPDATE.
    Retourne (inserts, updates, errors).
    """
    import psycopg2.extras

    local_conn  = get_connection("local")
    remote_conn = get_connection("remote")
    local_conn.autocommit  = True
    remote_conn.autocommit = False   # Transaction pour le distant

    lc = local_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    rc = remote_conn.cursor()

    inserts = updates = errors = 0

    try:
        # Colonnes de la table (depuis le distant)
        rc.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        cols = [r[0] for r in rc.fetchall()]
        if not cols:
            warn(f"Table '{table}' introuvable sur le distant (migrations non appliquées ?).")
            return (0, 0, 1)

        # Lire toutes les lignes locales
        lc.execute(f"SELECT {', '.join(cols)} FROM {table}")
        rows = lc.fetchall()
        info(f"  {len(rows)} enregistrement(s) à synchroniser dans '{table}'")

        if not rows:
            return (0, 0, 0)

        if dry_run:
            info(f"  [DRY-RUN] {len(rows)} lignes seraient envoyées vers '{table}'.")
            return (len(rows), 0, 0)

        # Construire la requête UPSERT
        col_list    = ", ".join(cols)
        placeholder = ", ".join(["%s"] * len(cols))
        update_cols = [c for c in cols if c not in conflict_cols and c != "id"]

        if update_cols:
            update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)
            conflict_str  = ", ".join(conflict_cols)
            sql = (
                f"INSERT INTO {table} ({col_list}) VALUES ({placeholder}) "
                f"ON CONFLICT ({conflict_str}) DO UPDATE SET {update_clause}"
            )
        else:
            conflict_str = ", ".join(conflict_cols)
            sql = (
                f"INSERT INTO {table} ({col_list}) VALUES ({placeholder}) "
                f"ON CONFLICT ({conflict_str}) DO NOTHING"
            )

        # Exécuter ligne par ligne pour compter inserts/updates
        for row in rows:
            values = [row[c] for c in cols]
            try:
                rc.execute(sql, values)
                inserts += 1
            except Exception as e:
                errors += 1
                warn(f"  Erreur sur {table} : {e}")
                remote_conn.rollback()
                remote_conn.autocommit = False

        remote_conn.commit()

    finally:
        lc.close(); local_conn.close()
        rc.close(); remote_conn.close()

    return (inserts, updates, errors)


def sync_table_delete_insert(
    table: str,
    fk_col: str,
    dry_run: bool = False,
) -> tuple:
    """
    Synchronise une table sans contrainte unique :
        1. Pour chaque valeur de fk_col présente en local, DELETE sur le distant
        2. INSERT de toutes les lignes locales

    Retourne (inserts, deletes, errors).
    """
    import psycopg2.extras

    local_conn  = get_connection("local")
    remote_conn = get_connection("remote")
    local_conn.autocommit  = True
    remote_conn.autocommit = False

    lc = local_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    rc = remote_conn.cursor()

    inserts = deletes = errors = 0

    try:
        # Colonnes de la table (depuis le distant)
        rc.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        cols = [r[0] for r in rc.fetchall()]
        if not cols:
            warn(f"Table '{table}' introuvable sur le distant.")
            return (0, 0, 1)

        # Lire les lignes locales
        lc.execute(f"SELECT {', '.join(cols)} FROM {table}")
        rows = lc.fetchall()
        info(f"  {len(rows)} enregistrement(s) à synchroniser dans '{table}'")

        if not rows:
            # Rien à synchroniser, vider le distant
            if not dry_run:
                rc.execute(f"DELETE FROM {table}")
                remote_conn.commit()
            return (0, 0, 0)

        # Identifier les valeurs de FK présentes en local
        fk_values = list({row[fk_col] for row in rows if row[fk_col] is not None})

        if dry_run:
            info(f"  [DRY-RUN] DELETE sur '{table}' WHERE {fk_col} IN ({fk_values})")
            info(f"  [DRY-RUN] INSERT de {len(rows)} lignes dans '{table}'.")
            return (len(rows), len(fk_values), 0)

        # DELETE par FK
        if fk_values:
            placeholders = ", ".join(["%s"] * len(fk_values))
            rc.execute(f"DELETE FROM {table} WHERE {fk_col} IN ({placeholders})", fk_values)
            deletes = rc.rowcount

        # INSERT
        col_list    = ", ".join(cols)
        placeholder = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholder})"

        for row in rows:
            values = [row[c] for c in cols]
            try:
                rc.execute(sql, values)
                inserts += 1
            except Exception as e:
                errors += 1
                warn(f"  Erreur INSERT dans {table} : {e}")
                remote_conn.rollback()
                remote_conn.autocommit = False

        remote_conn.commit()

    finally:
        lc.close(); local_conn.close()
        rc.close(); remote_conn.close()

    return (inserts, deletes, errors)


def reset_sequences_remote():
    """
    Remet à jour les séquences PostgreSQL sur le distant
    pour éviter les conflits d'ID après import.
    """
    # Tables de config dont les séquences peuvent avoir drifté
    tables_with_serial = [
        "clients", "enqueteurs", "tarifs_eos",
        "import_profiles", "import_field_mappings",
        "tarifs_client", "tarifs_enqueteur",
        "confirmation_options", "partner_request_keywords", "partner_tarif_rules",
    ]
    with db_cursor("remote") as cur:
        for tbl in tables_with_serial:
            try:
                cur.execute(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{tbl}', 'id'),
                        COALESCE((SELECT MAX(id) FROM {tbl}), 1),
                        true
                    )
                """)
            except Exception as e:
                # La table peut ne pas avoir de séquence (UUID, etc.)
                pass
    ok("Séquences des tables de configuration remises à jour.")


# ─────────────────────────────────────────────────────────────────────────────
# VÉRIFICATION FINALE
# ─────────────────────────────────────────────────────────────────────────────

def verify_sync():
    """Compare les comptages entre local et distant pour les tables de config."""
    results = []

    with db_cursor("local") as lc, db_cursor("remote") as rc:
        for tbl_cfg in CONFIG_TABLES:
            tbl = tbl_cfg["table"]
            try:
                lc.execute(f"SELECT COUNT(*) FROM {tbl}")
                local_count = lc.fetchone()[0]
            except Exception:
                local_count = "erreur"

            try:
                rc.execute(f"SELECT COUNT(*) FROM {tbl}")
                remote_count = rc.fetchone()[0]
            except Exception:
                remote_count = "erreur"

            status = "OK" if local_count == remote_count else "DIFF"
            results.append((tbl, local_count, remote_count, status))

    print()
    try:
        from tabulate import tabulate
        print(tabulate(
            results,
            headers=["Table", "Local", "Distant", "Statut"],
            tablefmt="simple",
        ))
    except ImportError:
        print(f"  {'Table':<40} {'Local':>8} {'Distant':>8} {'Statut':>8}")
        print("  " + "-" * 66)
        for row in results:
            color = GREEN if row[3] == "OK" else RED
            print(f"  {row[0]:<40} {str(row[1]):>8} {str(row[2]):>8} {color}{row[3]:>8}{RESET}")


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Configure la base de données distante EOS depuis la base locale.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Exemples :
              python CONFIGURER_BASE_DISTANTE.py
              python CONFIGURER_BASE_DISTANTE.py --dry-run
              python CONFIGURER_BASE_DISTANTE.py --skip-migrations
              python CONFIGURER_BASE_DISTANTE.py --skip-sync
        """),
    )
    parser.add_argument("--dry-run",          action="store_true",
                        help="Simule sans modifier la BDD distante")
    parser.add_argument("--skip-migrations",  action="store_true",
                        help="Ne pas appliquer les migrations Alembic")
    parser.add_argument("--skip-sync",        action="store_true",
                        help="Ne pas synchroniser les tables de config")
    args = parser.parse_args()

    # ── Vérification psycopg2 ─────────────────────────────────────────────────
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        fail("psycopg2 non installé.")
        print("  Lance : pip install psycopg2-binary")
        sys.exit(1)

    header("CONFIGURATION BASE DE DONNEES EOS - ORDINATEUR DISTANT")
    print(f"  Démarré le  : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Mode dry-run: {'OUI (aucune écriture)' if args.dry_run else 'NON (écriture activée)'}")

    # =========================================================================
    # ETAPE 1 : Connexion locale
    # =========================================================================
    step(1, "CONNEXION À LA BASE LOCALE")
    try:
        with db_cursor("local") as cur:
            cur.execute("SELECT version()")
            v = cur.fetchone()[0].split(",")[0]
            ok(f"Connecté à la BDD locale : {v}")
    except Exception as e:
        fail(f"Impossible de se connecter à la BDD locale : {e}")
        sys.exit(1)

    # =========================================================================
    # ETAPE 2 : Analyse du schéma local
    # =========================================================================
    step(2, "ANALYSE DU SCHÉMA LOCAL")
    info("Lecture de la structure complète de la BDD locale...")
    local_schema = analyze_schema("local")
    ok(f"Tables trouvées   : {len(local_schema['tables'])}")
    ok(f"Séquences         : {len(local_schema['sequences'])}")
    ok(f"Version Alembic   : {local_schema['alembic'] or 'table alembic_version absente'}")

    # Afficher les tables de config détectées
    print()
    info("Tables de configuration à synchroniser :")
    for tbl_cfg in CONFIG_TABLES:
        tbl = tbl_cfg["table"]
        if tbl in local_schema["tables"]:
            ncols = len(local_schema["tables"][tbl])
            with db_cursor("local") as cur:
                cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                nrows = cur.fetchone()[0]
            print(f"    {GREEN}[v]{RESET} {tbl:<40} {ncols:>3} colonnes  {nrows:>6} lignes")
        else:
            print(f"    {RED}[x]{RESET} {tbl:<40} table absente !")

    # =========================================================================
    # ETAPE 3 : Tunnel SSH + connexion distante
    # =========================================================================
    step(3, "CONNEXION AU POSTE DISTANT (TUNNEL SSH)")
    start_ssh_tunnel()

    try:
        with db_cursor("remote") as cur:
            cur.execute("SELECT version()")
            v = cur.fetchone()[0].split(",")[0]
            ok(f"Connecté à la BDD distante via tunnel : {v}")
    except Exception as e:
        fail(f"Impossible de se connecter à la BDD distante via tunnel : {e}")
        stop_ssh_tunnel()
        sys.exit(1)

    # =========================================================================
    # ETAPE 4 : Analyse du schéma distant
    # =========================================================================
    step(4, "ANALYSE DU SCHÉMA DISTANT")
    info("Lecture de la structure complète de la BDD distante...")
    try:
        remote_schema = analyze_schema("remote")
        ok(f"Tables trouvées   : {len(remote_schema['tables'])}")
        ok(f"Version Alembic   : {remote_schema['alembic'] or 'inconnue (BDD peut-être vide)'}")
    except Exception as e:
        fail(f"Erreur lecture schéma distant : {e}")
        stop_ssh_tunnel()
        sys.exit(1)

    # =========================================================================
    # ETAPE 5 : Comparaison des schémas
    # =========================================================================
    step(5, "COMPARAISON LOCAL vs DISTANT")
    report = compare_schemas(local_schema, remote_schema)
    print_schema_report(local_schema, remote_schema, report)

    # =========================================================================
    # ETAPE 6 : Migrations Alembic
    # =========================================================================
    step(6, "MIGRATIONS ALEMBIC SUR LE DISTANT")

    if args.skip_migrations:
        warn("Migrations ignorées (--skip-migrations).")
    elif local_schema["alembic"] == remote_schema["alembic"] and report["ok"]:
        ok("Schémas déjà synchronisés, aucune migration nécessaire.")
    else:
        if local_schema["alembic"] != remote_schema["alembic"]:
            warn(f"Version locale   : {local_schema['alembic']}")
            warn(f"Version distante : {remote_schema['alembic']}")
            warn("Des migrations doivent être appliquées.")

        migration_ok = run_alembic_remote(dry_run=args.dry_run)
        if not migration_ok:
            fail("Les migrations ont échoué. La synchronisation des données est risquée.")
            answer = input("  Continuer quand même ? (oui/non) : ").strip().lower()
            if answer != "oui":
                stop_ssh_tunnel()
                sys.exit(1)

        # Ré-analyser le schéma distant après migrations
        if not args.dry_run:
            info("Re-lecture du schéma distant après migrations...")
            remote_schema = analyze_schema("remote")
            report2 = compare_schemas(local_schema, remote_schema)
            if report2["ok"]:
                ok("Schémas identiques après migrations.")
            else:
                warn("Des différences persistent après migrations :")
                print_schema_report(local_schema, remote_schema, report2)

    # =========================================================================
    # ETAPE 7 : Synchronisation des tables de configuration
    # =========================================================================
    step(7, "SYNCHRONISATION DES TABLES DE CONFIGURATION")

    if args.skip_sync:
        warn("Synchronisation ignorée (--skip-sync).")
    else:
        sync_results = []

        for tbl_cfg in CONFIG_TABLES:
            tbl   = tbl_cfg["table"]
            label = tbl_cfg["label"]
            print(f"\n  {CYAN}>> {label} ({tbl}){RESET}")

            if tbl not in local_schema["tables"]:
                warn(f"  Table absente en local, ignorée.")
                sync_results.append((tbl, 0, 0, "IGNORE"))
                continue

            conflict_key = tbl_cfg.get("conflict_key")
            fk_col       = tbl_cfg.get("fk_col")

            try:
                if conflict_key:
                    ins, upd, err = sync_table_upsert(tbl, conflict_key, dry_run=args.dry_run)
                    ok(f"  Résultat : {ins} upserts, {err} erreurs")
                    sync_results.append((tbl, ins, err, "UPSERT"))
                else:
                    ins, dels, err = sync_table_delete_insert(tbl, fk_col, dry_run=args.dry_run)
                    ok(f"  Résultat : {dels} supprimés, {ins} insérés, {err} erreurs")
                    sync_results.append((tbl, ins, err, "DELETE+INSERT"))
            except Exception as e:
                fail(f"  Erreur sur '{tbl}' : {e}")
                sync_results.append((tbl, 0, 1, "ERREUR"))

        # Remettre à jour les séquences
        if not args.dry_run:
            print()
            info("Remise à jour des séquences PostgreSQL...")
            reset_sequences_remote()

    # =========================================================================
    # ETAPE 8 : Vérification finale
    # =========================================================================
    step(8, "VERIFICATION FINALE - COMPTAGES")
    try:
        verify_sync()
    except Exception as e:
        warn(f"Impossible d'afficher les comptages : {e}")

    # ── Fermeture du tunnel ───────────────────────────────────────────────────
    stop_ssh_tunnel()

    # ── Résumé ────────────────────────────────────────────────────────────────
    print(f"\n{GREEN}{'='*70}")
    print(f"  SYNCHRONISATION TERMINEE  --  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*70}{RESET}")
    print()
    ok("Le poste distant est maintenant configuré.")
    ok("Lance EOS sur le distant avec DEMARRER_EOS_SIMPLE.bat")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        warn("Interrompu par l'utilisateur.")
        stop_ssh_tunnel()
        sys.exit(0)
    except Exception as e:
        fail(f"Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        stop_ssh_tunnel()
        sys.exit(1)
