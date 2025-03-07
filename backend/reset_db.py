import os
from flask import Flask
from models import db

def reset_db():
    # Create the Flask application
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database
    db.init_app(app)
    
    with app.app_context():
        # Drop all tables if they exist
        db.drop_all()
        
        # Create new tables
        db.create_all()
        
        print("Database reset successfully!")

if __name__ == "__main__":
    reset_db()