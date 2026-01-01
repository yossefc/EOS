
import os
import sys

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.models import Donnee

app = create_app()

with app.app_context():
    ids_to_fix = [429, 432, 433]
    print(f"Resetting 'exported' status for IDs: {ids_to_fix}")
    
    count = Donnee.query.filter(Donnee.id.in_(ids_to_fix)).update({Donnee.exported: False}, synchronize_session=False)
    db.session.commit()
    
    print(f"Success: {count} inquiries updated.")
