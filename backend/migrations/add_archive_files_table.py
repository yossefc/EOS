"""
Script de migration pour créer la table enquete_archive_files
Cette table stocke les informations des fichiers d'archives générés
"""
import sys
import os
import sqlite3

# Chemin vers la base de données
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'eos.db')

def migrate():
    """Crée la table enquete_archive_files"""
    try:
        # Connexion directe à SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Créer la table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enquete_archive_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enquete_id INTEGER NOT NULL UNIQUE,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(500) NOT NULL,
                type_export VARCHAR(20) NOT NULL DEFAULT 'word',
                file_size INTEGER,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                utilisateur VARCHAR(100),
                FOREIGN KEY (enquete_id) REFERENCES donnees(id)
            )
        """)
        
        # Créer un index sur enquete_id pour améliorer les performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_archive_files_enquete_id 
            ON enquete_archive_files(enquete_id)
        """)
        
        # Créer un index sur created_at pour le tri
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_archive_files_created_at 
            ON enquete_archive_files(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
        
        print("✓ Table enquete_archive_files créée avec succès")
        print("✓ Index créés avec succès")
        
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {str(e)}")
        raise

if __name__ == '__main__':
    migrate()
