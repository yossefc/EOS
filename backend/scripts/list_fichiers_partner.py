#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:admin@localhost:5432/eos_db')

from models import db, Fichier, Donnee
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Lister tous les fichiers pour PARTNER (client_id=11)
    fichiers = Fichier.query.filter_by(client_id=11).order_by(Fichier.date_upload.desc()).all()
    
    print(f"\n=== Fichiers PARTNER (client_id=11) : {len(fichiers)} fichier(s) ===\n")
    
    for f in fichiers:
        # Compter combien de donnees sont liées à ce fichier
        count_donnees = Donnee.query.filter_by(fichier_id=f.id).count()
        
        print(f"ID: {f.id}")
        print(f"  Nom: {f.nom}")
        print(f"  Date upload: {f.date_upload}")
        print(f"  Nombre de données: {count_donnees}")
        print()
