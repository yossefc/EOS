# -*- coding: utf-8 -*-
"""
Verification complete d'une enquete: Excel -> Base de donnees
"""
import pandas as pd
import os

folder = r"d:\EOS\reponses_cr backup"

print("=== VERIFICATION IMPORT ENQUETE ===\n")

# Prendre le premier fichier
for filename in sorted(os.listdir(folder)):
    if not filename.endswith('.xls') and not filename.endswith('.xlsx'):
        continue
    
    filepath = os.path.join(folder, filename)
    
    try:
        df = pd.read_excel(filepath)
        
        if 'NUM' not in df.columns or len(df) == 0:
            continue
        
        # Prendre la premiere ligne avec nom et prenom
        for idx, row in df.iterrows():
            nom = str(row.get('NOM', '')).strip().upper() if pd.notna(row.get('NOM')) else ''
            prenom = str(row.get('PRENOM', '')).strip().upper() if pd.notna(row.get('PRENOM')) else ''
            
            if not nom:
                continue
            
            print(f"ENQUETE SELECTIONNEE:")
            print(f"  Fichier: {filename}")
            print(f"  Ligne Excel: {idx + 2}")
            print()
            
            enquete_excel = {}
            
            # Tous les champs
            for col in df.columns:
                val = row.get(col)
                if pd.notna(val):
                    enquete_excel[col] = val
                else:
                    enquete_excel[col] = None
            
            print("DONNEES DANS EXCEL:")
            print("="*100)
            
            print("\n[IDENTITE]")
            print(f"  NUM: {enquete_excel.get('NUM')}")
            print(f"  NOM: {enquete_excel.get('NOM')}")
            print(f"  PRENOM: {enquete_excel.get('PRENOM')}")
            print(f"  DATE NAISSANCE: {enquete_excel.get('DATE NAISSANCE')}")
            print(f"  LIEU NAISSANCE: {enquete_excel.get('LIEU NAISSANCE')}")
            
            print("\n[ADRESSE]")
            print(f"  ADR1: {enquete_excel.get('ADR1')}")
            print(f"  ADR2: {enquete_excel.get('ADR2')}")
            print(f"  ADR3: {enquete_excel.get('ADR3')}")
            print(f"  CP: {enquete_excel.get('CP')}")
            print(f"  VILLE: {enquete_excel.get('VILLE')}")
            print(f"  PAYS: {enquete_excel.get('PAYS')}")
            print(f"  TEL: {enquete_excel.get('TEL')}")
            
            print("\n[DEMANDE]")
            print(f"  TD (Type): {enquete_excel.get('TD')}")
            print(f"  Elem (Elements demandes): {enquete_excel.get('Elem')}")
            print(f"  DATE ENVOI: {enquete_excel.get('DATE ENVOI')}")
            print(f"  DATE BUTOIR: {enquete_excel.get('DATE BUTOIR')}")
            
            print("\n[RESULTAT]")
            print(f"  Resultat: {enquete_excel.get('Resultat')}")
            print(f"  Elem trouvé: {enquete_excel.get('Elem trouvé')}")
            print(f"  Dat retour: {enquete_excel.get('Dat retour')}")
            
            print("\n[EMPLOYEUR]")
            print(f"  Employeur: {enquete_excel.get('Employeur')}")
            print(f"  ADR EMPL1: {enquete_excel.get('ADR EMPL1')}")
            print(f"  ADR EMPL2: {enquete_excel.get('ADR EMPL2')}")
            print(f"  ADR EMPL3: {enquete_excel.get('ADR EMPL3')}")
            print(f"  CP EMPL: {enquete_excel.get('CP EMPL')}")
            print(f"  VIL EMPL: {enquete_excel.get('VIL EMPL')}")
            print(f"  TEL EMPL: {enquete_excel.get('TEL EMPL')}")
            
            print("\n[BANQUE]")
            print(f"  Banque: {enquete_excel.get('Banque')}")
            print(f"  CB (Code banque): {enquete_excel.get('CB')}")
            print(f"  CG (Code guichet): {enquete_excel.get('CG')}")
            print(f"  Lib Guichet: {enquete_excel.get('Lib Guichet')}")
            print(f"  Tit. compte: {enquete_excel.get('Tit. compte')}")
            
            print("\n[MEMOS]")
            for i in range(1, 6):
                memo = enquete_excel.get(f'MEMO{i}')
                if memo and str(memo).strip() and str(memo).upper() not in ['NAN', 'NONE']:
                    print(f"  MEMO{i}: {str(memo)[:150]}")
            
            print("\n" + "="*100)
            print("\nCLE DE RECHERCHE DANS LA BASE:")
            print(f"  Nom: {nom}")
            print(f"  Prenom: {prenom}")
            print(f"  Date naissance: {enquete_excel.get('DATE NAISSANCE')}")
            print()
            
            # Sauvegarder
            import json
            excel_json = {}
            for k, v in enquete_excel.items():
                if v is not None and str(v).upper() not in ['NAN', 'NONE']:
                    excel_json[k] = str(v)
                else:
                    excel_json[k] = None
            
            with open('enquete_excel.json', 'w', encoding='utf-8') as f:
                json.dump(excel_json, f, ensure_ascii=False, indent=2)
            
            print("Donnees sauvegardees dans 'enquete_excel.json'")
            exit(0)
        
    except Exception as e:
        print(f"Erreur {filename}: {e}")
        continue

print("Aucune enquete trouvee")
