"""
Script de diagnostic et correction complète de la configuration d'import
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from models.client import Client
from models.import_config import ImportProfile, ImportFieldMapping
from utils import COLUMN_SPECS
from sqlalchemy import text

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║       DIAGNOSTIC COMPLET - Configuration d'import EOS         ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        # 1. Vérifier le client EOS
        print("► ÉTAPE 1 : Vérification du client EOS")
        eos_client = Client.query.filter_by(code='EOS').first()
        if not eos_client:
            print("  ❌ Client EOS non trouvé !")
            return 1
        print(f"  ✅ Client EOS trouvé (ID: {eos_client.id})")
        print()
        
        # 2. Vérifier les profils d'import
        print("► ÉTAPE 2 : Vérification des profils d'import")
        profiles = ImportProfile.query.filter_by(client_id=eos_client.id).all()
        print(f"  Nombre de profils pour EOS : {len(profiles)}")
        for p in profiles:
            mappings_count = ImportFieldMapping.query.filter_by(import_profile_id=p.id).count()
            print(f"    - Profil ID={p.id}, Nom='{p.name}', Type='{p.file_type}', Mappings={mappings_count}")
        print()
        
        # 3. Si plusieurs profils, supprimer les mauvais
        if len(profiles) > 1:
            print("► ÉTAPE 3 : Suppression des profils en trop")
            # Garder le dernier créé (normalement le bon)
            profiles_sorted = sorted(profiles, key=lambda p: p.id)
            for p in profiles_sorted[:-1]:  # Tous sauf le dernier
                print(f"  Suppression du profil ID={p.id}...")
                ImportFieldMapping.query.filter_by(import_profile_id=p.id).delete()
                db.session.delete(p)
            db.session.commit()
            print("  ✅ Profils en trop supprimés")
            print()
            
            # Recharger le profil restant
            profiles = ImportProfile.query.filter_by(client_id=eos_client.id).all()
        
        # 4. Vérifier le profil restant
        if len(profiles) == 0:
            print("  ❌ Aucun profil trouvé après nettoyage ! Création d'un nouveau...")
            eos_profile = ImportProfile(
                client_id=eos_client.id,
                name='EOS - Fichier TXT fixe',
                file_type='TXT_FIXED'
            )
            db.session.add(eos_profile)
            db.session.commit()
            profiles = [eos_profile]
        
        eos_profile = profiles[0]
        print(f"► ÉTAPE 4 : Profil actif = ID {eos_profile.id}")
        print()
        
        # 5. Vérifier et corriger les mappings
        print("► ÉTAPE 5 : Vérification des mappings")
        existing_mappings = ImportFieldMapping.query.filter_by(import_profile_id=eos_profile.id).all()
        print(f"  Mappings existants : {len(existing_mappings)}")
        
        if len(existing_mappings) != len(COLUMN_SPECS):
            print(f"  ⚠️ Nombre incorrect ! Attendu: {len(COLUMN_SPECS)}, Trouvé: {len(existing_mappings)}")
            print("  Recréation des mappings...")
            
            # Supprimer les anciens
            ImportFieldMapping.query.filter_by(import_profile_id=eos_profile.id).delete()
            db.session.commit()
            
            # Créer les nouveaux (0-indexed)
            for field_name, start_pos, length in COLUMN_SPECS:
                mapping = ImportFieldMapping(
                    import_profile_id=eos_profile.id,
                    internal_field=field_name,
                    start_pos=start_pos,  # Déjà 0-indexed dans COLUMN_SPECS
                    length=length,
                    strip_whitespace=True
                )
                db.session.add(mapping)
            
            db.session.commit()
            print(f"  ✅ {len(COLUMN_SPECS)} mappings créés")
        else:
            print("  ✅ Nombre de mappings correct")
        print()
        
        # 6. Vérifier quelques mappings clés
        print("► ÉTAPE 6 : Vérification des mappings clés")
        key_fields = ['typeDemande', 'nom', 'prenom', 'numeroDossier', 'adresse1']
        for field in key_fields:
            mapping = ImportFieldMapping.query.filter_by(
                import_profile_id=eos_profile.id,
                internal_field=field
            ).first()
            if mapping:
                end_pos = mapping.start_pos + mapping.length
                # Trouver dans COLUMN_SPECS
                expected = next((cs for cs in COLUMN_SPECS if cs[0] == field), None)
                if expected:
                    exp_start, exp_length = expected[1], expected[2]
                    status = "✅" if (mapping.start_pos == exp_start and mapping.length == exp_length) else "❌"
                    print(f"  {status} {field:20s} : [{mapping.start_pos:3d}:{end_pos:3d}] (longueur {mapping.length}) | Attendu: [{exp_start:3d}:{exp_start+exp_length:3d}]")
        print()
        
        # 7. Vérifier les longueurs de colonnes PostgreSQL
        print("► ÉTAPE 7 : Vérification des longueurs de colonnes PostgreSQL")
        result = db.session.execute(text("""
            SELECT column_name, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'donnees'
            AND character_maximum_length IS NOT NULL
            ORDER BY column_name
        """))
        
        short_columns = []
        for row in result:
            col_name, max_length = row
            if max_length < 100:  # Colonnes potentiellement trop courtes
                short_columns.append((col_name, max_length))
        
        if short_columns:
            print(f"  ⚠️ {len(short_columns)} colonnes potentiellement trop courtes :")
            for col_name, max_length in short_columns[:10]:  # Afficher les 10 premières
                print(f"    - {col_name:30s} : VARCHAR({max_length})")
            print(f"\n  💡 Exécutez AGRANDIR_COLONNES.bat si nécessaire")
        else:
            print("  ✅ Toutes les colonnes ont des longueurs suffisantes")
        print()
        
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                  ✅ DIAGNOSTIC TERMINÉ                         ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")
        
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

