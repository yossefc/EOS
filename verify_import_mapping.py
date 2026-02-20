# -*- coding: utf-8 -*-
"""
Verification complete d'une enquete: Excel -> Base de donnees
"""
import pandas as pd
import os

folder = r"d:\EOS\reponses_cr backup"

print("=== VERIFICATION IMPORT ENQUETE ===\n")

# Prendre le premier fichier avec des donnees completes
for filename in sorted(os.listdir(folder)):
    if not filename.endswith('.xls') and not filename.endswith('.xlsx'):
        continue
    
    filepath = os.path.join(folder, filename)
    
    try:
        df = pd.read_excel(filepath)
        
        if 'NUM' not in df.columns:
            continue
        
        # Prendre la premiere enquete avec des donnees completes
        for idx, row in df.iterrows():
            nom = str(row.get('NOM', '')).strip().upper() if pd.notna(row.get('NOM')) else ''
            prenom = str(row.get('PRENOM', '')).strip().upper() if pd.notna(row.get('PRENOM')) else ''
            
            if not nom or not prenom:
                continue
            
            # Prendre celle-ci si elle a des donnees interessantes
            if pd.notna(row.get('ADR1')) or pd.notna(row.get('Employeur')) or pd.notna(row.get('Banque')):
                
                print(f"ENQUETE SELECTIONNEE:")
                print(f"  Fichier: {filename}")
                print(f"  Ligne: {idx + 2}")
                print()
                
                enquete_excel = {
                    'fichier': filename,
                    'NUM': row.get('NUM'),
                    'NOM': nom,
                    'PRENOM': prenom,
                    'DATE NAISSANCE': row.get('DATE NAISSANCE'),
                    'LIEU NAISSANCE': row.get('LIEU NAISSANCE'),
                    'ADR1': row.get('ADR1'),
                    'ADR2': row.get('ADR2'),
                    'ADR3': row.get('ADR3'),
                    'CP': row.get('CP'),
                    'VILLE': row.get('VILLE'),
                    'PAYS': row.get('PAYS'),
                    'TEL': row.get('TEL'),
                    'TD': row.get('TD'),
                    'Elem': row.get('Elem'),
                    'Resultat': row.get('Resultat'),
                    'Elem trouvé': row.get('Elem trouvé'),
                    'Dat retour': row.get('Dat retour'),
                    'Employeur': row.get('Employeur'),
                    'ADR EMPL1': row.get('ADR EMPL1'),
                    'ADR EMPL2': row.get('ADR EMPL2'),
                    'ADR EMPL3': row.get('ADR EMPL3'),
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
                }
                
                print("DONNEES DANS EXCEL:")
                print("="*100)
                
                print("\nIDENTITE:")
                print(f"  NUM: {enquete_excel['NUM']}")
                print(f"  Nom: {enquete_excel['NOM']}")
                print(f"  Prenom: {enquete_excel['PRENOM']}")
                print(f"  Date naissance: {enquete_excel['DATE NAISSANCE']}")
                print(f"  Lieu naissance: {enquete_excel['LIEU NAISSANCE']}")
                
                print("\nADRESSE:")
                print(f"  ADR1: {enquete_excel['ADR1']}")
                print(f"  ADR2: {enquete_excel['ADR2']}")
                print(f"  ADR3: {enquete_excel['ADR3']}")
                print(f"  CP: {enquete_excel['CP']}")
                print(f"  Ville: {enquete_excel['VILLE']}")
                print(f"  Pays: {enquete_excel['PAYS']}")
                print(f"  Tel: {enquete_excel['TEL']}")
                
                print("\nDEMANDE:")
                print(f"  Type: {enquete_excel['TD']}")
                print(f"  Elements demandes: {enquete_excel['Elem']}")
                
                print("\nRESULTAT:")
                print(f"  Code resultat: {enquete_excel['Resultat']}")
                print(f"  Elements trouves: {enquete_excel['Elem trouvé']}")
                print(f"  Date retour: {enquete_excel['Dat retour']}")
                
                print("\nEMPLOYEUR:")
                print(f"  Nom: {enquete_excel['Employeur']}")
                print(f"  ADR1: {enquete_excel['ADR EMPL1']}")
                print(f"  ADR2: {enquete_excel['ADR EMPL2']}")
                print(f"  ADR3: {enquete_excel['ADR EMPL3']}")
                print(f"  CP: {enquete_excel['CP EMPL']}")
                print(f"  Ville: {enquete_excel['VIL EMPL']}")
                print(f"  Tel: {enquete_excel['TEL EMPL']}")
                
                print("\nBANQUE:")
                print(f"  Nom: {enquete_excel['Banque']}")
                print(f"  Code banque: {enquete_excel['CB']}")
                print(f"  Code guichet: {enquete_excel['CG']}")
                print(f"  Libelle guichet: {enquete_excel['Lib Guichet']}")
                print(f"  Titulaire: {enquete_excel['Tit. compte']}")
                
                print("\nMEMOS:")
                for i in range(1, 6):
                    memo = enquete_excel.get(f'MEMO{i}')
                    if pd.notna(memo) and str(memo).strip():
                        print(f"  MEMO{i}: {str(memo)[:100]}")
                
                print("\n" + "="*100)
                print("\nMAINTENANT, CHERCHONS CETTE ENQUETE DANS LA BASE...")
                print(f"Cle de recherche: {nom}|{prenom}|{enquete_excel['DATE NAISSANCE']}")
                print()
                
                # Sauvegarder pour la comparaison
                import json
                with open('enquete_excel.json', 'w', encoding='utf-8') as f:
                    # Convertir en strings pour JSON
                    excel_json = {}
                    for k, v in enquete_excel.items():
                        if pd.notna(v):
                            excel_json[k] = str(v)
                        else:
                            excel_json[k] = None
                    json.dump(excel_json, f, ensure_ascii=False, indent=2)
                
                print("Donnees Excel sauvegardees dans 'enquete_excel.json'")
                print(f"Utilisez l'API pour chercher: nom={nom}, prenom={prenom}")
                
                # Sortir apres la premiere
                exit(0)
        
        # Si on arrive ici, essayer le fichier suivant
        
    except Exception as e:
        print(f"Erreur fichier {filename}: {e}")
        continue

print("Aucune enquete trouvee avec des donnees completes")
