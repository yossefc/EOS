# -*- coding: utf-8 -*-
"""
Verification du format des NUM dans les fichiers Excel
"""
import pandas as pd
import os

folder = r"d:\EOS\reponses_cr backup"

print("=== VERIFICATION FORMAT NUM ===\n")

exemples = []
for filename in sorted(os.listdir(folder))[:10]:
    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        continue
    
    filepath = os.path.join(folder, filename)
    
    try:
        df = pd.read_excel(filepath)
        if 'NUM' not in df.columns:
            continue
        
        print(f"{filename}:")
        for idx, row in df.head(5).iterrows():
            num = row.get('NUM', '')
            num_str = str(num).strip() if pd.notna(num) else ''
            num_upper = num_str.upper()
            print(f"  NUM brut: {repr(num)} -> str: '{num_str}' -> upper: '{num_upper}'")
            exemples.append((num, num_str, num_upper))
        print()
        break
    except:
        continue

print("\nExemples collectes:")
for brut, str_val, upper_val in exemples[:5]:
    print(f"  {repr(brut)} -> '{str_val}' -> '{upper_val}'")
