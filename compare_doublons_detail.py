# -*- coding: utf-8 -*-
"""
Analyse approfondie d'un doublon avec beaucoup de differences
"""
import pandas as pd
import os
from collections import defaultdict

folder = r"d:\EOS\reponses_cr backup"

print("=== RECHERCHE D'UN DOUBLON AVEC DIFFERENCES ===\n")

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
                'ADR2': row.get('ADR2'),
                'ADR3': row.get('ADR3'),
                'TEL': row.get('TEL'),
                'Resultat': row.get('Resultat'),
                'Dat retour': row.get('Dat retour'),
                'Elem trouve': row.get('Elem trouvé'),
                'Employeur': row.get('Employeur'),
                'ADR EMPL1': row.get('ADR EMPL1'),
                'VIL EMPL': row.get('VIL EMPL'),
                'TEL EMPL': row.get('TEL EMPL'),
                'Banque': row.get('Banque'),
                'CB': row.get('CB'),
                'CG': row.get('CG'),
                'MEMO1': str(row.get('MEMO1', ''))[:200] if pd.notna(row.get('MEMO1')) else None,
                'MEMO2': str(row.get('MEMO2', ''))[:200] if pd.notna(row.get('MEMO2')) else None,
                'TD': row.get('TD'),
                'Elem': row.get('Elem'),
            })
            
    except Exception as e:
        continue

# Trouver doublons avec le plus de differences
doublons = {k: v for k, v in personnes.items() if len(v) > 1}

meilleur_exemple = None
max_differences = 0

champs = ['ADR1', 'ADR2', 'TEL', 'Resultat', 'Dat retour', 'Elem trouve', 
          'Employeur', 'ADR EMPL1', 'VIL EMPL', 'TEL EMPL', 'Banque', 'CB', 'CG']

for key, occurrences in doublons.items():
    nb_diff = 0
    for champ in champs:
        valeurs = set(str(occ.get(champ, '')) for occ in occurrences)
        if len(valeurs) > 1 and 'nan' not in ''.join(valeurs).lower():
            nb_diff += 1
    
    if nb_diff > max_differences:
        max_differences = nb_diff
        meilleur_exemple = (key, occurrences)

if meilleur_exemple:
    key, occurrences = meilleur_exemple
    
    print(f"DOUBLON AVEC LE PLUS DE DIFFERENCES:")
    print(f"  Personne: {key}")
    print(f"  Occurrences: {len(occurrences)}")
    print(f"  Champs differents: {max_differences}")
    print()
    
    print("="*120)
    for i, occ in enumerate(occurrences, 1):
        print(f"\nOCCURRENCE {i}: {occ['fichier']}")
        print(f"  NUM: {occ['NUM']}")
        print(f"  Identite: {occ['NOM']} {occ['PRENOM']} (ne le {occ['DATE NAISSANCE']})")
        print()
        print(f"  ADRESSE:")
        print(f"    {occ['ADR1']}")
        if occ['ADR2'] and str(occ['ADR2']) != 'nan':
            print(f"    {occ['ADR2']}")
        if occ['ADR3'] and str(occ['ADR3']) != 'nan':
            print(f"    {occ['ADR3']}")
        print(f"    {occ['CP']} {occ['VILLE']}")
        print(f"    Tel: {occ['TEL']}")
        print()
        print(f"  RESULTAT:")
        print(f"    Code: {occ['Resultat']}")
        print(f"    Date retour: {occ['Dat retour']}")
        print(f"    Elements trouves: {occ['Elem trouve']}")
        print()
        if occ['Employeur'] and str(occ['Employeur']) != 'nan':
            print(f"  EMPLOYEUR:")
            print(f"    Nom: {occ['Employeur']}")
            print(f"    Adresse: {occ['ADR EMPL1']}")
            print(f"    Ville: {occ['VIL EMPL']}")
            print(f"    Tel: {occ['TEL EMPL']}")
            print()
        if occ['Banque'] and str(occ['Banque']) != 'nan':
            print(f"  BANQUE:")
            print(f"    Nom: {occ['Banque']}")
            print(f"    Code banque: {occ['CB']}, Code guichet: {occ['CG']}")
            print()
        if occ['MEMO1']:
            print(f"  MEMO1: {occ['MEMO1']}")
        if occ['MEMO2']:
            print(f"  MEMO2: {occ['MEMO2']}")
        print("-"*120)
    
    print("\n\nCOMPARAISON DETAILLEE:")
    print()
    
    for champ in champs:
        valeurs = [str(occ.get(champ, '')) for occ in occurrences]
        if len(set(valeurs)) > 1 and 'nan' not in ''.join(valeurs).lower():
            print(f"  {champ}:")
            for i, val in enumerate(valeurs, 1):
                print(f"    Occurrence {i}: {val}")
            print()

else:
    print("Aucun doublon trouve avec des differences significatives")
