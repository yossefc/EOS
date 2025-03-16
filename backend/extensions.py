# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

# Initializations
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()

# Function to initialize all extensions
def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)  # Make sure this line is present