# backend/init_db.py
from app import init_app

app = init_app()

if __name__ == '__main__':
    with app.app_context():
        from flask_migrate import Migrate
        from extensions import db
        migrate = Migrate(app, db)
        
        # Ne pas initialiser de nouvelles migrations
        # Utilisez plutôt les commandes suivantes séparément si nécessaire
        # from flask_migrate import upgrade
        # upgrade()