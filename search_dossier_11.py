# -*- coding: utf-8 -*-
import pandas as pd
import os

# Chercher le dossier 11 dans les fichiers récents
folder = r"d:\EOS\reponses_cr backup"
print("Recherche du dossier 11 dans les fichiers Excel...")
print()

for filename in sorted([f for f in os.listdir(folder) if f.endswith('.xls') or f.endswith('.xlsx')], reverse=True)[:10]:
    filepath = os.path.join(folder, filename)
    try:
        df = pd.read_excel(filepath)
        
        # Chercher NUM = 11
        matches = df[df['NUM'].astype(str) == '11']
        
        if len(matches) > 0:
            print(f"=== TROUVE dossier 11 dans {filename} ===")
            print()
            
            for idx, row in matches.iterrows():
                print(f"NUM: {row['NUM']}")
                print(f"NOM: {row['NOM']}")
                print(f"PRENOM: {row['PRENOM']}")
                print(f"Date naissance: {row['JOUR']}/{row['MOIS']}/{row['ANNEE NAISSANCE']}")
                print(f"Lieu naissance: {row['LIEUNAISSANCE']}")
                print(f"ADRESSE origine: {row['ADRESSE']}")
                print(f"CP: {row['CP']}")
                print(f"VILLE: {row['VILLE']}")
                print(f"RECHERCHE: {row['RECHERCHE']}")
                print(f"Resultat: {row['Resultat']}")
                print()
                print("=== Donnees enqueteur ===")
                print(f"Adresse 1: {row['Adresse 1']}")
                print(f"Adresse 2: {row['Adresse 2']}")
                print(f"Adresse 3: {row['Adresse 3']}")
                print(f"Code postal: {row['Code postal']}")
                print(f"Ville: {row['Ville']}")
                print(f"Pays: {row['Pays']}")
                print(f"Telephone 1: {row['Telephone 1']}")
                print(f"Telephone 2: {row['Telephone 2']}")
                print(f"Portable 1: {row['Portable 1']}")
                print(f"memo: {row['memo']}")
                print()
                print("=== Employeur ===")
                print(f"Nom employeur: {row['Nom employeur']}")
                print(f"Adresse 1 employeur: {row['Adresse 1 employeur']}")
                print(f"Telephone employeur: {row['Telephone employeur']}")
                print(f"Memo employeur: {row['Memo employeur']}")
                print()
                print("=== Banque ===")
                print(f"Nom banque: {row['Nom banque']}")
                print(f"Code Banque: {row['Code Banque']}")
                print(f"Code guichet: {row['Code guichet']}")
                print(f"Telepone banque: {row['Telepone banque']}")
                print()
                break
            break
            
    except Exception as e:
        pass
