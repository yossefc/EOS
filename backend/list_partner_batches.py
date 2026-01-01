
import os
import sys

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.client import Client
from models.export_batch import ExportBatch

app = create_app()

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        print("PARTNER client not found")
        sys.exit(1)
    
    batches = ExportBatch.query.filter_by(client_id=partner.id).all()
    print(f"--- PARTNER BATCHES (ID: {partner.id}) ---")
    for b in batches:
        print(f"ID: {b.id} | Filename: {b.filename} | Date: {b.created_at}")
