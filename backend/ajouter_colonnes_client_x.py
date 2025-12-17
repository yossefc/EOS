"""
Script pour ajouter les colonnes spécifiques à CLIENT_X dans PostgreSQL
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         Ajout des colonnes CLIENT_X (PostgreSQL)              ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Étape 1 : Créer la table tarifs_client si elle n'existe pas
            print("► Vérification de la table 'tarifs_client'...")
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_name = 'tarifs_client'
            """))
            
            if result.fetchone():
                print("  ⏭️  Table 'tarifs_client' déjà existante (ignorée)\n")
            else:
                print("  ✅ Création de la table 'tarifs_client'...")
                db.create_all()  # Créer toutes les tables manquantes
                print("  ✅ Table 'tarifs_client' créée avec succès\n")
            
            # Étape 2 : Vérifier si les colonnes existent déjà
            print("► Vérification des colonnes CLIENT_X dans 'donnees'...")
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = 'donnees'
                  AND column_name IN ('tarif_lettre', 'recherche', 'date_jour', 'nom_complet', 'motif')
                ORDER BY column_name
            """))
            
            existing_columns = [row[0] for row in result]
            print(f"  Colonnes existantes : {existing_columns if existing_columns else 'aucune'}\n")
            
            # Liste des colonnes à ajouter
            # Format: (nom_colonne, type_sql, description)
            colonnes_a_ajouter = [
                ('tarif_lettre', 'VARCHAR(10)', 'Code lettre du tarif CLIENT_X (A, B, C, etc.)'),
                ('recherche', 'VARCHAR(255)', 'Éléments retrouvés par CLIENT_X'),
                ('date_jour', 'DATE', 'Date du jour pour les contestations CLIENT_X'),
                ('nom_complet', 'VARCHAR(255)', 'Nom complet pour les contestations CLIENT_X'),
                ('motif', 'VARCHAR(500)', 'Motif de la contestation CLIENT_X'),
            ]
            
            print("► Ajout des colonnes dans la table 'donnees'...\n")
            
            nb_ajoutees = 0
            nb_existantes = 0
            
            for colonne, type_sql, description in colonnes_a_ajouter:
                try:
                    if colonne in existing_columns:
                        print(f"  ⏭️  {colonne:20s} → déjà existante (ignorée)")
                        nb_existantes += 1
                    else:
                        sql = f'ALTER TABLE donnees ADD COLUMN {colonne} {type_sql};'
                        db.session.execute(text(sql))
                        db.session.commit()  # Commit après CHAQUE colonne réussie
                        print(f"  ✅ {colonne:20s} → {type_sql:15s} ajoutée")
                        print(f"      └─ {description}")
                        nb_ajoutees += 1
                except Exception as e:
                    db.session.rollback()  # Rollback en cas d'erreur pour continuer
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print(f"  ⏭️  {colonne:20s} → déjà existante (ignorée)")
                        nb_existantes += 1
                    else:
                        print(f"  ❌ {colonne:20s} → erreur: {e}")
                        raise
            
            print()
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║          ✅ Migration CLIENT_X terminée avec succès            ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            
            print(f"  • Colonnes ajoutées    : {nb_ajoutees}")
            print(f"  • Colonnes existantes  : {nb_existantes}")
            print()
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

