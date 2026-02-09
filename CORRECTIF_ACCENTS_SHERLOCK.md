# 🔧 CORRECTIF - Problème d'accents dans l'import Sherlock

## 🎯 PROBLÈME IDENTIFIÉ

**Vous avez raison!** Les champs avec **accents** ne sont pas importés correctement:

❌ **Champs manquants:**
- `RéférenceInterne` (accent: é)
- `EC-Civilité` (accent: é)
- `EC-Prénom`, `EC-Prénom2`, `EC-Prénom3`, `EC-Prénom4` (accent: é)
- `EC-Localité Naissance` (accent: é)

**Cause:** Le matching des noms de colonnes Excel avec le profil d'import échoue à cause des accents qui peuvent être encodés différemment selon le système.

---

## ✅ SOLUTION APPLIQUÉE

J'ai ajouté une **normalisation des noms de colonnes** qui:
1. Enlève tous les accents (`é` → `e`, `è` → `e`, etc.)
2. Met tout en majuscules
3. Fait un matching robuste

**Exemple:**
```
"RéférenceInterne" → normalise → "REFERENCEINTERNE"
"EC-Civilité"      → normalise → "EC-CIVILITE"
"EC-Prénom"        → normalise → "EC-PRENOM"
```

---

## 📂 FICHIERS MODIFIÉS

### 1. `backend/import_engine.py`

**Ajout de la fonction de normalisation:**
```python
import unicodedata

def normalize_column_name(name):
    """Normalise un nom de colonne en enlevant les accents"""
    if not name:
        return ""
    name_str = str(name)
    nfd = unicodedata.normalize('NFD', name_str)
    without_accents = ''.join(char for char in nfd 
                               if unicodedata.category(char) != 'Mn')
    return without_accents.upper().strip()
```

**Modification du mapping:**
```python
# Créer un dictionnaire de mapping normalisé pour gérer les accents
normalized_map = {normalize_column_name(k): k for k in raw_record.keys()}

for m in self.client_config['mappings']:
    source_key = m.get('source_key')
    
    # Essayer d'abord avec le nom exact
    value = raw_record.get(source_key)
    
    # Si pas trouvé, essayer avec la normalisation (sans accents)
    if value is None:
        normalized_source = normalize_column_name(source_key)
        original_key = normalized_map.get(normalized_source)
        if original_key:
            value = raw_record.get(original_key)
```

---

## 🔄 ÉTAPES POUR APPLIQUER LA CORRECTION

### Étape 1: Vérifier que les corrections sont sur cet ordinateur

Ouvrez `d:\EOS\backend\import_engine.py` et vérifiez:

**Ligne ~1-10:**
```python
import unicodedata  # ← Cette ligne doit être présente
```

**Ligne ~15-25:**
```python
def normalize_column_name(name):  # ← Cette fonction doit exister
    """Normalise un nom de colonne en enlevant les accents"""
```

**Si ces éléments sont absents:**
- Copiez le fichier `import_engine.py` depuis l'autre ordinateur
- OU synchronisez via Git

---

### Étape 2: REDÉMARRER le serveur Flask

**IMPORTANT:** Le serveur DOIT être redémarré pour charger les modifications!

```bash
# 1. Arrêter le serveur (dans le terminal où il tourne)
Ctrl+C

# 2. Redémarrer le serveur
cd D:\EOS\backend
python app.py
```

**Vérifiez qu'il démarre sans erreur!**

---

### Étape 3: Supprimer l'ancien fichier Sherlock

Dans l'interface web:
1. Allez dans la section "Fichiers Sherlock" ou "Gestion des fichiers"
2. **Supprimez** le fichier précédemment importé
3. Cela supprimera les données partielles où les champs avec accents sont vides

---

### Étape 4: RÉIMPORTER le fichier Sherlock

1. Importez à nouveau le fichier Excel Sherlock
2. L'import devrait maintenant **réussir complètement**
3. **Vérifiez les logs** - il ne devrait y avoir aucune erreur

---

### Étape 5: Vérifier l'export

1. Exportez les données Sherlock
2. Ouvrez le fichier Excel exporté
3. **Vérifiez que TOUS les champs avec accents sont remplis:**

**Attendu:**
```
✅ RéférenceInterne: DANS_SHERLOCK_260114008
✅ EC-Civilité: Monsieur
✅ EC-Prénom: DANIEN YOUNSOUF
✅ EC-Prénom2: (valeur ou vide si pas de données)
✅ EC-Prénom3: (valeur ou vide si pas de données)
✅ EC-Prénom4: (valeur ou vide si pas de données)
✅ EC-Localité Naissance: PARIS 10E ARRONDISSEMENT
```

**Formatage:**
```
✅ Dates: 30/06/1986 (pas 1986-06-30 00:00:00)
✅ Codes: 75110 (pas 75110.0)
✅ Pas de tarifs
```

---

## 🔍 TEST DE DIAGNOSTIC

Vous pouvez vérifier si tout est correct en cherchant dans `import_engine.py`:

```bash
# Rechercher la fonction de normalisation
grep -n "def normalize_column_name" backend/import_engine.py
```

Ou ouvrez le fichier et cherchez `normalize_column_name`.

**Si trouvé:** ✅ La correction est présente
**Si non trouvé:** ❌ Il faut copier le fichier corrigé

---

## ⚠️ POINTS IMPORTANTS

1. **TOUJOURS redémarrer Flask** après modification du code
2. **TOUJOURS supprimer l'ancien fichier** avant de réimporter
3. Les corrections sont dans le **code**, pas dans la base de données
4. Si vous avez des erreurs, vérifiez les **logs du serveur Flask**

---

## 📊 RÉSUMÉ DES CORRECTIONS

| Correction | Fichier | Description |
|------------|---------|-------------|
| 1. Normalisation accents | `import_engine.py` | Fonction `normalize_column_name()` |
| 2. Mapping robuste | `import_engine.py` | Utilise `normalized_map` |
| 3. Format dates | `app.py` | JJ/MM/AAAA au lieu de AAAA-MM-JJ |
| 4. Codes sans .0 | `app.py` | Enlève `.0` des codes INSEE/CP |
| 5. Tarifs supprimés | `app.py` | 65 champs au lieu de 68 |
| 6. Correction montant_ht | `import_engine.py` | Utilise `convert_float()` |

---

## ✅ CHECKLIST FINALE

Avant de tester:
- [ ] Fichier `import_engine.py` contient `normalize_column_name`
- [ ] Serveur Flask redémarré
- [ ] Ancien fichier Sherlock supprimé

Après import:
- [ ] Import réussi sans erreur
- [ ] Champs avec accents remplis dans l'export
- [ ] Dates au format JJ/MM/AAAA
- [ ] Codes sans .0

---

**Une fois ces étapes complétées, tous les champs devraient être correctement importés et exportés!**
