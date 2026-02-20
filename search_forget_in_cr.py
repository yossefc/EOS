# -*- coding: utf-8 -*-
import pandas as pd
import os
import sys

# Chercher FORGET YOANN dans tous les fichiers Excel du dossier
folder = r"d:\EOS\reponses_cr backup"
target_nom = "FORGET"
target_prenom = "YOANN"

print(f"Recherche de {target_nom} {target_prenom}...")
print()

found = False

for filename in os.listdir(folder):
    if filename.endswith('.xls') or filename.endswith('.xlsx'):
        filepath = os.path.join(folder, filename)
        try:
            df = pd.read_excel(filepath)
            
            # Chercher dans NOM et PRENOM
            matches = df[
                (df['NOM'].astype(str).str.upper().str.contains(target_nom, na=False)) &
                (df['PRENOM'].astype(str).str.upper().str.contains(target_prenom, na=False))
            ]
            
            if len(matches) > 0:
                found = True
                print(f"=== TROUVE dans {filename} ===")
                print()
                
                for idx, row in matches.iterrows():
                    print(f"Ligne {idx + 2}:")  # +2 car Excel commence à 1 et il y a l'en-tête
                    print(f"  NUM: {row['NUM']}")
                    print(f"  NOM: {row['NOM']}")
                    print(f"  PRENOM: {row['PRENOM']}")
                    print(f"  Date naissance: {row['JOUR']}/{row['MOIS']}/{row['ANNEE NAISSANCE']}")
                    print(f"  Lieu naissance: {row['LIEUNAISSANCE']}")
                    print(f"  ADRESSE (origine): {row['ADRESSE']}")
                    print(f"  CP: {row['CP']}")
                    print(f"  VILLE: {row['VILLE']}")
                    print(f"  RECHERCHE: {row['RECHERCHE']}")
                    print(f"  Resultat: {row['Resultat']}")
                    print()
                    print(f"  Adresse 1 (enqueteur): {row['Adresse 1']}")
                    print(f"  Adresse 2: {row['Adresse 2']}")
                    print(f"  Adresse 3: {row['Adresse 3']}")
                    print(f"  Code postal: {row['Code postal']}")
                    print(f"  Ville (enqueteur): {row['Ville']}")
                    print(f"  Telephone 1: {row['Telephone 1']}")
                    print(f"  Telephone 2: {row['Telephone 2']}")
                    print(f"  memo: {row['memo']}")
                    print()
                    print(f"  Nom employeur: {row['Nom employeur']}")
                    print(f"  Adresse 1 employeur: {row['Adresse 1 employeur']}")
                    print(f"  Telephone employeur: {row['Telephone employeur']}")
                    print()
                    print(f"  Nom banque: {row['Nom banque']}")
                    print(f"  Code Banque: {row['Code Banque']}")
                    print(f"  Code guichet: {row['Code guichet']}")
                    print()
                    
        except Exception as e:
            pass  # Ignorer les erreurs de lecture

if not found:
    print(f"Aucun resultat trouve pour {target_nom} {target_prenom}")
