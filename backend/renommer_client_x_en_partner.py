"""
Script pour renommer CLIENT_X en PARTNER dans la base de données
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         Renommer CLIENT_X en PARTNER (PostgreSQL)             ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier que CLIENT_X existe
            print("► Vérification de CLIENT_X...")
            result = db.session.execute(text("""
                SELECT id, code, nom 
                FROM clients 
                WHERE code = 'CLIENT_X'
            """))
            
            client_x = result.fetchone()
            if not client_x:
                print("  ❌ CLIENT_X n'existe pas dans la base de données")
                print("     Aucune action nécessaire")
                return 0
            
            print(f"  ✅ CLIENT_X trouvé (ID: {client_x[0]}, Nom: {client_x[2]})")
            print()
            
            # Vérifier que PARTNER n'existe pas déjà
            print("► Vérification que PARTNER n'existe pas déjà...")
            result = db.session.execute(text("""
                SELECT id, code, nom 
                FROM clients 
                WHERE code = 'PARTNER'
            """))
            
            existing_partner = result.fetchone()
            if existing_partner:
                print(f"  ⚠️  PARTNER existe déjà (ID: {existing_partner[0]})")
                print("     Impossible de renommer CLIENT_X")
                return 1
            
            print("  ✅ PARTNER n'existe pas")
            print()
            
            # Compter les données liées
            print("► Comptage des données liées à CLIENT_X...")
            
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM donnees WHERE client_id = :client_id
            """), {'client_id': client_x[0]})
            nb_donnees = result.scalar()
            
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM fichiers WHERE client_id = :client_id
            """), {'client_id': client_x[0]})
            nb_fichiers = result.scalar()
            
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM import_profiles WHERE client_id = :client_id
            """), {'client_id': client_x[0]})
            nb_profiles = result.scalar()
            
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM tarifs_client WHERE client_id = :client_id
            """), {'client_id': client_x[0]})
            nb_tarifs = result.scalar()
            
            print(f"  • {nb_donnees} enquête(s)")
            print(f"  • {nb_fichiers} fichier(s)")
            print(f"  • {nb_profiles} profil(s) d'import")
            print(f"  • {nb_tarifs} tarif(s)")
            print()
            
            # Demander confirmation
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║  ⚠️  ATTENTION : Cette opération va renommer CLIENT_X         ║")
            print("║                  en PARTNER dans toute la base de données     ║")
            print("╚════════════════════════════════════════════════════════════════╝")
            print()
            response = input("Continuer ? (oui/non) : ").strip().lower()
            
            if response not in ['oui', 'o', 'yes', 'y']:
                print("\n❌ Opération annulée par l'utilisateur")
                return 0
            
            print()
            print("► Renommage de CLIENT_X en PARTNER...")
            
            # Mettre à jour le client
            db.session.execute(text("""
                UPDATE clients 
                SET code = 'PARTNER', 
                    nom = 'PARTNER',
                    date_modification = NOW()
                WHERE code = 'CLIENT_X'
            """))
            db.session.commit()
            
            print("  ✅ Code client mis à jour : CLIENT_X → PARTNER")
            print("  ✅ Nom client mis à jour : Client X → PARTNER")
            print()
            
            # Vérifier la mise à jour
            print("► Vérification de la mise à jour...")
            result = db.session.execute(text("""
                SELECT id, code, nom 
                FROM clients 
                WHERE code = 'PARTNER'
            """))
            
            partner = result.fetchone()
            if partner:
                print(f"  ✅ PARTNER créé avec succès (ID: {partner[0]}, Nom: {partner[2]})")
            else:
                print("  ❌ Erreur : PARTNER non trouvé après mise à jour")
                return 1
            
            print()
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║              ✅ Renommage terminé avec succès !               ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            
            print("Ce qui a changé :")
            print(f"  • Client code : CLIENT_X → PARTNER")
            print(f"  • Client nom : Client X → PARTNER")
            print(f"  • {nb_donnees} enquête(s) maintenant liées à PARTNER")
            print(f"  • {nb_fichiers} fichier(s) maintenant liés à PARTNER")
            print(f"  • {nb_profiles} profil(s) d'import maintenant liés à PARTNER")
            print(f"  • {nb_tarifs} tarif(s) maintenant liés à PARTNER")
            print()
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())


