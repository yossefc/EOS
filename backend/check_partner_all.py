
import os
import sys

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.models import Donnee
from models.client import Client

app = create_app()

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        print("PARTNER client not found")
        sys.exit(1)
    
    print(f"PARTNER (ID: {partner.id})")
    
    from sqlalchemy import func
    stats = db.session.query(
        Donnee.statut_validation, 
        Donnee.exported, 
        func.count(Donnee.id)
    ).filter(Donnee.client_id == partner.id).group_by(Donnee.statut_validation, Donnee.exported).all()
    
    print("\nStatus Breakdown:")
    for status, exported, count in stats:
        print(f" - Status: {status}, Exported: {exported} -> Count: {count}")
    
    if not stats:
        print("No inquiries found for PARTNER.")
