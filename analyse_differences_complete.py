# -*- coding: utf-8 -*-
"""
Analyse complete de tous les types de differences dans les doublons
"""
import pandas as pd
import os
from collections import defaultdict

folder = r"d:\EOS\reponses_cr backup"

print("=== ANALYSE COMPLETE DES DIFFERENCES ===\n")

personnes = defaultdict(list)

# Collecter toutes les donnees
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
            
            # Stocker TOUS les champs
            personnes[key].append({
                'fichier': filename,
                'NUM': row.get('NUM'),
                'NOM': nom,
                'PRENOM': prenom,
                'DATE NAISSANCE': date_naissance,
                'LIEU NAISSANCE': row.get('LIEU NAISSANCE'),
                'ADR1': row.get('ADR1'),
                'ADR2': row.get('ADR2'),
                'ADR3': row.get('ADR3'),
                'CP': row.get('CP'),
                'VILLE': row.get('VILLE'),
                'PAYS': row.get('PAYS'),
                'TEL': row.get('TEL'),
                'Resultat': row.get('Resultat'),
                'Dat retour': row.get('Dat retour'),
                'Elem': row.get('Elem'),
                'Elem trouve': row.get('Elem trouvé'),
                'Employeur': row.get('Employeur'),
                'ADR EMPL1': row.get('ADR EMPL1'),
                'ADR EMPL2': row.get('ADR EMPL2'),
                'CP EMPL': row.get('CP EMPL'),
                'VIL EMPL': row.get('VIL EMPL'),
                'TEL EMPL': row.get('TEL EMPL'),
                'Banque': row.get('Banque'),
                'CB': row.get('CB'),
                'CG': row.get('CG'),
                'Lib Guichet': row.get('Lib Guichet'),
                'Tit. compte': row.get('Tit. compte'),
                'MEMO1': row.get('MEMO1'),
                'MEMO2': row.get('MEMO2'),
                'MEMO3': row.get('MEMO3'),
                'MEMO4': row.get('MEMO4'),
                'MEMO5': row.get('MEMO5'),
                'TD': row.get('TD'),
                'DATE ENVOI': row.get('DATE ENVOI'),
                'DATE BUTOIR': row.get('DATE BUTOIR'),
            })
            
    except Exception as e:
        continue

print(f"Total personnes: {len(personnes)}")

# Analyser les types de differences
doublons = {k: v for k, v in personnes.items() if len(v) > 1}
print(f"Personnes avec doublons: {len(doublons)}\n")

# Statistiques sur les types de differences
types_diff = defaultdict(int)
exemples_par_type = {}

champs_a_analyser = [
    'ADR1', 'ADR2', 'CP', 'VILLE', 'TEL',
    'Resultat', 'Dat retour', 'Elem trouve',
    'Employeur', 'ADR EMPL1', 'VIL EMPL', 'TEL EMPL',
    'Banque', 'CB', 'CG', 'Lib Guichet',
    'MEMO1', 'MEMO2', 'MEMO3'
]

for key, occurrences in doublons.items():
    diff_this = []
    
    for champ in champs_a_analyser:
        valeurs = []
        for occ in occurrences:
            val = occ.get(champ)
            if pd.notna(val) and str(val).strip() and str(val).upper() not in ['NAN', 'NONE', '0', '']:
                valeurs.append(str(val))
        
        if len(set(valeurs)) > 1:
            diff_this.append(champ)
    
    for d in diff_this:
        types_diff[d] += 1
        if d not in exemples_par_type:
            exemples_par_type[d] = (key, occurrences)

print("STATISTIQUES DES DIFFERENCES PAR CHAMP:")
print("="*80)
for champ, count in sorted(types_diff.items(), key=lambda x: x[1], reverse=True):
    print(f"  {champ:20} : {count:4} doublons avec differences")
print()

# Afficher exemples pour les champs les plus importants
champs_importants = ['ADR1', 'TEL', 'Employeur', 'Banque', 'Resultat', 'MEMO1']

print("\nEXEMPLES DE DIFFERENCES PAR TYPE:")
print("="*120)

for champ in champs_importants:
    if champ in exemples_par_type:
        key, occurrences = exemples_par_type[champ]
        print(f"\n>>> CHAMP: {champ}")
        print(f"    Personne: {key.split('|')[0]} {key.split('|')[1]}")
        print(f"    Occurrences: {len(occurrences)}\n")
        
        for i, occ in enumerate(occurrences[:3], 1):
            val = occ.get(champ)
            if pd.notna(val):
                val_str = str(val)[:100]
            else:
                val_str = "(vide)"
            print(f"    Occ {i} ({occ['fichier'][:30]}): {val_str}")
        print("-"*120)

# Trouver un doublon avec BEAUCOUP de differences
print("\n\nDOUBLON AVEC LE PLUS DE DIFFERENCES:")
print("="*120)

max_diff = 0
meilleur = None

for key, occurrences in doublons.items():
    nb_diff = 0
    for champ in champs_a_analyser:
        valeurs = []
        for occ in occurrences:
            val = occ.get(champ)
            if pd.notna(val) and str(val).strip() and str(val).upper() not in ['NAN', 'NONE', '0', '']:
                valeurs.append(str(val))
        if len(set(valeurs)) > 1:
            nb_diff += 1
    
    if nb_diff > max_diff:
        max_diff = nb_diff
        meilleur = (key, occurrences, nb_diff)

if meilleur:
    key, occurrences, nb_diff = meilleur
    print(f"\nPersonne: {key}")
    print(f"Nombre d'occurrences: {len(occurrences)}")
    print(f"Nombre de champs differents: {nb_diff}\n")
    
    for i, occ in enumerate(occurrences, 1):
        print(f"\n>>> OCCURRENCE {i}: {occ['fichier']}")
        print(f"    Adresse: {occ.get('ADR1')}, {occ.get('CP')} {occ.get('VILLE')}")
        print(f"    Tel: {occ.get('TEL')}")
        print(f"    Resultat: {occ.get('Resultat')} (retour: {occ.get('Dat retour')})")
        print(f"    Elements: {occ.get('Elem trouve')}")
        
        if pd.notna(occ.get('Employeur')) and str(occ.get('Employeur')).upper() not in ['NAN', 'NONE']:
            print(f"    Employeur: {occ.get('Employeur')}")
            print(f"              {occ.get('ADR EMPL1')}, {occ.get('VIL EMPL')}")
            print(f"              Tel: {occ.get('TEL EMPL')}")
        
        if pd.notna(occ.get('Banque')) and str(occ.get('Banque')).upper() not in ['NAN', 'NONE']:
            print(f"    Banque: {occ.get('Banque')} (CB: {occ.get('CB')}, CG: {occ.get('CG')})")
        
        if pd.notna(occ.get('MEMO1')) and str(occ.get('MEMO1')).strip():
            print(f"    MEMO1: {str(occ.get('MEMO1'))[:100]}")

print("\n" + "="*120)
