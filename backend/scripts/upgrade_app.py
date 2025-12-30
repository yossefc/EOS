"""
Script automatique de mise à jour de l'application EOS
Usage: python scripts/upgrade_app.py [--version VERSION]
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from flask_migrate import upgrade as flask_upgrade, current as flask_current
from sqlalchemy import inspect


def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_environment():
    """Vérifie que l'environnement est correct"""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ ERREUR : DATABASE_URL n'est pas défini")
        print("   Solution : $env:DATABASE_URL=\"postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db\"")
        return False
    
    print(f"✅ DATABASE_URL : {db_url[:50]}...")
    return True


def create_backup():
    """Crée une sauvegarde automatique de la base"""
    print("💾 Création d'une sauvegarde de sécurité...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backups'))
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = os.path.join(backup_dir, f'eos_backup_{timestamp}.dump')
    
    try:
        # Extraire les paramètres de connexion
        db_url = os.environ.get('DATABASE_URL')
        # Format: postgresql+psycopg2://user:password@host:port/database
        
        parts = db_url.replace('postgresql+psycopg2://', '').split('@')
        user_pass = parts[0].split(':')
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        database = host_db[1]
        
        # Créer le dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', database,
            '-F', 'c',
            '-f', backup_file
        ]
        
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        
        # Vérifier que le fichier existe
        if os.path.exists(backup_file):
            size_mb = os.path.getsize(backup_file) / 1024 / 1024
            print(f"✅ Sauvegarde créée : {backup_file}")
            print(f"   Taille : {size_mb:.2f} MB")
            return backup_file
        else:
            print("❌ Échec de création de la sauvegarde")
            return None
    
    except Exception as e:
        print(f"⚠️  Impossible de créer la sauvegarde automatique : {e}")
        print("   Veuillez créer une sauvegarde manuelle avant de continuer :")
        print("   pg_dump -U eos_user -d eos_db -F c -f backup.dump")
        return None


def get_current_version(app):
    """Obtient la version actuelle de la base"""
    print("📊 Version actuelle de la base de données...")
    
    with app.app_context():
        try:
            # Version Alembic
            from flask_migrate import current
            from io import StringIO
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            
            current()
            
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            
            if output.strip():
                print(f"   Version Alembic : {output.strip()}")
            else:
                print("   Version Alembic : Aucune migration appliquée")
            
            # Version de l'application
            if hasattr(app, 'config') and 'VERSION' in app.config:
                print(f"   Version application : {app.config['VERSION']}")
            
        except Exception as e:
            print(f"   ⚠️  Impossible de déterminer la version : {e}")


def check_database_state(app):
    """Vérifie l'état de la base de données"""
    print("🔍 Vérification de l'état de la base...")
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"   Tables : {len(tables)} trouvées")
            
            # Vérifier les tables critiques
            critical_tables = ['clients', 'donnees', 'fichiers', 'enqueteurs']
            for table in critical_tables:
                if table in tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} MANQUANTE")
            
            # Vérifier les colonnes client_id
            if 'fichiers' in tables:
                columns = [col['name'] for col in inspector.get_columns('fichiers')]
                if 'client_id' in columns:
                    print(f"   ✅ fichiers.client_id existe")
                else:
                    print(f"   ⚠️  fichiers.client_id manquant")
            
            return True
        
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
            return False


def apply_migrations(directory='migrations'):
    """Applique les migrations Alembic"""
    print("🔄 Application des migrations...")
    
    try:
        flask_upgrade(directory=directory)
        print("✅ Migrations appliquées avec succès")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de l'application des migrations : {e}")
        print("\n⚠️  ATTENTION : La base peut être dans un état incohérent")
        print("   Restaurez la sauvegarde si nécessaire :")
        print("   pg_restore -U eos_user -d eos_db backup.dump")
        return False


