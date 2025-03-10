from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Nous gardons CORS mais sans l'initialiser tout de suite
cors = CORS()

# Fonction pour initialiser toutes les extensions
def init_extensions(app):
    db.init_app(app)
    # Nous commentons cette ligne pour éviter la double configuration CORS
    # cors.init_app(app)