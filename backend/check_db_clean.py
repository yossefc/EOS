import sqlite3
import sys

try:
    conn = sqlite3.connect('instance/eos.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(donnees)')
    cols = [row[1] for row in cursor.fetchall()]
    
    print(f"Total colonnes: {len(cols)}")
    
    export_cols = [c for c in cols if 'export' in c.lower()]
    if export_cols:
        print(f"ERREUR: Colonnes 'export' trouvées: {export_cols}")
        sys.exit(1)
    else:
        print("OK: Base de données propre")
        sys.exit(0)
    
    conn.close()
except Exception as e:
    print(f"ERREUR: {e}")
    sys.exit(1)

