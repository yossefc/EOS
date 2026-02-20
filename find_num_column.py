# -*- coding: utf-8 -*-
import pandas as pd
import os

folder = r"d:\EOS\reponses_cr backup"

print("Recherche fichiers avec colonne NUM...")
for filename in sorted(os.listdir(folder)):
    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        continue
    
    filepath = os.path.join(folder, filename)
    try:
        df = pd.read_excel(filepath)
        if 'NUM' in df.columns:
            print(f"\nTrouve: {filename}")
            print(f"Colonnes: {list(df.columns)[:10]}")
            print(f"Nombre lignes: {len(df)}")
            
            # Afficher premiers NUM
            for idx in range(min(5, len(df))):
                num_val = df.iloc[idx]['NUM']
                print(f"  Ligne {idx}: NUM = {repr(num_val)} (type: {type(num_val)})")
            break
    except Exception as e:
        continue

print("\nFin recherche")
