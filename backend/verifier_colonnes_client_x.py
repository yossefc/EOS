"""
Script pour vérifier que les colonnes CLIENT_X ont bien été ajoutées
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║     Vérification des colonnes CLIENT_X (PostgreSQL)           ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier la table tarifs_client
            print("► Vérification de la table 'tarifs_client'...")
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_name = 'tarifs_client'
            """))
            
            if result.fetchone():
                print("  ✅ Table 'tarifs_client' existe\n")
                
                # Compter les tarifs CLIENT_X
                result = db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM tarifs_client tc
                    JOIN clients c ON tc.client_id = c.id
                    WHERE c.code = 'CLIENT_X'
                """))
                count = result.scalar()
                print(f"     └─ {count} tarif(s) configuré(s) pour CLIENT_X")
            else:
                print("  ❌ Table 'tarifs_client' MANQUANTE\n")
            
            print()
            
            # Vérifier les colonnes dans donnees
            print("► Vérification des colonnes dans 'donnees'...")
            colonnes_requises = ['tarif_lettre', 'recherche', 'date_jour', 'nom_complet', 'motif']
            
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = 'donnees'
                  AND column_name IN ('tarif_lettre', 'recherche', 'date_jour', 'nom_complet', 'motif')
                ORDER BY column_name
            """))
            
            colonnes_trouvees = []
            for row in result:
                col_name = row[0]
                data_type = row[1]
                max_length = row[2]
                colonnes_trouvees.append(col_name)
                
                type_str = f"{data_type}"
                if max_length:
                    type_str += f"({max_length})"
                
                print(f"  ✅ {col_name:20s} → {type_str}")
            
            print()
            
            # Vérifier les colonnes manquantes
            colonnes_manquantes = set(colonnes_requises) - set(colonnes_trouvees)
            
            if colonnes_manquantes:
                print("⚠️  Colonnes MANQUANTES :")
                for col in colonnes_manquantes:
                    print(f"  ❌ {col}")
                print()
                print("👉 Exécutez : AJOUTER_COLONNES_CLIENT_X.bat")
                return 1
            else:
                print()
                print("╔════════════════════════════════════════════════════════════════╗")
                print("║       ✅ Toutes les colonnes CLIENT_X sont présentes          ║")
                print("╚════════════════════════════════════════════════════════════════╝\n")
                
                # Vérifier CLIENT_X
                print("► Vérification de CLIENT_X dans la base...")
                result = db.session.execute(text("""
                    SELECT id, code, nom 
                    FROM clients 
                    WHERE code = 'CLIENT_X'
                """))
                
                client = result.fetchone()
                if client:
                    print(f"  ✅ CLIENT_X existe (ID: {client[0]}, Nom: {client[2]})")
                    
                    # Compter les profils d'import
                    result = db.session.execute(text("""
                        SELECT COUNT(*) 
                        FROM import_profiles 
                        WHERE client_id = :client_id
                    """), {'client_id': client[0]})
                    nb_profiles = result.scalar()
                    print(f"     └─ {nb_profiles} profil(s) d'import configuré(s)")
                else:
                    print("  ⚠️  CLIENT_X n'est pas encore installé")
                    print("     👉 Exécutez : INSTALLER_CLIENT_X.bat")
                
                print()
                print("╔════════════════════════════════════════════════════════════════╗")
                print("║              ✅ Vérification terminée avec succès              ║")
                print("╚════════════════════════════════════════════════════════════════╝\n")
                return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())





