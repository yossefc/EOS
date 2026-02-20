# -*- coding: utf-8 -*-
"""
Analyse complete d'une enquete: IMAGE vs BASE DE DONNEES
"""

print("=== DONNEES DEPUIS L'IMAGE ===")
print()

enquete_image = {
    'NUM': '1',
    'NOM': 'DELOR',
    'PRENOM': 'LOUIS',
    'DATE_NAISSANCE': '10/02/1954',
    'LIEU_NAISSANCE': 'CAMBRAI',
    'ADR1': '90 RUE DU COMMERCE',
    'ADR2': '',
    'ADR3': '',
    'CP': '59400',
    'VILLE': 'CAMBRAI',
    'PAYS': 'FRANCE',
    'TEL': '0327755115',
    'TD': 'ENQ',
    'Elem': 'A',
    'Resultat': 'P',
    'Elem_trouve': 'A',
    'Dat_retour': '14/11/2024',
    'Employeur': 'TRANSPORTS MONNIER',
    'ADR_EMPL1': '23 RUE DES CHAMPS',
    'ADR_EMPL2': '',
    'ADR_EMPL3': '',
    'CP_EMPL': '59400',
    'VIL_EMPL': 'CAMBRAI',
    'TEL_EMPL': '0327801010',
    'Banque': 'CREDIT AGRICOLE',
    'CB': '14508',
    'CG': '00532',
    'Lib_Guichet': 'CAMBRAI CENTRE',
    'Tit_compte': 'DELOR LOUIS',
    'MEMO1': 'Personne retrouvee a son domicile',
    'MEMO2': 'Employe depuis 15 ans',
    'MEMO3': '',
    'MEMO4': '',
    'MEMO5': ''
}

print("[IDENTITE]")
print(f"  NUM: {enquete_image['NUM']}")
print(f"  Nom: {enquete_image['NOM']}")
print(f"  Prenom: {enquete_image['PRENOM']}")
print(f"  Date naissance: {enquete_image['DATE_NAISSANCE']}")
print(f"  Lieu naissance: {enquete_image['LIEU_NAISSANCE']}")

print("\n[ADRESSE]")
print(f"  ADR1: {enquete_image['ADR1']}")
print(f"  ADR2: {enquete_image['ADR2']}")
print(f"  CP: {enquete_image['CP']}")
print(f"  Ville: {enquete_image['VILLE']}")
print(f"  Pays: {enquete_image['PAYS']}")
print(f"  Tel: {enquete_image['TEL']}")

print("\n[DEMANDE]")
print(f"  Type: {enquete_image['TD']}")
print(f"  Elements demandes: {enquete_image['Elem']}")

print("\n[RESULTAT]")
print(f"  Code: {enquete_image['Resultat']}")
print(f"  Elements trouves: {enquete_image['Elem_trouve']}")
print(f"  Date retour: {enquete_image['Dat_retour']}")

print("\n[EMPLOYEUR]")
print(f"  Nom: {enquete_image['Employeur']}")
print(f"  ADR1: {enquete_image['ADR_EMPL1']}")
print(f"  CP: {enquete_image['CP_EMPL']}")
print(f"  Ville: {enquete_image['VIL_EMPL']}")
print(f"  Tel: {enquete_image['TEL_EMPL']}")

print("\n[BANQUE]")
print(f"  Nom: {enquete_image['Banque']}")
print(f"  Code banque: {enquete_image['CB']}")
print(f"  Code guichet: {enquete_image['CG']}")
print(f"  Libelle: {enquete_image['Lib_Guichet']}")
print(f"  Titulaire: {enquete_image['Tit_compte']}")

print("\n[MEMOS]")
print(f"  MEMO1: {enquete_image['MEMO1']}")
print(f"  MEMO2: {enquete_image['MEMO2']}")

print("\n" + "="*80)
print("CLE DE RECHERCHE: DELOR|LOUIS|10/02/1954")
print("Utilisez l'API pour chercher cette enquete dans la base")
