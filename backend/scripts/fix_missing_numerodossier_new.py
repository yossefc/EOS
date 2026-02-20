#!/usr/bin/env python3
"""
Assigne des numeroDossier aux contestations qui n'en ont pas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Utiliser le même mot de passe que le serveur Flask
db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:Minoria2121@localhost:5432/eos_db')
os.environ['DATABASE_URL'] = db_url

from models import db, Donnee
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Trouver toutes les contestations SANS numeroDossier
    contestations_sans_numero = Donnee.query.filter(
        Donnee.est_contestation == True,
        db.or_(
            Donnee.numeroDossier == None,
            Donnee.numeroDossier == '',
            Donnee.numeroDossier == 'None'
        )
    ).all()
    
    print(f"\n=== Contestations sans numeroDossier : {len(contestations_sans_numero)} ===\n")
    
    if not contestations_sans_numero:
        print("✓ Toutes les contestations ont un numeroDossier")
        sys.exit(0)
    
    for contestation in contestations_sans_numero:
        # Assigner CON-{ID}
        nouveau_numero = f"CON-{contestation.id}"
        ancien = contestation.numeroDossier
        contestation.numeroDossier = nouveau_numero
        
        print(f"ID {contestation.id} ({contestation.nom} {contestation.prenom}): '{ancien}' → '{nouveau_numero}'")
    
    # Sauvegarder
    db.session.commit()
    
    print(f"\n✓ {len(contestations_sans_numero)} numeroDossier assignés avec succès !")
