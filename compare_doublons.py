# -*- coding: utf-8 -*-
"""
Analyse des doublons dans les fichiers CR backup
"""
import pandas as pd
import os
from collections import defaultdict

folder = r"d:\EOS\reponses_cr backup"

print("=== ANALYSE DES DOUBLONS ===\n")

# Stocker toutes les occurrences de chaque personne
personnes = defaultdict(list)

for filename in sorted(os.listdir(folder)):
    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        continue
    
    filepath = os.path.join(folder, filename)
    
    try:
        df = pd.read_excel(filepath)
        
        if 'NUM' not in df.columns:
            continue
        
        for idx, row in df.iterrows():
            nom = str(row.get('NOM', '')).strip().upper() if pd.notna(row.get('NOM')) else ''
            prenom = str(row.get('PRENOM', '')).strip().upper() if pd.notna(row.get('PRENOM')) else ''
            date_naissance = row.get('DATE NAISSANCE')
            
            if not nom:
                continue
            
            # Cle unique
            key = f"{nom}|{prenom}|{date_naissance}"
            
            personnes[key].append({
                'fichier': filename,
                'NUM': row.get('NUM'),
                'NOM': nom,
                'PRENOM': prenom,
                'DATE NAISSANCE': date_naissance,
                'VILLE': row.get('VILLE'),
                'CP': row.get('CP'),
                'ADR1': row.get('ADR1'),
                'Resultat': row.get('Resultat'),
                'Dat retour': row.get('Dat retour'),
                'Employeur': row.get('Employeur'),
                'Banque': row.get('Banque'),
                'MEMO1': str(row.get('MEMO1', ''))[:100] if pd.notna(row.get('MEMO1')) else None,
                'TD': row.get('TD'),
                'Elem': row.get('Elem'),
            })
            
    except Exception as e:
        continue

# Trouver un doublon interessant
doublons = {k: v for k, v in personnes.items() if len(v) > 1}

print(f"Total personnes: {len(personnes)}")
print(f"Personnes avec doublons: {len(doublons)}")
print()

if doublons:
    # Prendre le premier doublon avec plusieurs occurrences
    exemple_key, occurrences = next(iter(doublons.items()))
    
    print(f"EXEMPLE DE DOUBLON:")
    print(f"  Personne: {exemple_key}")
    print(f"  Nombre d'occurrences: {len(occurrences)}")
    print()
    
    print("="*120)
    for i, occ in enumerate(occurrences[:5], 1):  # Limiter a 5 occurrences
        print(f"\nOCCURRENCE {i}:")
        print(f"  Fichier: {occ['fichier']}")
        print(f"  NUM: {occ['NUM']}")
        print(f"  Nom: {occ['NOM']} {occ['PRENOM']}")
        print(f"  Date naissance: {occ['DATE NAISSANCE']}")
        print(f"  Ville: {occ['VILLE']} ({occ['CP']})")
        print(f"  Adresse: {occ['ADR1']}")
        print(f"  Resultat: {occ['Resultat']} (retour: {occ['Dat retour']})")
        print(f"  Employeur: {occ['Employeur']}")
        print(f"  Banque: {occ['Banque']}")
        if occ['MEMO1']:
            print(f"  MEMO1: {occ['MEMO1']}")
        print(f"  Type: {occ['TD']}, Elements: {occ['Elem']}")
        print("-"*120)
    
    # Analyser les differences
    print("\n\nANALYSE DES DIFFERENCES:")
    
    champs = ['NUM', 'VILLE', 'CP', 'ADR1', 'Resultat', 'Dat retour', 'Employeur', 'Banque', 'TD', 'Elem']
    differences = defaultdict(set)
    
    for champ in champs:
        valeurs = set(str(occ.get(champ, '')) for occ in occurrences)
        if len(valeurs) > 1:
            differences[champ] = valeurs
    
    if differences:
        print("\nChamps qui varient entre les occurrences:")
        for champ, valeurs in differences.items():
            print(f"  - {champ}: {len(valeurs)} valeurs differentes")
            for v in list(valeurs)[:3]:
                print(f"      * {v}")
    else:
        print("  Toutes les occurrences sont IDENTIQUES (memes donnees)")
    
    print("\n\nCONCLUSION:")
    print("  Les doublons sont probablement dus a:")
    print("  1. Exports successifs qui incluent les memes enquetes")
    print("  2. Mises a jour des donnees (adresse, resultat, etc.)")
    print("  3. Fichiers de backup incrementaux")
    
else:
    print("Aucun doublon trouve!")

print("\n" + "="*120)
