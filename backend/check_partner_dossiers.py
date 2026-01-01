
import os
import sys

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        print("PARTNER client not found")
        sys.exit(1)
    
    print(f"Partner ID: {partner.id}")
    
    # Check all validee dossiers for partner
    validees = Donnee.query.filter_by(client_id=partner.id, statut_validation='validee').all()
    print(f"Total validee dossiers for Partner: {len(validees)}")
    
    for d in validees:
        de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
        if de:
            print(f"Dossier {d.numeroDossier}: exported={d.exported}, code_resultat={de.code_resultat}, est_contestation={d.est_contestation}")
        else:
            print(f"Dossier {d.numeroDossier}: NO DonneeEnqueteur entry!")

    # Check non-validee but confirmed
    confirmees = Donnee.query.filter_by(client_id=partner.id, statut_validation='confirmee').all()
    print(f"Total confirmee (pending validation) dossiers for Partner: {len(confirmees)}")
