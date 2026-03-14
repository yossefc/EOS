#!/usr/bin/env python3
"""
Script de vérification de l'ordre des migrations Alembic
Vérifie qu'il n'y a pas de révisions en doublon ou de références manquantes
"""
import os
import re
from pathlib import Path

# Couleurs pour la console
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def extract_migration_info(filepath):
    """Extrait les informations d'une migration"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    revision_match = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", content)
    down_revision_match = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", content)
    
    if not revision_match:
        return None
    
    return {
        'file': filepath.name,
        'revision': revision_match.group(1),
        'down_revision': down_revision_match.group(1) if down_revision_match else None
    }

def check_migrations():
    """Vérifie la cohérence des migrations"""
    migrations_dir = Path(__file__).parent / 'backend' / 'migrations' / 'versions'
    
    if not migrations_dir.exists():
        print(f"{RED}✗ Dossier des migrations introuvable : {migrations_dir}{RESET}")
        return False
    
    print(f"\n{YELLOW}=== Vérification des migrations Alembic ==={RESET}\n")
    print(f"Dossier : {migrations_dir}\n")
    
    # Charger toutes les migrations
    migrations = []
    for py_file in sorted(migrations_dir.glob('*.py')):
        if py_file.name == 'README.md' or py_file.name.startswith('__'):
            continue
        
        info = extract_migration_info(py_file)
        if info:
            migrations.append(info)
    
    if not migrations:
        print(f"{RED}✗ Aucune migration trouvée{RESET}")
        return False
    
    print(f"{GREEN}✓ {len(migrations)} fichiers de migration trouvés{RESET}\n")
    
    # Construire un dictionnaire revision -> info
    revisions = {}
    errors = []
    
    for m in migrations:
        rev = m['revision']
        if rev in revisions:
            errors.append(f"{RED}✗ ERREUR : Révision '{rev}' présente plusieurs fois !{RESET}")
            errors.append(f"  - {revisions[rev]['file']}")
            errors.append(f"  - {m['file']}")
        else:
            revisions[rev] = m
    
    # Vérifier les références
    all_revisions = set(revisions.keys())
    referenced_revisions = set()
    
    for m in migrations:
        down_rev = m['down_revision']
        if down_rev and down_rev != 'None':
            referenced_revisions.add(down_rev)
            if down_rev not in all_revisions:
                errors.append(f"{RED}✗ ERREUR : '{m['file']}' référence '{down_rev}' qui n'existe pas !{RESET}")
    
    # Trouver la révision racine (celle dont down_revision est None ou absente)
    root_revisions = []
    for m in migrations:
        down_rev = m['down_revision']
        if not down_rev or down_rev == 'None':
            root_revisions.append(m['revision'])
    
    if len(root_revisions) == 0:
        errors.append(f"{RED}✗ ERREUR : Aucune révision racine trouvée (cycle détecté ?){RESET}")
    elif len(root_revisions) > 1:
        errors.append(f"{YELLOW}⚠ ATTENTION : Plusieurs révisions racines trouvées :{RESET}")
        for root in root_revisions:
            errors.append(f"  - {root} ({revisions[root]['file']})")
    
    # Afficher l'ordre des migrations
    if not errors:
        print(f"{GREEN}✓ Pas d'erreurs détectées !{RESET}\n")
        print(f"{YELLOW}=== Ordre des migrations ==={RESET}\n")
        
        # Construire la chaîne depuis la racine
        if root_revisions:
            current = list(root_revisions)[0]
            visited = set()
            order = []
            
            while current and current not in visited:
                visited.add(current)
                migration = revisions.get(current)
                if migration:
                    order.append(migration)
                
                # Trouver la migration suivante (celle qui a current comme down_revision)
                next_migration = None
                for m in migrations:
                    if m['down_revision'] == current:
                        next_migration = m['revision']
                        break
                current = next_migration
            
            # Afficher l'ordre
            for i, m in enumerate(order, 1):
                print(f"{i:2d}. {m['revision']:40s} ({m['file']})")
                if i < len(order):
                    print("     ↓")
            
            # Vérifier qu'on a bien toutes les migrations
            if len(order) != len(migrations):
                print(f"\n{YELLOW}⚠ ATTENTION : {len(migrations) - len(order)} migration(s) ne sont pas dans la chaîne{RESET}")
                missing = set(m['revision'] for m in migrations) - set(m['revision'] for m in order)
                for rev in missing:
                    m = revisions[rev]
                    print(f"  - {rev} ({m['file']})")
        else:
            # Afficher toutes les migrations sans ordre particulier
            print(f"{YELLOW}Migrations détectées (aucune chaîne complète trouvée):{RESET}\n")
            for m in sorted(migrations, key=lambda x: x['file']):
                down = m['down_revision'] or 'None'
                print(f"  {m['revision']:40s} → {down:30s} ({m['file']})")
    else:
        print(f"\n{RED}=== ERREURS DÉTECTÉES ==={RESET}\n")
        for error in errors:
            print(error)
        return False
    
    print(f"\n{GREEN}✓ Vérification terminée avec succès !{RESET}\n")
    return True

if __name__ == '__main__':
    import sys
    # Forcer UTF-8 pour Windows
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    success = check_migrations()
    sys.exit(0 if success else 1)

