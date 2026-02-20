# -*- coding: utf-8 -*-
"""
Recherche VERKAIN ELODIE dans les fichiers Excel
"""
import pandas as pd
import os

folder = r"d:\EOS\reponses_cr backup"

print("Recherche VERKAIN dans les fichiers Excel...\n")

found = False
for filename in os.listdir(folder):
    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        continue
    
    filepath = os.path.join(folder, filename)
    
    try:
        df = pd.read_excel(filepath)
        
        if 'NOM' not in df.columns:
            continue
        
        for idx, row in df.iterrows():
            nom = str(row.get('NOM', '')).upper()
            if 'VERKAIN' in nom:
                print(f"TROUVE dans {filename}:")
                print(f"  NUM: {row.get('NUM')}")
                print(f"  Nom: {row.get('NOM')}")
                print(f"  Prenom: {row.get('PRENOM')}")
                print(f"  Ville: {row.get('VILLE')}")
                print()
                found = True
                
    except Exception as e:
        continue

if not found:
    print("VERKAIN ELODIE n'est PAS dans les fichiers 'reponses_cr backup'")
    print()
    print("Cette enquete est probablement:")
    print("  - Un exemple/test que vous avez cree")
    print("  - Dans un autre dossier de backup")
    print("  - Une enquete recente non encore exportee")
