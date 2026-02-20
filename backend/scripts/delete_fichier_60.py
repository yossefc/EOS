#!/usr/bin/env python3
"""
Script pour supprimer le fichier ID 60 et toutes ses données associées
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Minoria2121@localhost:5432/eos_db')

from models import db, Fichier, Donnee
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Chercher le fichier ID 60
    fichier = Fichier.query.get(60)
    
    if not fichier:
        print("✗ Fichier ID 60 n'existe pas dans la base de données")
        sys.exit(0)
    
    print(f"\n=== Fichier trouvé ===")
    print(f"ID: {fichier.id}")
    print(f"Nom: {fichier.nom}")
    print(f"Client ID: {fichier.client_id}")
    print(f"Date upload: {fichier.date_upload}")
    
    # Compter les données associées
    count_donnees = Donnee.query.filter_by(fichier_id=60).count()
    print(f"Nombre de données associées: {count_donnees}")
    
    if count_donnees > 0:
        print(f"\n⚠️  ATTENTION: Ce fichier a encore {count_donnees} données associées !")
        reponse = input("Voulez-vous supprimer le fichier ET toutes ses données ? (o/n): ")
        if reponse.lower() != 'o':
            print("Opération annulée.")
            sys.exit(0)
        
        # Supprimer les données
        Donnee.query.filter_by(fichier_id=60).delete()
        print(f"✓ {count_donnees} données supprimées")
    
    # Supprimer le fichier
    db.session.delete(fichier)
    db.session.commit()
    
    print(f"✓ Fichier ID 60 supprimé avec succès !")
    print("\nVous pouvez maintenant réimporter votre fichier de contestations.")
