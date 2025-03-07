from flask import Flask
from models.enqueteur import Enqueteur
from extensions import db
import os

def init_database():
    # Configuration de l'application Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation de la base de données
    db.init_app(app)
    
    with app.app_context():
        # Suppression de la base existante si elle existe
        if os.path.exists('eos.db'):
            os.remove('eos.db')
            
        # Création des tables
        db.create_all()
        print("Base de données initialisée avec succès!")

if __name__ == '__main__':
    init_database()