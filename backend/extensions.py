# backend/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Initialisation de CORS
cors = CORS()

# Vous pouvez ajouter d'autres extensions ici au besoin
# Par exemple:
# from flask_migrate import Migrate
# migrate = Migrate()

# Fonction pour initialiser toutes les extensions
def init_extensions(app):
    db.init_app(app)
    cors.init_app(app)
    # Ajoutez ici l'initialisation d'autres extensions
    # migrate.init_app(app, db)