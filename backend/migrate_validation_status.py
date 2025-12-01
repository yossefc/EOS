"""
Script de migration pour le nouveau système de validation
Convertit les statuts 'confirmee' en 'archive' et crée les entrées d'archive
"""
from app import create_app
from extensions import db
from models.models import Donnee
from models.enquete_archive import EnqueteArchive
from datetime import datetime
import sys

def migrate_validation_status():
    """Migre les statuts de validation vers le nouveau système"""
    app = create_app()
    with app.app_context():
        try:
            print("=== Migration du système de validation ===\n")
            
            # 1. Compter les enquêtes avec statut 'confirmee'
            enquetes_confirmees = Donnee.query.filter_by(statut_validation='confirmee').all()
            count_confirmees = len(enquetes_confirmees)
            
            print(f"📊 Enquêtes trouvées avec statut 'confirmee' : {count_confirmees}")
            
            if count_confirmees == 0:
                print("✅ Aucune migration nécessaire")
                return True
            
            # 2. Demander confirmation
            print(f"\n⚠️  Cette opération va :")
            print(f"   - Changer le statut de {count_confirmees} enquête(s) de 'confirmee' à 'archive'")
            print(f"   - Créer des entrées dans la table enquete_archives")
            
            confirmation = input("\nTapez 'OUI' pour confirmer : ")
            if confirmation.upper() != 'OUI':
                print("❌ Migration annulée")
                return False
            
            # 3. Effectuer la migration
            print("\n🔄 Migration en cours...")
            migrated_count = 0
            archives_created = 0
            
            for enquete in enquetes_confirmees:
                # Changer le statut
                enquete.statut_validation = 'archive'
                migrated_count += 1
                
                # Vérifier si une archive existe déjà
                existing_archive = EnqueteArchive.query.filter_by(enquete_id=enquete.id).first()
                
                if not existing_archive:
                    # Créer une entrée d'archive
                    archive = EnqueteArchive(
                        enquete_id=enquete.id,
                        date_export=enquete.updated_at or datetime.now(),
                        utilisateur='Migration Automatique',
                        nom_fichier=None  # Sera rempli lors de l'export réel
                    )
                    db.session.add(archive)
                    archives_created += 1
                
                # Ajouter à l'historique
                enquete.add_to_history(
                    'migration',
                    'Migration automatique du statut confirmee vers archive',
                    'Système'
                )
            
            # 4. Commit des changements
            db.session.commit()
            
            print(f"\n✅ Migration réussie !")
            print(f"   - {migrated_count} enquête(s) migrée(s) vers le statut 'archive'")
            print(f"   - {archives_created} entrée(s) d'archive créée(s)")
            
            # 5. Vérification
            remaining_confirmees = Donnee.query.filter_by(statut_validation='confirmee').count()
            if remaining_confirmees > 0:
                print(f"\n⚠️  Attention : {remaining_confirmees} enquête(s) avec statut 'confirmee' restante(s)")
                return False
            
            print("\n✅ Vérification : Aucune enquête avec statut 'confirmee' restante")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la migration : {e}")
            return False

def verify_migration():
    """Vérifie l'état de la migration"""
    app = create_app()
    with app.app_context():
        print("\n=== Vérification de la migration ===\n")
        
        # Compter les enquêtes par statut
        statuts = db.session.query(
            Donnee.statut_validation,
            db.func.count(Donnee.id)
        ).group_by(Donnee.statut_validation).all()
        
        print("📊 Répartition des statuts de validation :")
        for statut, count in statuts:
            print(f"   - {statut}: {count} enquête(s)")
        
        # Compter les archives
        archives_count = EnqueteArchive.query.count()
        print(f"\n📦 Nombre d'entrées dans enquete_archives : {archives_count}")
        
        # Vérifier la cohérence
        enquetes_archive = Donnee.query.filter_by(statut_validation='archive').count()
        print(f"\n🔍 Cohérence :")
        print(f"   - Enquêtes avec statut 'archive' : {enquetes_archive}")
        print(f"   - Entrées dans enquete_archives : {archives_count}")
        
        if archives_count >= enquetes_archive:
            print("   ✅ Cohérence OK")
        else:
            print(f"   ⚠️  Incohérence : {enquetes_archive - archives_count} archive(s) manquante(s)")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration du système de validation')
    parser.add_argument('--verify', action='store_true', help='Vérifier l\'état sans migrer')
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        success = migrate_validation_status()
        
        if success:
            print("\n💡 Vous pouvez maintenant vérifier avec : python migrate_validation_status.py --verify")
            sys.exit(0)
        else:
            sys.exit(1)



