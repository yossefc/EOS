import os
import sys
import psycopg2

# Configuration
DATABASE_URL = "postgresql://eos_user:eos_password@localhost:5432/eos_db"

def repair():
    print("=== RÉPARATION DES DONNÉES EOS ===")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. Vérifier si les tables existent
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables trouvées : {', '.join(tables)}")
        
        if 'donnees' not in tables:
            print("❌ Erreur : La table 'donnees' n'existe pas. La base est peut-être vide.")
            return

        # 2. Compter le nombre total de données
        cur.execute("SELECT COUNT(*) FROM donnees")
        total = cur.fetchone()[0]
        print(f"Nombre total de lignes dans 'donnees' : {total}")
        
        # 3. Vérifier les client_id NULL
        cur.execute("SELECT COUNT(*) FROM donnees WHERE client_id IS NULL")
        null_clients = cur.fetchone()[0]
        print(f"Lignes avec client_id manquant (cachées) : {null_clients}")
        
        if null_clients > 0:
            print(f"► Réparation de {null_clients} lignes...")
            # S'assurer que le client EOS (ID 1) existe
            cur.execute("SELECT id FROM clients WHERE code = 'EOS'")
            client_eos = cur.fetchone()
            if not client_eos:
                print("► Création du client EOS...")
                cur.execute("INSERT INTO clients (id, code, nom, actif) VALUES (1, 'EOS', 'EOS France', true) ON CONFLICT DO NOTHING")
                client_id = 1
            else:
                client_id = client_eos[0]
            
            cur.execute("UPDATE donnees SET client_id = %s WHERE client_id IS NULL", (client_id,))
            cur.execute("UPDATE fichiers SET client_id = %s WHERE client_id IS NULL", (client_id,))
            cur.execute("UPDATE donnees_enqueteur SET client_id = %s WHERE client_id IS NULL", (client_id,))
            conn.commit()
            print("✅ Réparation terminée !")
        else:
            print("✅ Aucune donnée n'est cachée par le filtre client.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur lors de la réparation : {e}")

if __name__ == "__main__":
    repair()
