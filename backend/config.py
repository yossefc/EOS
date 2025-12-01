import os
import logging

class Config:
    """Configuration de base pour l'application Flask"""
    
    # Configuration de la base de données
    # Utilise une variable d'environnement ou SQLite par défaut pour le développement
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'eos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration SQLite pour éviter les erreurs "database is locked"
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 30,  # Timeout de 30 secondes au lieu de 5 par défaut
            'check_same_thread': False  # Permet l'utilisation multi-thread
        },
        'pool_pre_ping': True,  # Vérifie la connexion avant utilisation
        'pool_recycle': 3600  # Recycle les connexions après 1 heure
    }
    
    # Configuration des fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    # Configuration CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://192.168.175.1:5173').split(',')
    
    # Configuration de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log'

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
