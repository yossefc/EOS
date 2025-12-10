"""
Wrapper pour démarrer l'application avec PostgreSQL
Ce script garantit que DATABASE_URL est défini AVANT d'importer app
"""
import os
import sys

# Définir DATABASE_URL AVANT tout import
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

print("✓ DATABASE_URL définie dans le processus Python")
print(f"  {os.environ['DATABASE_URL'][:50]}...")
print()

# Maintenant importer et lancer l'application
from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

