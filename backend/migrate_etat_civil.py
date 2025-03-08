from flask import Flask
from extensions import db
import logging
import os
from sqlalchemy import text, inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_etat_civil_fields():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            logger.info("Vérification des colonnes existantes pour la table donnees_enqueteur...")
            
            # Utiliser l'inspecteur SQLAlchemy
            inspector = inspect(db.engine)
            
            # Vérifier si la table existe
            if 'donnees_enqueteur' not in inspector.get_table_names():
                logger.error("La table donnees_enqueteur n'existe pas encore!")
                return
                
            # Récupérer les colonnes existantes
            columns = inspector.get_columns('donnees_enqueteur')
            existing_columns = [column['name'] for column in columns]
            
            logger.info(f"Colonnes existantes: {existing_columns}")
            
            columns_to_add = [
                "qualite_corrigee VARCHAR(10)",
                "nom_corrige VARCHAR(30)",
                "prenom_corrige VARCHAR(20)",
                "nom_patronymique_corrige VARCHAR(30)",
                "date_naissance_corrigee DATE",
                "lieu_naissance_corrige VARCHAR(50)",
                "code_postal_naissance_corrige VARCHAR(10)",
                "pays_naissance_corrige VARCHAR(32)",
                "type_divergence VARCHAR(20)"
            ]
            
            # Ajouter chaque colonne si elle n'existe pas déjà
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                if column_name not in existing_columns:
                    logger.info(f"Ajout de la colonne {column_name}...")
                    alter_query = f"ALTER TABLE donnees_enqueteur ADD COLUMN {column_def}"
                    db.session.execute(text(alter_query))
                else:
                    logger.info(f"La colonne {column_name} existe déjà.")
            
            db.session.commit()
            logger.info("Migration terminée avec succès!")
            
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_etat_civil_fields()