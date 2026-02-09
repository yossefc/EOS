"""Script de diagnostic complet pour identifier le problème Sherlock"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("🔍 DIAGNOSTIC COMPLET - PROBLÈME SHERLOCK")
print("="*80)

problemes = []
ok_count = 0
total_checks = 0

# ============================================================================
# ÉTAPE 1: Vérifier les fichiers Python
# ============================================================================
print("\n📁 ÉTAPE 1: VÉRIFICATION DES FICHIERS")
print("-"*80)

total_checks += 3

# Test 1.1: import_engine.py
try:
    with open('import_engine.py', 'r', encoding='utf-8') as f:
        content_engine = f.read()
    
    has_unicodedata = 'import unicodedata' in content_engine
    has_normalize_func = 'def normalize_column_name' in content_engine
    has_col_map_exact = 'col_map_exact' in content_engine
    has_col_map_normalized = 'col_map_normalized' in content_engine
    
    if has_unicodedata and has_normalize_func and has_col_map_exact and has_col_map_normalized:
        print("✅ import_engine.py: TOUTES les corrections présentes")
        ok_count += 1
    else:
        print("❌ import_engine.py: Corrections MANQUANTES")
        if not has_unicodedata:
            problemes.append("- import_engine.py: Manque 'import unicodedata'")
        if not has_normalize_func:
            problemes.append("- import_engine.py: Manque 'def normalize_column_name'")
        if not has_col_map_exact:
            problemes.append("- import_engine.py: Manque 'col_map_exact'")
        if not has_col_map_normalized:
            problemes.append("- import_engine.py: Manque 'col_map_normalized'")
except Exception as e:
    print(f"❌ import_engine.py: Erreur de lecture - {e}")
    problemes.append(f"- import_engine.py: Erreur - {e}")

# Test 1.2: models/import_config.py
try:
    with open('models/import_config.py', 'r', encoding='utf-8') as f:
        content_config = f.read()
    
    has_unicodedata = 'import unicodedata' in content_config
    has_normalize_func = 'def normalize_column_name' in content_config
    has_normalize_usage = 'normalize_column_name(alias)' in content_config
    
    if has_unicodedata and has_normalize_func and has_normalize_usage:
        print("✅ models/import_config.py: TOUTES les corrections présentes")
        ok_count += 1
    else:
        print("❌ models/import_config.py: Corrections MANQUANTES")
        if not has_unicodedata:
            problemes.append("- import_config.py: Manque 'import unicodedata'")
        if not has_normalize_func:
            problemes.append("- import_config.py: Manque 'def normalize_column_name'")
        if not has_normalize_usage:
            problemes.append("- import_config.py: N'utilise pas normalize_column_name")
except Exception as e:
    print(f"❌ models/import_config.py: Erreur de lecture - {e}")
    problemes.append(f"- import_config.py: Erreur - {e}")

# Test 1.3: app.py (corrections export)
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content_app = f.read()
    
    has_format_date = 'def format_date(date_str):' in content_app
    has_remove_decimal = 'def remove_decimal_zero' in content_app
    has_tarifs = "'Tarif A'" in content_app and "'tarif_a'" in content_app
    
    if has_format_date and has_remove_decimal and not has_tarifs:
        print("✅ app.py: Corrections export présentes (dates, codes, sans tarifs)")
        ok_count += 1
    else:
        print("⚠️  app.py: Vérification export")
        if not has_format_date:
            problemes.append("- app.py: Manque format_date (dates pas en JJ/MM/AAAA)")
        if not has_remove_decimal:
            problemes.append("- app.py: Manque remove_decimal_zero (codes avec .0)")
        if has_tarifs:
            problemes.append("- app.py: Les tarifs sont encore dans l'export")
except Exception as e:
    print(f"❌ app.py: Erreur de lecture - {e}")
    problemes.append(f"- app.py: Erreur - {e}")

# ============================================================================
# ÉTAPE 2: Vérifier la base de données
# ============================================================================
print("\n🗄️  ÉTAPE 2: VÉRIFICATION BASE DE DONNÉES")
print("-"*80)

total_checks += 1

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("⚠️  DATABASE_URL non définie - Impossible de vérifier la base")
    print("   → Lancez START_POSTGRESQL.ps1 ou définissez DATABASE_URL")
else:
    try:
        from app import create_app
        from models import SherlockDonnee
        from extensions import db
        
        app = create_app()
        
        with app.app_context():
            total = db.session.query(SherlockDonnee).count()
            
            if total == 0:
                print("⚠️  Base de données: VIDE (aucune donnée)")
                print("   → Importez un fichier Sherlock")
            else:
                print(f"✅ Base de données: {total} enregistrements trouvés")
                ok_count += 1
                
                # Vérifier les champs avec accents
                first = db.session.query(SherlockDonnee).first()
                
                champs_problematiques = [
                    ('reference_interne', 'RéférenceInterne'),
                    ('ec_civilite', 'EC-Civilité'),
                    ('ec_prenom', 'EC-Prénom'),
                    ('ec_localite_naissance', 'EC-Localité Naissance'),
                ]
                
                vides = 0
                for field_name, display_name in champs_problematiques:
                    value = getattr(first, field_name, None)
                    if not value or value == '' or str(value).lower() == 'nan':
                        vides += 1
                
                if vides == len(champs_problematiques):
                    print("   ❌ Tous les champs avec accents sont VIDES")
                    problemes.append("- Base: Champs avec accents vides (import n'a pas marché)")
                elif vides == 0:
                    print("   ✅ Tous les champs avec accents sont REMPLIS")
                else:
                    print(f"   ⚠️  {vides}/{len(champs_problematiques)} champs vides")
                    problemes.append(f"- Base: {vides} champs partiellement vides")
                    
    except Exception as e:
        print(f"❌ Erreur vérification base: {e}")
        problemes.append(f"- Base de données: Erreur - {e}")

# ============================================================================
# ÉTAPE 3: Vérifier le profil d'import
# ============================================================================
print("\n📋 ÉTAPE 3: VÉRIFICATION PROFIL IMPORT SHERLOCK")
print("-"*80)

total_checks += 1

try:
    import yaml
    yaml_path = 'clients/rg_sherlock/mapping_import.yaml'
    
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        mappings = config.get('mappings', [])
        
        # Vérifier les champs problématiques
        champs_yaml = [m.get('source_key') for m in mappings]
        
        has_ref = 'RéférenceInterne' in champs_yaml
        has_civ = 'EC-Civilité' in champs_yaml
        has_pre = 'EC-Prénom' in champs_yaml
        
        if has_ref and has_civ and has_pre:
            print(f"✅ YAML: {len(mappings)} mappings, champs avec accents présents")
            ok_count += 1
        else:
            print("⚠️  YAML: Certains champs manquants")
            if not has_ref:
                problemes.append("- YAML: Manque 'RéférenceInterne'")
            if not has_civ:
                problemes.append("- YAML: Manque 'EC-Civilité'")
            if not has_pre:
                problemes.append("- YAML: Manque 'EC-Prénom'")
    else:
        print(f"❌ YAML introuvable: {yaml_path}")
        problemes.append(f"- YAML introuvable: {yaml_path}")
        
except Exception as e:
    print(f"❌ Erreur lecture YAML: {e}")
    problemes.append(f"- YAML: Erreur - {e}")

# ============================================================================
# ÉTAPE 4: Test de normalisation
# ============================================================================
print("\n🧪 ÉTAPE 4: TEST DE NORMALISATION")
print("-"*80)

total_checks += 1

try:
    import unicodedata
    
    def normalize_column_name(name):
        if not name:
            return ""
        name_str = str(name)
        nfd = unicodedata.normalize('NFD', name_str)
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        return without_accents.upper().strip()
    
    test_cols = [
        ("RéférenceInterne", "REFERENCEINTERNE"),
        ("EC-Civilité", "EC-CIVILITE"),
        ("EC-Prénom", "EC-PRENOM"),
    ]
    
    all_ok = True
    for original, expected in test_cols:
        result = normalize_column_name(original)
        if result != expected:
            all_ok = False
            print(f"   ❌ '{original}' → '{result}' (attendu: '{expected}')")
            
    if all_ok:
        print("✅ Normalisation fonctionne correctement")
        ok_count += 1
    else:
        problemes.append("- Normalisation: Fonction ne marche pas correctement")
        
except Exception as e:
    print(f"❌ Erreur test normalisation: {e}")
    problemes.append(f"- Normalisation: Erreur - {e}")

# ============================================================================
# DIAGNOSTIC FINAL
# ============================================================================
print("\n" + "="*80)
print("📊 DIAGNOSTIC FINAL")
print("="*80)

print(f"\n✅ Tests OK: {ok_count}/{total_checks}")
print(f"❌ Problèmes: {len(problemes)}")

if problemes:
    print("\n🔴 PROBLÈMES IDENTIFIÉS:")
    for p in problemes:
        print(f"   {p}")
    
    print("\n" + "="*80)
    print("🔧 SOLUTION:")
    print("="*80)
    
    if any('import_engine.py' in p for p in problemes):
        print("\n1️⃣ import_engine.py a des problèmes")
        print("   → Copiez le fichier depuis l'autre ordinateur")
        print("   → OU synchronisez via Git")
    
    if any('import_config.py' in p for p in problemes):
        print("\n2️⃣ models/import_config.py a des problèmes")
        print("   → Copiez le fichier depuis l'autre ordinateur")
        print("   → OU synchronisez via Git")
    
    if any('Base' in p for p in problemes):
        print("\n3️⃣ Base de données a des données incorrectes")
        print("   → Supprimez le fichier Sherlock importé")
        print("   → Redémarrez Flask (Ctrl+C puis python app.py)")
        print("   → Réimportez le fichier")
    
    print("\n4️⃣ ÉTAPES DANS L'ORDRE:")
    print("   a) Vérifiez/copiez les fichiers corrigés")
    print("   b) REDÉMARREZ Flask (OBLIGATOIRE!)")
    print("   c) Supprimez l'ancien fichier importé")
    print("   d) Réimportez le fichier")
    print("   e) Relancez ce script pour vérifier")
    
else:
    print("\n✅ TOUS LES TESTS SONT OK!")
    print("\nSi l'import ne marche toujours pas:")
    print("1. Vérifiez les LOGS du serveur Flask pendant l'import")
    print("2. Cherchez les erreurs Python")
    print("3. Vérifiez que le fichier Excel n'est pas corrompu")

print("\n" + "="*80)
