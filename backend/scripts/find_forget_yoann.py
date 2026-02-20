#!/usr/bin/env python3
"""
Chercher FORGET YOANN dans la table donnees
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:Minoria2121@localhost:5432/eos_db')

from models import db, Donnee
from models.enqueteur import Enqueteur
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("\n=== Recherche FORGET YOANN dans la base ===\n")
    
    # Chercher toutes les enquêtes avec FORGET ou YOANN
    enquetes = Donnee.query.filter(
        db.or_(
            Donnee.nom.ilike('%FORGET%'),
            Donnee.prenom.ilike('%YOANN%'),
            Donnee.nom.ilike('%YOANN%')
        )
    ).order_by(Donnee.id.desc()).all()
    
    print(f"Trouvé {len(enquetes)} résultat(s):\n")
    
    for enq in enquetes:
        print(f"ID: {enq.id}")
        print(f"  Numéro dossier: {enq.numeroDossier}")
        print(f"  Nom: {enq.nom}")
        print(f"  Prénom: {enq.prenom}")
        print(f"  Type: {enq.typeDemande}")
        print(f"  Est contestation: {enq.est_contestation}")
        print(f"  Enquêteur ID: {enq.enqueteurId}")
        
        # Récupérer le nom de l'enquêteur
        if enq.enqueteurId:
            enqueteur = Enqueteur.query.get(enq.enqueteurId)
            if enqueteur:
                print(f"  Enquêteur: {enqueteur.prenom} {enqueteur.nom}")
        else:
            print(f"  Enquêteur: Non assigné")
        
        print(f"  Statut: {enq.statut_validation}")
        print(f"  Client ID: {enq.client_id}")
        print(f"  Adresse: {enq.adresse1 or '-'}")
        print(f"  Ville: {enq.ville or '-'}")
        
        # Si c'est une contestation, chercher l'enquête originale
        if enq.est_contestation and enq.enquete_originale_id:
            original = Donnee.query.get(enq.enquete_originale_id)
            if original:
                print(f"  ⚠️ Enquête originale: ID {original.id}, Dossier {original.numeroDossier}")
                if original.enqueteurId:
                    enq_orig = Enqueteur.query.get(original.enqueteurId)
                    if enq_orig:
                        print(f"     Enquêteur original: {enq_orig.prenom} {enq_orig.nom}")
                else:
                    print(f"     Enquêteur original: Non assigné")
        
        print()
