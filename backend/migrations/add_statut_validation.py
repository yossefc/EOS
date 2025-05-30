"""
Script de migration pour ajouter le champ statut_validation à la table donnees
"""

import sqlite3
import os
from datetime import datetime

def migrate_add_statut_validation():
    """Ajoute la colonne statut_validation à la table donnees"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'eos.db')
    
    if not os.path.exists(db_path):
        print(f"Base de données non trouvée à: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(donnees)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'statut_validation' in columns:
            print("La colonne statut_validation existe déjà.")
            conn.close()
            return True
        
        # Ajouter la colonne statut_validation
        cursor.execute("""
            ALTER TABLE donnees 
            ADD COLUMN statut_validation VARCHAR(20) DEFAULT 'en_attente' NOT NULL
        """)
        
        # Mettre à jour toutes les enquêtes existantes avec des résultats à "en_attente"
        cursor.execute("""
            UPDATE donnees 
            SET statut_validation = 'en_attente' 
            WHERE id IN (
                SELECT d.id 
                FROM donnees d 
                JOIN donnees_enqueteur de ON d.id = de.donnee_id 
                WHERE de.code_resultat IS NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"Migration réussie: colonne statut_validation ajoutée à la table donnees")
        print(f"Enquêtes avec résultats mises à jour vers 'en_attente'")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la migration: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    migrate_add_statut_validation()
