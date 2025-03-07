from app import app
from models.models import db

with app.app_context():
    # Ajout de la colonne enqueteurId
    with db.engine.connect() as connection:
        connection.execute('''
            ALTER TABLE donnees 
            ADD COLUMN IF NOT EXISTS enqueteurId INTEGER REFERENCES enqueteurs(id)
        ''')
        print("Migration completed successfully!")
