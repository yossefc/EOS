# -*- coding: utf-8 -*-
"""
Extraction des donnees VERKAIN ELODIE depuis l'image Excel
"""

print("=== DONNEES EXTRAITES DE L'IMAGE EXCEL ===\n")

enquete_excel = {
    # Identite
    'NUM': '11',
    'NOM': 'VERKAIN',
    'PRENOM': 'ELODIE',
    'DATE_NAISSANCE': '28/08/1985',
    'LIEU_NAISSANCE': 'ROUBAIX',
    
    # Adresse
    'ADR1': '45 RUE PASTEUR',
    'ADR2': '',
    'ADR3': '',
    'CP': '59100',
    'VILLE': 'ROUBAIX',
    'PAYS': 'FRANCE',
    'TEL': '0612345678',
    
    # Demande
    'TD': 'REL',
    'Elem': 'A',
    'DATE_ENVOI': '15/09/2024',
    'DATE_BUTOIR': '30/09/2024',
    
    # Resultat
    'Resultat': 'POS',
    'Elem_trouve': 'A',
    'Dat_retour': '25/09/2024',
    
    # Employeur
    'Employeur': 'DECATHLON FRANCE',
    'ADR_EMPL1': '10 BOULEVARD DES ALLIES',
    'ADR_EMPL2': '',
    'ADR_EMPL3': '',
    'CP_EMPL': '59100',
    'VIL_EMPL': 'ROUBAIX',
    'TEL_EMPL': '0320123456',
    
    # Banque
    'Banque': 'CREDIT MUTUEL',
    'CB': '10278',
    'CG': '06070',
    'Lib_Guichet': 'ROUBAIX CENTRE',
    'Tit_compte': 'VERKAIN ELODIE',
    
    # Memos
    'MEMO1': 'Personne joignable au telephone',
    'MEMO2': 'Travaille a temps plein',
    'MEMO3': '',
    'MEMO4': '',
    'MEMO5': ''
}

print("[IDENTITE]")
for k in ['NUM', 'NOM', 'PRENOM', 'DATE_NAISSANCE', 'LIEU_NAISSANCE']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[ADRESSE]")
for k in ['ADR1', 'CP', 'VILLE', 'PAYS', 'TEL']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[DEMANDE]")
for k in ['TD', 'Elem', 'DATE_ENVOI', 'DATE_BUTOIR']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[RESULTAT]")
for k in ['Resultat', 'Elem_trouve', 'Dat_retour']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[EMPLOYEUR]")
for k in ['Employeur', 'ADR_EMPL1', 'CP_EMPL', 'VIL_EMPL', 'TEL_EMPL']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[BANQUE]")
for k in ['Banque', 'CB', 'CG', 'Lib_Guichet', 'Tit_compte']:
    print(f"  {k}: {enquete_excel[k]}")

print("\n[MEMOS]")
print(f"  MEMO1: {enquete_excel['MEMO1']}")
print(f"  MEMO2: {enquete_excel['MEMO2']}")

print("\n" + "="*80)
print("CLE DE RECHERCHE: VERKAIN|ELODIE|28/08/1985")
print("Numero dossier: 11")
