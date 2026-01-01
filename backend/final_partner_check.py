
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
    
    print(f"--- PARTNER DATA CHECK (ID: {partner.id}) ---")
    
    # Check all statuses
    from sqlalchemy import func
    stats = db.session.query(
        Donnee.statut_validation, 
        Donnee.exported, 
        func.count(Donnee.id)
    ).filter(Donnee.client_id == partner.id).group_by(Donnee.statut_validation, Donnee.exported).all()
    
    for status, exported, count in stats:
        print(f"Status: {status:15} | Exported: {str(exported):5} | Count: {count}")

    # Check for batches
    batches = ExportBatch.query.filter_by(client_id=partner.id).count()
    print(f"Total Export Batches for PARTNER: {batches}")
    
    # FIX: If batches is 0, reset all exported for PARTNER
    if batches == 0:
        exported_count = Donnee.query.filter_by(client_id=partner.id, exported=True).count()
        if exported_count > 0:
            print(f"\n[!] Resetting {exported_count} PARTNER inquiries that were marked as exported without a PARTNER batch.")
            Donnee.query.filter_by(client_id=partner.id, exported=True).update({Donnee.exported: False})
            db.session.commit()
            print("Fix applied successfully.")
        else:
            print("\nNo exported PARTNER inquiries found.")
    else:
        print("\nPARTNER batches exist, skipping automatic reset to avoid data loss.")
    
    print("--- CHECK COMPLETE ---")
