# 📍 OÙ TROUVER L'EXPORT SHERLOCK

## 📂 FICHIER PRINCIPAL

**Fichier:** `D:\EOS\backend\app.py`

**Ligne de début:** `1882`

**Route API:** `/api/export/sherlock`

---

## 🔍 STRUCTURE DU CODE

### 1️⃣ Route API (ligne 1881-1882)
```python
@app.route('/api/export/sherlock', methods=['POST'])
def export_sherlock():
    """Exporte les données Sherlock au format XLS vertical avec formatage"""
```

**Comment ça fonctionne:**
- L'interface web envoie une requête POST à `/api/export/sherlock`
- La fonction récupère les données de la base PostgreSQL
- Elle génère un fichier Excel (.xls)
- Elle renvoie le fichier pour téléchargement

---

### 2️⃣ Récupération des données (lignes 1895-1907)
```python
# Récupérer toutes les données SherlockDonnee
query = db.session.query(SherlockDonnee).join(
    Fichier, SherlockDonnee.fichier_id == Fichier.id
)

# Filtrer par client si nécessaire
if client_id:
    query = query.filter(Fichier.client_id == client_id)

# Récupérer les enregistrements
items = query.order_by(SherlockDonnee.id.asc()).all()
```

---

### 3️⃣ MAPPING DES CHAMPS (lignes 1909-1977) ⭐ IMPORTANT

**C'est ici que vous définissez les colonnes à exporter!**

```python
FIELDS_MAPPING = [
    ('DossierId', 'dossier_id', ''),           # Nom affiché, nom en base, valeur par défaut
    ('RéférenceInterne', 'reference_interne', ''),
    ('Demande', 'demande', ''),
    ('EC-Civilité', 'ec_civilite', ''),
    ('EC-Prénom', 'ec_prenom', ''),
    # ... 65 champs au total
]
```

**Format:**
```python
('Nom dans Excel', 'nom_champ_base_donnees', 'valeur_par_defaut')
```

**Modifications importantes:**
- ✅ **65 champs** (pas 68)
- ❌ **Pas de tarifs** (Tarif A, Tarif AT, Tarif DCD supprimés)
- ✅ Tous les champs **avec accents** (RéférenceInterne, EC-Civilité, etc.)

---

### 4️⃣ FONCTIONS DE FORMATAGE (lignes 1979-2042) ⭐ CORRECTIONS

#### A) Format des DATES (ligne 1979)
```python
def format_date(date_str):
    """Formate une date au format JJ/MM/AAAA"""
    # Convertit: 1975-02-07 00:00:00 → 07/02/1975
```

**Appliqué sur:**
- EC-Date Naissance
- Rép-EC-Date Naissance  
- Rép-DCD-Date

**Résultat:**
- ❌ Avant: `1975-02-07 00:00:00`
- ✅ Après: `07/02/1975`

---

#### B) Enlever le .0 des CODES (ligne 2001)
```python
def remove_decimal_zero(val):
    """Enlève le .0 des nombres comme 35000.0 -> 35000"""
    # Convertit: 75110.0 → 75110
```

**Appliqué sur:**
- Naissance CP
- Naissance INSEE
- AD-L6 CP
- AD-L6 INSEE
- Tous les champs "_cp" et "insee"

**Résultat:**
- ❌ Avant: `75110.0`, `88100.0`
- ✅ Après: `75110`, `88100`

---

#### C) Récupération des valeurs (ligne 2027)
```python
def get_field_value(item, attr_name, default_value):
    """Récupère la valeur d'un champ avec formatage spécial"""
    
    # 1. Récupérer la valeur de la base
    val = getattr(item, attr_name)
    
    # 2. Formater les dates
    if 'date_naissance' in attr_name.lower():
        return format_date(val)
    
    # 3. Enlever .0 des codes
    if any(x in attr_name.lower() for x in ['_cp', 'insee']):
        return remove_decimal_zero(val)
    
    # 4. Nettoyer la valeur
    return clean_value(val)
```

---

### 5️⃣ GÉNÉRATION DU FICHIER EXCEL (lignes 2044-2100)

**Format du fichier:**
- Format **VERTICAL** (2 colonnes)
- Colonne A: Nom du champ (en GRAS)
- Colonne B: Valeur

**Exemple:**
```
┌──────────────────────────┬────────────────────────────┐
│ DossierId               │ 570377204                  │
│ RéférenceInterne        │ DANS_SHERLOCK_260114008    │
│ Demande                 │ +A+T+Logement              │
│ EC-Civilité             │ Monsieur                   │
│ EC-Prénom               │ JEAN                       │
│ EC-Date Naissance       │ 07/02/1975                 │ ← Format JJ/MM/AAAA
│ Naissance CP            │ 75110                      │ ← Sans .0
│ ...                     │ ...                        │
└──────────────────────────┴────────────────────────────┘
```

---

## 🔧 POUR MODIFIER L'EXPORT

### Ajouter un champ:
**Ligne 1909-1977** dans `FIELDS_MAPPING`:
```python
FIELDS_MAPPING = [
    # ... champs existants ...
    ('Nouveau Champ', 'nouveau_champ_en_base', ''),  # ← Ajouter ici
]
```

### Supprimer un champ:
**Ligne 1909-1977** - Supprimez la ligne correspondante

### Changer le format:
**Modifiez les fonctions:**
- `format_date()` (ligne 1979) pour les dates
- `remove_decimal_zero()` (ligne 2001) pour les codes
- `get_field_value()` (ligne 2027) pour appliquer le formatage

---

## 📊 RÉSUMÉ DES CORRECTIONS APPLIQUÉES

| Aspect | Ligne | Avant | Après |
|--------|-------|-------|-------|
| **Nombre de champs** | 1909 | 68 | 65 (sans tarifs) |
| **Format dates** | 1979 | `1975-02-07 00:00:00` | `07/02/1975` |
| **Codes postaux/INSEE** | 2001 | `75110.0` | `75110` |
| **Tarifs** | 1909 | Présents | Supprimés |

---

## 🎯 FICHIERS IMPORTANTS POUR L'EXPORT

### Pour que l'export fonctionne, vous avez besoin de:

1. **`backend/app.py`** (lignes 1881-2100)
   - Fonction d'export
   - Formatage des données
   
2. **`backend/models/sherlock_donnee.py`**
   - Modèle de données SherlockDonnee
   - Définit les champs disponibles

3. **Base de données PostgreSQL**
   - Table `sherlock_donnees`
   - Doit contenir des données!

---

## ⚠️ ATTENTION

**Si l'export est vide, c'est que:**
1. ❌ **L'import n'a pas marché** (pas de données en base)
2. ❌ **Les fichiers d'import ne sont pas corrigés** (import_engine.py, import_config.py)

**Solution:**
1. Corrigez d'abord l'IMPORT (fichiers avec normalisation)
2. Réimportez les données
3. L'export fonctionnera automatiquement

---

## 📍 CHEMIN COMPLET DU CODE

```
D:\EOS\backend\app.py
Lignes: 1881 à 2100 (environ 220 lignes)

Sections principales:
- Route API: 1881-1882
- Récupération données: 1895-1907
- Mapping champs: 1909-1977  ⭐
- Formatage: 1979-2042       ⭐
- Génération Excel: 2044-2100
```

---

## 🔍 COMMENT TROUVER RAPIDEMENT

Dans Visual Studio Code / Cursor:
```
1. Ouvrir: D:\EOS\backend\app.py
2. Ctrl+F → Chercher: "def export_sherlock"
3. Aller à la ligne: 1882
```

---

**C'est ici que tout l'export Sherlock se passe!** 🎯
