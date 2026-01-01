
import os
import sys

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models.client import Client

with app.app_context():
    clients = Client.query.all()
    for client in clients:
        print(f"ID: {client.id}, Code: '{client.code}', Nom: '{client.nom}'")