def verify_data_integrity(app):
    """Vérifie que les données importantes sont toujours présentes"""
    print("🔍 Vérification de l'intégrité des données...")
    
    with app.app_context():
        try:
            from models import Client, Donnee, Fichier, Enqueteur
            
            # Compter les enregistrements
            clients_count = Client.query.count()
            donnees_count = Donnee.query.count()
            fichiers_count = Fichier.query.count()
            enqueteurs_count = Enqueteur.query.count()
            
            print(f"   Clients : {clients_count}")
            print(f"   Enquêtes : {donnees_count}")
            print(f"   Fichiers : {fichiers_count}")
            print(f"   Enquêteurs : {enqueteurs_count}")
            
            if clients_count == 0:
                print("   ⚠️  Aucun client trouvé (attendu: au moins EOS)")
                return False
            
            print("   ✅ Données présentes")
            return True
        
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
            return False


def update_dependencies():
    """Met à jour les dépendances Python"""
    print("📦 Mise à jour des dépendances Python...")
    
    try:
        requirements_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'requirements.txt'
        ))
        
        if not os.path.exists(requirements_file):
            print("   ⚠️  requirements.txt introuvable")
            return True
        
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
            check=True,
            capture_output=True
        )
        
        print("   ✅ Dépendances mises à jour")
        return True
    
    except Exception as e:
        print(f"   ⚠️  Erreur : {e}")
        print("   Continuez manuellement avec : pip install -r requirements.txt")
        return True  # Ne pas bloquer si ça échoue


def main():
    parser = argparse.ArgumentParser(
        description='Script de mise à jour automatique de l\'application EOS'
    )
    parser.add_argument(
        '--version',
        help='Version cible (optionnel, sinon applique toutes les migrations en attente)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Ne pas créer de sauvegarde automatique (NON RECOMMANDÉ)'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Ne pas mettre à jour les dépendances Python'
    )
    
    args = parser.parse_args()
    
    print_header("🚀 MISE À JOUR DE L'APPLICATION EOS")
    
    # 1. Vérifier l'environnement
    if not check_environment():
        sys.exit(1)
    
    # 2. Créer l'application
    print("🔧 Chargement de l'application...")
    try:
        app = create_app()
        print("✅ Application chargée")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)
    
    # 3. Version actuelle
    get_current_version(app)
    
    # 4. État de la base
    if not check_database_state(app):
        print("\n⚠️  L'état de la base semble incomplet")
        response = input("Continuer quand même ? (O/N) : ")
        if response.upper() != 'O':
            sys.exit(1)
    
    # 5. Sauvegarde
    if not args.no_backup:
        backup_file = create_backup()
        if not backup_file:
            print("\n⚠️  ATTENTION : Aucune sauvegarde créée")
            response = input("Continuer sans sauvegarde ? (O/N) : ")
            if response.upper() != 'O':
                print("❌ Mise à jour annulée")
                sys.exit(1)
    else:
        print("⚠️  Mode --no-backup : aucune sauvegarde créée (NON RECOMMANDÉ)")
    
    # 6. Mettre à jour les dépendances
    if not args.skip_deps:
        update_dependencies()
    
    # 7. Appliquer les migrations
    with app.app_context():
        if not apply_migrations():
            print("\n❌ ÉCHEC : Les migrations n'ont pas pu être appliquées")
            sys.exit(1)
    
    # 8. Vérifier l'intégrité
    if not verify_data_integrity(app):
        print("\n⚠️  ATTENTION : Problème d'intégrité détecté")
        print("   Vérifiez les données manuellement")
    
    # 9. Résumé final
    print_header("✅ MISE À JOUR TERMINÉE")
    print("📊 Prochaines étapes :")
    print("   1. Vérifier les logs pour les erreurs éventuelles")
    print("   2. Redémarrer l'application : .\\start_eos.bat")
    print("   3. Tester que tout fonctionne correctement")
    print("   4. Vérifier que vos données sont toujours présentes")
    print("\n💡 En cas de problème :")
    print("   Restaurez la sauvegarde avec :")
    if not args.no_backup and 'backup_file' in locals():
        print(f"   pg_restore -U eos_user -d eos_db {backup_file}")
    else:
        print("   pg_restore -U eos_user -d eos_db backups/eos_backup_XXXX.dump")
    print()


if __name__ == '__main__':
    main()





