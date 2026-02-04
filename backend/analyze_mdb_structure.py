"""
Script d'analyse de la structure des fichiers MDB (Microsoft Access)

Ce script permet d'examiner la structure d'un fichier MDB pour :
- Lister toutes les tables
- Afficher les colonnes et types de données
- Générer un rapport JSON pour faciliter le mapping

Usage:
    python analyze_mdb_structure.py --file "chemin/vers/fichier.mdb"
    python analyze_mdb_structure.py --folder "chemin/vers/dossier"
    python analyze_mdb_structure.py --test-connection
"""

import pyodbc
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def test_odbc_drivers():
    """Teste la disponibilité des pilotes ODBC Access"""
    print("\n" + "="*70)
    print("TEST DES PILOTES ODBC DISPONIBLES")
    print("="*70)
    
    drivers = [x for x in pyodbc.drivers() if 'Access' in x or 'Microsoft' in x]
    
    if not drivers:
        print("\n❌ ERREUR : Aucun pilote Microsoft Access trouvé !")
        print("\n📥 INSTALLATION REQUISE :")
        print("   Téléchargez et installez :")
        print("   Microsoft Access Database Engine 2016 Redistributable")
        print("   https://www.microsoft.com/en-us/download/details.aspx?id=54920")
        print("\n⚠️  IMPORTANT : Choisissez la version (32-bit ou 64-bit)")
        print("   qui correspond à votre installation Python")
        return False
    
    print("\n✅ Pilotes ODBC trouvés :")
    for driver in drivers:
        print(f"   - {driver}")
    
    return True


def get_mdb_connection(mdb_file):
    """Établit une connexion à un fichier MDB"""
    if not os.path.exists(mdb_file):
        raise FileNotFoundError(f"Fichier introuvable : {mdb_file}")
    
    # Trouver le pilote Access disponible
    drivers = [x for x in pyodbc.drivers() if 'Access' in x]
    if not drivers:
        raise RuntimeError("Aucun pilote Microsoft Access ODBC trouvé. Installez Access Database Engine.")
    
    driver = drivers[0]
    conn_str = f'DRIVER={{{driver}}};DBQ={mdb_file};'
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"\n❌ Erreur de connexion : {e}")
        raise


def analyze_mdb_structure(mdb_file):
    """Analyse la structure d'un fichier MDB"""
    print(f"\n{'='*70}")
    print(f"ANALYSE DU FICHIER : {os.path.basename(mdb_file)}")
    print(f"{'='*70}")
    
    conn = get_mdb_connection(mdb_file)
    cursor = conn.cursor()
    
    # Récupérer toutes les tables (exclure les tables système)
    tables = []
    for table_info in cursor.tables(tableType='TABLE'):
        table_name = table_info.table_name
        # Ignorer les tables système Access
        if not table_name.startswith('MSys') and not table_name.startswith('~'):
            tables.append(table_name)
    
    structure = {
        'file': os.path.basename(mdb_file),
        'full_path': os.path.abspath(mdb_file),
        'analyzed_at': datetime.now().isoformat(),
        'tables': []
    }
    
    print(f"\n📊 Tables trouvées : {len(tables)}")
    
    for table_name in tables:
        print(f"\n┌─ Table : {table_name}")
        
        # Récupérer les colonnes
        columns = []
        try:
            for column in cursor.columns(table=table_name):
                col_info = {
                    'name': column.column_name,
                    'type': column.type_name,
                    'size': column.column_size if hasattr(column, 'column_size') else None,
                    'nullable': column.nullable == 1 if hasattr(column, 'nullable') else None
                }
                columns.append(col_info)
                
                nullable_str = "NULL" if col_info['nullable'] else "NOT NULL"
                size_str = f"({col_info['size']})" if col_info['size'] else ""
                print(f"│  - {col_info['name']:<30} {col_info['type']:<15} {size_str:<10} {nullable_str}")
            
            # Compter les enregistrements
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                row_count = cursor.fetchone()[0]
                print(f"└─ Nombre d'enregistrements : {row_count}")
            except:
                row_count = None
                print(f"└─ Impossible de compter les enregistrements")
            
            structure['tables'].append({
                'name': table_name,
                'columns': columns,
                'row_count': row_count
            })
            
        except Exception as e:
            print(f"└─ ⚠️  Erreur lors de l'analyse : {e}")
    
    conn.close()
    return structure


def save_structure_report(structure, output_file=None):
    """Sauvegarde le rapport de structure en JSON"""
    if output_file is None:
        base_name = Path(structure['file']).stem
        output_file = f"mdb_structure_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Rapport sauvegardé : {output_file}")
    return output_file


def analyze_folder(folder_path):
    """Analyse tous les fichiers MDB dans un dossier"""
    mdb_files = list(Path(folder_path).glob('*.mdb'))
    
    if not mdb_files:
        print(f"\n❌ Aucun fichier .mdb trouvé dans : {folder_path}")
        return
    
    print(f"\n📁 {len(mdb_files)} fichier(s) .mdb trouvé(s)")
    
    all_structures = []
    for mdb_file in mdb_files:
        try:
            structure = analyze_mdb_structure(str(mdb_file))
            all_structures.append(structure)
            save_structure_report(structure)
        except Exception as e:
            print(f"\n❌ Erreur lors de l'analyse de {mdb_file.name} : {e}")
    
    # Créer un rapport consolidé
    if all_structures:
        consolidated = {
            'analyzed_at': datetime.now().isoformat(),
            'folder': str(folder_path),
            'total_files': len(all_structures),
            'files': all_structures
        }
        
        output_file = f"mdb_consolidated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Rapport consolidé sauvegardé : {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyse la structure des fichiers MDB')
    parser.add_argument('--file', help='Chemin vers un fichier MDB à analyser')
    parser.add_argument('--folder', help='Chemin vers un dossier contenant des fichiers MDB')
    parser.add_argument('--test-connection', action='store_true', help='Teste la disponibilité des pilotes ODBC')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("ANALYSEUR DE STRUCTURE MDB")
    print("="*70)
    
    if args.test_connection:
        success = test_odbc_drivers()
        sys.exit(0 if success else 1)
    
    if not args.file and not args.folder:
        print("\n❌ Erreur : Spécifiez --file ou --folder")
        parser.print_help()
        sys.exit(1)
    
    # Vérifier les pilotes d'abord
    if not test_odbc_drivers():
        sys.exit(1)
    
    try:
        if args.file:
            structure = analyze_mdb_structure(args.file)
            save_structure_report(structure)
        elif args.folder:
            analyze_folder(args.folder)
        
        print("\n" + "="*70)
        print("✅ ANALYSE TERMINÉE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
