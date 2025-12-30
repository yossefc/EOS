"""
Script pour ajouter manuellement les colonnes client_id manquantes
et mettre à jour la version Alembic
"""
import os
import sys

# Définir DATABASE_URL AVANT tout import
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from flask_migrate import stamp

# Créer l'application
app = create_app()

with app.app_context():
    print("\n🔧 CORRECTION DE LA BASE DE DONNÉES")
    print("="*70)
    
    try:
        # 1. Ajouter client_id à fichiers
        print("\n📁 Ajout de client_id à la table fichiers...")
        db.session.execute(db.text("""
            ALTER TABLE fichiers ADD COLUMN IF NOT EXISTS client_id INTEGER;
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS ix_fichiers_client_id ON fichiers(client_id);
        """))
        print("   ✅ Colonne ajoutée")
        
        # 2. Ajouter client_id à donnees
        print("\n📝 Ajout de client_id à la table donnees...")
        db.session.execute(db.text("""
            ALTER TABLE donnees ADD COLUMN IF NOT EXISTS client_id INTEGER;
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_donnee_client_id ON donnees(client_id);
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_donnee_client_statut ON donnees(client_id, statut_validation);
        """))
        print("   ✅ Colonne ajoutée")
        
        # 3. Ajouter client_id à donnees_enqueteur
        print("\n👨‍💼 Ajout de client_id à la table donnees_enqueteur...")
        db.session.execute(db.text("""
            ALTER TABLE donnees_enqueteur ADD COLUMN IF NOT EXISTS client_id INTEGER;
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_donnee_enqueteur_client_id ON donnees_enqueteur(client_id);
        """))
        print("   ✅ Colonne ajoutée")
        
        # 4. Ajouter client_id à enquete_archive_files si la table existe
        print("\n📦 Ajout de client_id à la table enquete_archive_files...")
        db.session.execute(db.text("""
            ALTER TABLE enquete_archive_files ADD COLUMN IF NOT EXISTS client_id INTEGER;
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_archive_file_client_id ON enquete_archive_files(client_id);
        """))
        print("   ✅ Colonne ajoutée")
        
        # 5. Ajouter client_id à export_batches si la table existe
        print("\n📤 Ajout de client_id à la table export_batches...")
        db.session.execute(db.text("""
            ALTER TABLE export_batches ADD COLUMN IF NOT EXISTS client_id INTEGER;
        """))
        db.session.execute(db.text("""
            CREATE INDEX IF NOT EXISTS idx_export_batch_client_id ON export_batches(client_id);
        """))
        print("   ✅ Colonne ajoutée")
        
        # 6. Vérifier si le client EOS existe
        print("\n👥 Vérification du client EOS...")
        result = db.session.execute(db.text("SELECT COUNT(*) FROM clients WHERE code = 'EOS'"))
        count = result.scalar()
        
        if count == 0:
            print("   ℹ️  Client EOS inexistant, création...")
            db.session.execute(db.text("""
                INSERT INTO clients (code, nom, actif, date_creation)
                VALUES ('EOS', 'EOS France', true, NOW())
            """))
            print("   ✅ Client EOS créé")
        else:
            print("   ✅ Client EOS existe déjà")
        
        # 7. Récupérer l'ID du client EOS
        result = db.session.execute(db.text("SELECT id FROM clients WHERE code = 'EOS'"))
        eos_client_id = result.scalar()
        print(f"   → ID du client EOS : {eos_client_id}")
        
        # 8. Mettre à jour toutes les données existantes avec client_id = EOS
        print(f"\n🔄 Migration des données existantes vers client EOS (id={eos_client_id})...")
        
        db.session.execute(db.text(f"UPDATE fichiers SET client_id = {eos_client_id} WHERE client_id IS NULL"))
        db.session.execute(db.text(f"UPDATE donnees SET client_id = {eos_client_id} WHERE client_id IS NULL"))
        db.session.execute(db.text(f"UPDATE donnees_enqueteur SET client_id = {eos_client_id} WHERE client_id IS NULL"))
        db.session.execute(db.text(f"UPDATE enquete_archive_files SET client_id = {eos_client_id} WHERE client_id IS NULL"))
        db.session.execute(db.text(f"UPDATE export_batches SET client_id = {eos_client_id} WHERE client_id IS NULL"))
        
        print("   ✅ Données migrées")
        
        # 9. Rendre les colonnes NOT NULL et ajouter les contraintes FK
        print("\n🔒 Ajout des contraintes...")
        
        db.session.execute(db.text("ALTER TABLE fichiers ALTER COLUMN client_id SET NOT NULL"))
        db.session.execute(db.text("""
            ALTER TABLE fichiers 
            DROP CONSTRAINT IF EXISTS fk_fichiers_client_id,
            ADD CONSTRAINT fk_fichiers_client_id FOREIGN KEY (client_id) REFERENCES clients(id)
        """))
        
        db.session.execute(db.text("ALTER TABLE donnees ALTER COLUMN client_id SET NOT NULL"))
        db.session.execute(db.text("""
            ALTER TABLE donnees 
            DROP CONSTRAINT IF EXISTS fk_donnees_client_id,
            ADD CONSTRAINT fk_donnees_client_id FOREIGN KEY (client_id) REFERENCES clients(id)
        """))
        
        db.session.execute(db.text("ALTER TABLE donnees_enqueteur ALTER COLUMN client_id SET NOT NULL"))
        db.session.execute(db.text("""
            ALTER TABLE donnees_enqueteur 
            DROP CONSTRAINT IF EXISTS fk_donnees_enqueteur_client_id,
            ADD CONSTRAINT fk_donnees_enqueteur_client_id FOREIGN KEY (client_id) REFERENCES clients(id)
        """))
        
        db.session.execute(db.text("ALTER TABLE enquete_archive_files ALTER COLUMN client_id SET NOT NULL"))
        db.session.execute(db.text("""
            ALTER TABLE enquete_archive_files 
            DROP CONSTRAINT IF EXISTS fk_enquete_archive_files_client_id,
            ADD CONSTRAINT fk_enquete_archive_files_client_id FOREIGN KEY (client_id) REFERENCES clients(id)
        """))
        
        db.session.execute(db.text("ALTER TABLE export_batches ALTER COLUMN client_id SET NOT NULL"))
        db.session.execute(db.text("""
            ALTER TABLE export_batches 
            DROP CONSTRAINT IF EXISTS fk_export_batches_client_id,
            ADD CONSTRAINT fk_export_batches_client_id FOREIGN KEY (client_id) REFERENCES clients(id)
        """))
        
        print("   ✅ Contraintes ajoutées")
        
        # 10. Créer le profil d'import EOS s'il n'existe pas
        print("\n⚙️  Vérification du profil d'import EOS...")
        result = db.session.execute(db.text("SELECT COUNT(*) FROM import_profiles WHERE client_id = :client_id"), {"client_id": eos_client_id})
        count = result.scalar()
        
        if count == 0:
            print("   ℹ️  Profil d'import inexistant, création...")
            db.session.execute(db.text("""
                INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
                VALUES (:client_id, 'EOS TXT Format Standard', 'TXT_FIXED', 'utf-8', true, NOW())
            """), {"client_id": eos_client_id})
            print("   ✅ Profil d'import créé")
        else:
            print("   ✅ Profil d'import existe déjà")
        
        # 11. Commit toutes les modifications
        db.session.commit()
        print("\n💾 Modifications enregistrées")
        
        # 12. Mettre à jour la version Alembic
        print("\n🏷️  Mise à jour de la version Alembic...")
        stamp(revision='002_multi_client', directory='migrations')
        print("   ✅ Version mise à jour : 002_multi_client")
        
        print("\n" + "="*70)
        print("🎉 BASE DE DONNÉES CORRIGÉE AVEC SUCCÈS !")
        print("="*70)
        print("\nVous pouvez maintenant lancer l'application avec :")
        print("  python start_with_postgresql.py\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)





