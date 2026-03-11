"""
Wrapper pour démarrer l'application avec PostgreSQL
Ce script garantit que DATABASE_URL est défini AVANT d'importer app
"""
import os
import sys

def _load_env_file(path: str) -> None:
    """Charge les variables d'un fichier .env (syntaxe KEY=VALUE, sans python-dotenv)."""
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        pass

# Charger .env AVANT toute importation applicative
_env_path = os.path.join(os.path.dirname(__file__), '.env')
_load_env_file(_env_path)

if 'DATABASE_URL' not in os.environ:
    print("ERREUR : DATABASE_URL non définie. Ajoutez-la dans backend/.env")
    sys.exit(1)

print("✓ DATABASE_URL définie dans le processus Python")
print(f"  {os.environ['DATABASE_URL'][:50]}...")
print()

# Maintenant importer et lancer l'application
from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
