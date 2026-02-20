# -*- coding: utf-8 -*-
"""
Script pour comparer les fichiers Excel CR avec la base de données
et identifier ce qui manque
"""
import pandas as pd
import os
import sys

folder = r"d:\EOS\reponses_cr backup"

print("=== ANALYSE DES FICHIERS EXCEL CR ===\n")

# Compter le nombre total d'enquêtes dans tous les fichiers Excel
total_excel = 0
fichiers_excel = []
enquetes_excel = []

for filename in os.listdir(folder):
    if filename.endswith('.xls') or filename.endswith('.xlsx'):
        filepath = os.path.join(folder, filename)
        try:
            df = pd.read_excel(filepath)
            nb_lignes = len(df)
            total_excel += nb_lignes
            fichiers_excel.append(filename)
            
            # Stocker les NUM (numéros de dossier)
            for idx, row in df.iterrows():
                enquetes_excel.append({
                    'num': str(row['NUM']),
                    'nom': str(row['NOM']),
                    'prenom': str(row['PRENOM']),
                    'fichier': filename,
                    'resultat': str(row['Resultat']) if pd.notna(row['Resultat']) else None
                })
                
        except Exception as e:
            print(f"Erreur lecture {filename}: {e}")

print(f"Nombre de fichiers Excel: {len(fichiers_excel)}")
print(f"Nombre total enquetes dans Excel: {total_excel}")
print()

# Statistiques sur les résultats
resultats_count = {}
for enq in enquetes_excel:
    res = enq['resultat']
    if res:
        resultats_count[res] = resultats_count.get(res, 0) + 1

print("Repartition des resultats dans Excel:")
for res, count in sorted(resultats_count.items()):
    print(f"  {res}: {count}")
print()

# Sauvegarder la liste pour comparaison
print("Sauvegarde de la liste des enquetes Excel...")
with open('enquetes_excel_list.txt', 'w', encoding='utf-8') as f:
    for enq in enquetes_excel:
        f.write(f"{enq['num']}|{enq['nom']}|{enq['prenom']}|{enq['resultat']}\n")

print(f"Liste sauvegardee dans enquetes_excel_list.txt")
print()
print("Pour comparer avec la base, utilisez API pour obtenir:")
print("  - Nombre enquetes avec statut 'archive' dans client PARTNER")
print("  - Verifier si les donnees enqueteur (code_resultat) sont presentes")
