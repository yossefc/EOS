
import os
import sys
import json

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.models import Donnee
from models.client import Client
from models.export_batch import ExportBatch

app = create_app()

with app.app_context():
    partner = Client.query.filter_by(code='PARTNER').first()
    
    # Get the 3 exported inquiries
    exported_enquetes = Donnee.query.filter_by(
        client_id=partner.id, 
        statut_validation='validee', 
        exported=True
    ).all()
    exported_ids = [e.id for e in exported_enquetes]
    print(f"Exported PARTNER IDs: {exported_ids}")
    
    # Get Batch 28
    batch = db.session.get(ExportBatch, 28)
    if not batch:
        print("Batch 28 not found.")
    else:
        batch_ids = batch.get_enquete_ids_list()
        print(f"IDs in Batch 28: {batch_ids}")
        
        # Check intersection
        found = [eid for eid in exported_ids if eid in batch_ids]
        missing = [eid for eid in exported_ids if eid not in batch_ids]
        
        print(f"\nFound in Batch 28: {len(found)}")
        print(f"NOT in any PARTNER Batch: {len(missing)}")
        
        if missing:
            print(f"IDs missing from Batch 28: {missing}")
            # Fix missing ones
            # Donnee.query.filter(Donnee.id.in_(missing)).update({Donnee.exported: False}, synchronize_session=False)
            # db.session.commit()
            # print(f"Reset 'exported' status for {len(missing)} inquiries.")
