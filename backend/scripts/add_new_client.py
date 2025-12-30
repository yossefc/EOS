"""
Script helper pour ajouter un nouveau client avec son profil d'import
Usage: python scripts/add_new_client.py --code CLIENT_B --name "Client B" --format TXT_FIXED
"""
import argparse
import sys
import os

# Ajouter le dossier parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import Client, ImportProfile, ImportFieldMapping
from extensions import db


def create_client(code, name):
    """Créer un nouveau client"""
    client = Client(
        code=code.upper(),
        nom=name,
        actif=True
    )
    db.session.add(client)
    db.session.commit()
    print(f"✓ Client créé: {client.code} - {client.nom} (ID: {client.id})")
    return client


def create_txt_profile(client, encoding='utf-8'):
    """Créer un profil d'import TXT à positions fixes"""
    profile = ImportProfile(
        client_id=client.id,
        name=f'{client.nom} - Format TXT',
        file_type='TXT_FIXED',
        encoding=encoding,
        actif=True
    )
    db.session.add(profile)
    db.session.commit()
    print(f"✓ Profil d'import TXT créé (ID: {profile.id})")
    return profile


def create_excel_profile(client, sheet_name='Sheet1', encoding='utf-8'):
    """Créer un profil d'import Excel"""
    profile = ImportProfile(
        client_id=client.id,
        name=f'{client.nom} - Format Excel',
        file_type='EXCEL',
        sheet_name=sheet_name,
        encoding=encoding,
        actif=True
    )
    db.session.add(profile)
    db.session.commit()
    print(f"✓ Profil d'import Excel créé (ID: {profile.id})")
    return profile


def add_field_mappings_interactive(profile):
    """Ajouter des mappings de champs de manière interactive"""
    print("\n--- Configuration des champs ---")
    print("Entrez les mappings un par un (Entrée vide pour terminer)")
    
    if profile.file_type == 'TXT_FIXED':
        print("Format: internal_field start_pos length")
        print("Exemple: numeroDossier 0 10")
    else:
        print("Format: internal_field column_name")
        print("Exemple: numeroDossier N° Dossier")
    
    mappings = []
    
    while True:
        user_input = input("\nMapping (ou Entrée pour terminer): ").strip()
        
        if not user_input:
            break
        
        try:
            if profile.file_type == 'TXT_FIXED':
                parts = user_input.split()
                if len(parts) != 3:
                    print("❌ Format invalide. Attendu: internal_field start_pos length")
                    continue
                
                field_name, start_pos, length = parts
                mapping = ImportFieldMapping(
                    import_profile_id=profile.id,
                    internal_field=field_name,
                    start_pos=int(start_pos),
                    length=int(length),
                    strip_whitespace=True
                )
                db.session.add(mapping)
                mappings.append(field_name)
                print(f"✓ Mapping ajouté: {field_name} [{start_pos}:{int(start_pos)+int(length)}]")
                
            else:  # EXCEL
                if ' ' not in user_input:
                    print("❌ Format invalide. Attendu: internal_field column_name")
                    continue
                
                field_name, column_name = user_input.split(' ', 1)
                mapping = ImportFieldMapping(
                    import_profile_id=profile.id,
                    internal_field=field_name,
                    column_name=column_name,
                    strip_whitespace=True
                )
                db.session.add(mapping)
                mappings.append(field_name)
                print(f"✓ Mapping ajouté: {field_name} -> '{column_name}'")
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            continue
    
    if mappings:
        db.session.commit()
        print(f"\n✓ {len(mappings)} mappings enregistrés")
    else:
        print("\n⚠️ Aucun mapping créé")
    
    return len(mappings)


def main():
    parser = argparse.ArgumentParser(
        description='Ajouter un nouveau client avec son profil d\'import'
    )
    parser.add_argument('--code', required=True, help='Code unique du client (ex: CLIENT_B)')
    parser.add_argument('--name', required=True, help='Nom du client (ex: "Client B")')
    parser.add_argument('--format', choices=['TXT_FIXED', 'EXCEL'], default='TXT_FIXED',
                       help='Format de fichier (défaut: TXT_FIXED)')
    parser.add_argument('--encoding', default='utf-8', help='Encodage du fichier (défaut: utf-8)')
    parser.add_argument('--sheet', default='Sheet1', help='Nom de la feuille Excel (défaut: Sheet1)')
    parser.add_argument('--interactive', action='store_true',
                       help='Mode interactif pour ajouter les mappings')
    
    args = parser.parse_args()
    
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"Ajout d'un nouveau client")
        print(f"{'='*60}\n")
        
        # Vérifier si le client existe déjà
        existing = Client.query.filter_by(code=args.code.upper()).first()
        if existing:
            print(f"❌ Un client avec le code '{args.code.upper()}' existe déjà!")
            sys.exit(1)
        
        # Créer le client
        client = create_client(args.code, args.name)
        
        # Créer le profil d'import
        if args.format == 'TXT_FIXED':
            profile = create_txt_profile(client, args.encoding)
        else:
            profile = create_excel_profile(client, args.sheet, args.encoding)
        
        # Ajouter les mappings (mode interactif)
        if args.interactive:
            mapping_count = add_field_mappings_interactive(profile)
            
            if mapping_count == 0:
                print("\n⚠️ Aucun mapping créé. Le profil d'import est incomplet.")
                print("Vous pouvez ajouter les mappings plus tard via l'interface d'administration")
        else:
            print("\n⚠️ Mode non-interactif: Aucun mapping créé")
            print("Utilisez --interactive pour ajouter les mappings maintenant")
            print("Ou ajoutez-les plus tard via l'interface d'administration")
        
        print(f"\n{'='*60}")
        print(f"✅ Client configuré avec succès!")
        print(f"{'='*60}\n")
        print(f"Client ID: {client.id}")
        print(f"Code: {client.code}")
        print(f"Profil d'import ID: {profile.id}")
        print(f"\nPour importer un fichier pour ce client:")
        print(f"  POST /parse avec client_id={client.id} ou client_code={client.code}")


if __name__ == '__main__':
    main()





