
import os
import sys

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
    if not partner:
        print("PARTNER client not found")
        sys.exit(1)
    
    print(f"Checking PARTNER (ID: {partner.id})")
    
    # 1. Total validee but NOT exported (Should be visible in Exporter)
    visible = Donnee.query.filter_by(
        client_id=partner.id, 
        statut_validation='validee', 
        exported=False
    ).count()
    print(f"Validated and NOT exported (VISIBLE in exporter): {visible}")
    
    # 2. Total validee AND exported (Should be HIDDEN in Exporter)
    hidden = Donnee.query.filter_by(
        client_id=partner.id, 
        statut_validation='validee', 
        exported=True
    ).count()
    print(f"Validated and ALREADY exported (HIDDEN in exporter): {hidden}")
    
    # 3. Check for PARTNER batches
    batches = ExportBatch.query.filter_by(client_id=partner.id).count()
    print(f"Total Export Batches for PARTNER: {batches}")
    
    # 4. If there are hidden ones but NO batches, it confirms the bug happened
    if hidden > 0 and batches == 0:
        print("\n[!] BUG CONFIRMED: Found hidden inquiries but no PARTNER batches exist.")
        print("These were likely marked as exported by the global EOS tool.")
        
        # Suggest fixing them
        print("Resetting exported status for these inquiries to make them visible again...")
        count = Donnee.query.filter_by(
            client_id=partner.id, 
            statut_validation='validee', 
            exported=True
        ).update({Donnee.exported: False})
        db.session.commit()
        print(f"Fixed {count} inquiries. They should now be visible in the exporter.")
    else:
        print("\nNo visible discrepancy found or batches already exist.")
