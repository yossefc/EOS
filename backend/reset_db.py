import os
from flask import Flask
from extensions import db
# Importer explicitement tous les modèles
import models.models
import models.models_enqueteur
import models.enqueteur
import models.tarifs

def reset_db():
    # Créer l'application Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialiser la base de données
    db.init_app(app)
    
    with app.app_context():
        # Supprimer toutes les tables si elles existent
        db.drop_all()
        
        # Créer de nouvelles tables
        db.create_all()
        
        print("Base de données réinitialisée avec succès!")

if __name__ == "__main__":
    reset_db()