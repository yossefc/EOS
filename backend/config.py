import os
import logging

class Config:
    """Configuration de base pour l'application Flask"""
    
    # Configuration de la base de données - PostgreSQL UNIQUEMENT
    # SQLite n'est plus supporté depuis la migration du 10/12/2025
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Récupérer DATABASE_URL (PostgreSQL obligatoire)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    
    # Vérification PostgreSQL (sera validée au démarrage de l'app)
    @staticmethod
    def validate_database_url():
        """Valide que DATABASE_URL est définie et pointe vers PostgreSQL"""
        db_url = os.environ.get('DATABASE_URL')
        if not db_url or not db_url.startswith('postgresql'):
            raise ValueError(
                "\n❌ ERREUR : DATABASE_URL doit être défini et pointer vers PostgreSQL !\n"
                "\n🔧 Solution :\n"
                "   Windows PowerShell :\n"
                "   $env:DATABASE_URL=\"postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db\"\n"
                "\n   Ou utilisez le script START_POSTGRESQL.ps1\n"
            )
        return db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration PostgreSQL optimisée pour production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,  # Taille du pool de connexions
        'max_overflow': 20,  # Connexions supplémentaires en cas de pic
        'pool_pre_ping': True,  # Vérifie la connexion avant utilisation
        'pool_recycle': 3600,  # Recycle les connexions après 1 heure
        'echo': False  # Désactive le logging SQL (activer en dev si besoin)
    }
    
    # Configuration des fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    # Configuration CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://192.168.175.1:5173,http://172.18.240.1:5173').split(',')
    
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
