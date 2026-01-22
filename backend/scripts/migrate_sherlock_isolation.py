import os
import sys
import sqlalchemy as sa
from sqlalchemy import text

# Définir DATABASE_URL AVANT tout import
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

# Importer l'application Flask pour le contexte
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from extensions import db

def apply_isolation_migration():
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        try:
            print("🚀 Début de la migration d'isolation Sherlock...")
            
            # 1. Création de la table sherlock_donnees SI elle n'existe pas
            print("  → Création de la table 'sherlock_donnees'...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sherlock_donnees (
                    id SERIAL PRIMARY KEY,
                    fichier_id INTEGER REFERENCES fichiers(id),
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    dossier_id VARCHAR(50),
                    reference_interne VARCHAR(50),
                    demande VARCHAR(100),
                    ec_civilite VARCHAR(10),
                    ec_prenom VARCHAR(100),
                    ec_prenom2 VARCHAR(100),
                    ec_prenom3 VARCHAR(100),
                    ec_prenom4 VARCHAR(100),
                    ec_nom_usage VARCHAR(100),
                    ec_nom_naissance VARCHAR(100),
                    ec_date_naissance VARCHAR(20),
                    naissance_cp VARCHAR(10),
                    ec_localite_naissance VARCHAR(100),
                    naissance_insee VARCHAR(10),
                    ec_pays_naissance VARCHAR(100),
                    client_commentaire TEXT,
                    ad_l1 VARCHAR(100),
                    ad_l2 VARCHAR(100),
                    ad_l3 VARCHAR(100),
                    ad_l4_numero VARCHAR(10),
                    ad_l4_type VARCHAR(50),
                    ad_l4_voie VARCHAR(100),
                    ad_l5 VARCHAR(100),
                    ad_l6_cedex VARCHAR(10),
                    ad_l6_cp VARCHAR(10),
                    ad_l6_insee VARCHAR(10),
                    ad_l6_localite VARCHAR(100),
                    ad_l7_pays VARCHAR(100),
                    ad_telephone VARCHAR(20),
                    ad_telephone_pro VARCHAR(20),
                    ad_telephone_mobile VARCHAR(20),
                    ad_email VARCHAR(255),
                    tarif_a VARCHAR(50),
                    tarif_at VARCHAR(50),
                    tarif_dcd VARCHAR(50),
                    resultat VARCHAR(50),
                    montant_ht FLOAT,
                    rep_ec_civilite VARCHAR(10),
                    rep_ec_prenom VARCHAR(100),
                    rep_ec_prenom2 VARCHAR(100),
                    rep_ec_prenom3 VARCHAR(100),
                    rep_ec_prenom4 VARCHAR(100),
                    rep_ec_nom_usage VARCHAR(100),
                    rep_ec_nom_naissance VARCHAR(100),
                    rep_ec_date_naissance VARCHAR(20),
                    rep_naissance_cp VARCHAR(10),
                    rep_ec_localite_naissance VARCHAR(100),
                    rep_naissance_insee VARCHAR(10),
                    rep_ec_pays_naissance VARCHAR(100),
                    rep_dcd_date VARCHAR(20),
                    rep_dcd_numero_acte VARCHAR(50),
                    rep_dcd_localite VARCHAR(100),
                    rep_dcd_cp VARCHAR(10),
                    rep_dcd_insee VARCHAR(10),
                    rep_dcd_pays VARCHAR(100),
                    rep_ad_l1 VARCHAR(100),
                    rep_ad_l2 VARCHAR(100),
                    rep_ad_l3 VARCHAR(100),
                    rep_ad_l4_numero VARCHAR(10),
                    rep_ad_l4_type VARCHAR(50),
                    rep_ad_l4_voie VARCHAR(100),
                    rep_ad_l5 VARCHAR(100),
                    rep_ad_l6_cedex VARCHAR(10),
                    rep_ad_l6_cp VARCHAR(10),
                    rep_ad_l6_insee VARCHAR(10),
                    rep_ad_l6_localite VARCHAR(100),
                    rep_ad_l7_pays VARCHAR(100),
                    rep_ad_telephone VARCHAR(20)
                )
            """))

            # 2. Suppression des données Sherlock de la table donnees
            print("  → Nettoyage des données Sherlock dans 'donnees'...")
            conn.execute(text("DELETE FROM donnees WHERE client_id IN (SELECT id FROM clients WHERE code = 'RG_SHERLOCK')"))

            # 3. Restauration des tailles de colonnes dans la table donnees
            print("  → Restauration des tailles de colonnes dans 'donnees'...")
            columns_revert = [
                ("numeroDossier", "VARCHAR(10)"),
                ("referenceDossier", "VARCHAR(15)"),
                ("numeroInterlocuteur", "VARCHAR(12)"),
                ("guidInterlocuteur", "VARCHAR(36)"),
                ("typeDemande", "VARCHAR(3)"),
                ("numeroDemande", "VARCHAR(11)"),
                ("numeroDemandeContestee", "VARCHAR(11)"),
                ("numeroDemandeInitiale", "VARCHAR(11)")
            ]
            
            for col_name, old_type in columns_revert:
                print(f"    - {col_name} → {old_type}")
                # Note: On tronque si nécessaire pour revenir à la taille d'origine
                sql = f'ALTER TABLE donnees ALTER COLUMN "{col_name}" TYPE {old_type} USING LEFT("{col_name}", {old_type[8:-1]})'
                conn.execute(text(sql))
            
            trans.commit()
            print("✅ Migration d'isolation Sherlock terminée avec succès.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Erreur lors de la migration : {e}")
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    apply_isolation_migration()
