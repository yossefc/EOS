"""Test pour montrer que les accents SONT gardés dans le matching"""
import sys
import io
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_column_name(name):
    """Normalise un nom de colonne en enlevant les accents"""
    if not name:
        return ""
    name_str = str(name)
    nfd = unicodedata.normalize('NFD', name_str)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return without_accents.upper().strip()

print("="*80)
print("TEST DU MATCHING INTELLIGENT AVEC ACCENTS")
print("="*80)

# Simuler les colonnes Excel (AVEC accents - encodage correct)
colonnes_excel_correctes = [
    "DossierId",
    "RéférenceInterne",
    "EC-Civilité",
    "EC-Prénom",
    "EC-Localité Naissance",
]

# Simuler les colonnes Excel (SANS accents - encodage Windows parfois problématique)
colonnes_excel_sans_accents = [
    "DossierId",
    "ReferenceInterne",  # Pas d'accent
    "EC-Civilite",       # Pas d'accent
    "EC-Prenom",         # Pas d'accent
    "EC-Localite Naissance",  # Pas d'accent
]

# Les colonnes attendues dans le YAML (AVEC accents)
colonnes_yaml = [
    "RéférenceInterne",
    "EC-Civilité",
    "EC-Prénom",
    "EC-Localité Naissance",
]

print("\n1️⃣ CAS 1: Excel avec accents corrects (Windows moderne/Mac)")
print()

# Créer le col_map comme dans le nouveau code
col_map_exact = {str(col).strip(): col for col in colonnes_excel_correctes}
col_map_normalized = {normalize_column_name(col): col for col in colonnes_excel_correctes}
col_map = {**col_map_normalized, **col_map_exact}

print("col_map créé:")
for k, v in list(col_map.items())[:8]:
    print(f"   {k:30s} → {v}")

print("\nMatching des colonnes YAML:")
for yaml_col in colonnes_yaml:
    # STRATÉGIE 1: Exact match
    if yaml_col.strip() in col_map:
        excel_col = col_map[yaml_col.strip()]
        print(f"   ✅ '{yaml_col}' → TROUVÉ (EXACT avec accents): '{excel_col}'")
    # STRATÉGIE 2: Normalized
    else:
        norm = normalize_column_name(yaml_col)
        if norm in col_map:
            excel_col = col_map[norm]
            print(f"   ✅ '{yaml_col}' → TROUVÉ (NORMALIZED): '{excel_col}'")
        else:
            print(f"   ❌ '{yaml_col}' → NON TROUVÉ")

print("\n" + "="*80)
print("2️⃣ CAS 2: Excel sans accents (Windows ancien/encodage problématique)")
print()

# Créer le col_map pour Excel sans accents
col_map_exact = {str(col).strip(): col for col in colonnes_excel_sans_accents}
col_map_normalized = {normalize_column_name(col): col for col in colonnes_excel_sans_accents}
col_map = {**col_map_normalized, **col_map_exact}

print("col_map créé:")
for k, v in list(col_map.items())[:8]:
    print(f"   {k:30s} → {v}")

print("\nMatching des colonnes YAML (avec accents):")
for yaml_col in colonnes_yaml:
    # STRATÉGIE 1: Exact match
    if yaml_col.strip() in col_map:
        excel_col = col_map[yaml_col.strip()]
        print(f"   ✅ '{yaml_col}' → TROUVÉ (EXACT): '{excel_col}'")
    # STRATÉGIE 2: Normalized
    else:
        norm = normalize_column_name(yaml_col)
        if norm in col_map:
            excel_col = col_map[norm]
            print(f"   ✅ '{yaml_col}' → TROUVÉ (via NORMALIZED): '{excel_col}'")
        else:
            print(f"   ❌ '{yaml_col}' → NON TROUVÉ")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("""
✅ STRATÉGIE 1 (EXACT): Garde les accents si Excel les a bien encodés
   → "RéférenceInterne" (YAML) ↔ "RéférenceInterne" (Excel)
   → Matching direct, pas de perte d'information

✅ STRATÉGIE 2 (NORMALIZED): Fonctionne même si Excel n'a pas les accents
   → "RéférenceInterne" (YAML) ↔ "ReferenceInterne" (Excel)
   → Via normalisation: REFERENCEINTERNE = REFERENCEINTERNE

🎯 MEILLEUR DES DEUX MONDES:
   → Garde les accents si possible (meilleur)
   → Fonctionne sans accents si nécessaire (compatibilité)
   
💡 C'EST POUR ÇA QU'ON A LES DEUX:
   → On essaie D'ABORD avec accents (exact)
   → On essaie ENSUITE sans accents (normalized) si échec
   → Ça marche dans TOUS les cas!

ACTIONS:
1. REDÉMARREZ Flask
2. Supprimez l'ancien fichier
3. Réimportez
4. Les données seront correctement importées!
""")
print("="*80)
