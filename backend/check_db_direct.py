
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'eos.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- CLIENTS ---")
cursor.execute("SELECT id, code, nom FROM client")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Code: '{row[1]}', Nom: '{row[2]}'")

print("\n--- STATS DONNEE (VALIDEES) ---")
cursor.execute("SELECT client_id, COUNT(*) FROM donnees WHERE statut_validation = 'validee' GROUP BY client_id")
for row in cursor.fetchall():
    print(f"Client ID: {row[0]}, Count: {row[1]}")

print("\n--- CHECK PARTNER VALIDEES CODES ---")
cursor.execute("""
    SELECT de.code_resultat, COUNT(*) 
    FROM donnees d
    JOIN donnees_enqueteur de ON d.id = de.donnee_id
    WHERE d.client_id = (SELECT id FROM client WHERE code = 'PARTNER')
    AND d.statut_validation = 'validee'
    GROUP BY de.code_resultat
""")
for row in cursor.fetchall():
    print(f"Code: '{row[0]}', Count: {row[1]}")

conn.close()
