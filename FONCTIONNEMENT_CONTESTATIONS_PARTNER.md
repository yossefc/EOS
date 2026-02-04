# 🔍 Fonctionnement des Contestations PARTNER

**Date** : 22 janvier 2026  
**Objectif** : Expliquer comment le système traite les contestations Partner

---

## 📋 Table des Matières

1. [Recherche de l'Enquête Originale](#recherche-enquete-originale)
2. [Gestion du Prénom URGENT](#gestion-prenom-urgent)
3. [Vérifier les Mappings](#verifier-mappings)
4. [Diagnostic et Correction](#diagnostic-correction)

---

## 🔍 1. Recherche de l'Enquête Originale {#recherche-enquete-originale}

### Comment ça marche ?

Quand vous importez un fichier de **contestations**, le système cherche **automatiquement** l'enquête originale qui est contestée en 3 étapes :

#### **Étape 1 : Recherche par Numéro de Dossier**
```python
# Cherche dans numeroDossier
enquete_originale = Donnee.query.filter_by(
    client_id=partner_id,
    numeroDossier=contested_number  # Ex: "123" depuis la colonne "NUM CONTESTE"
).first()
```

#### **Étape 2 : Recherche par Numéro de Demande (si étape 1 échoue)**
```python
# Cherche dans numeroDemande
enquete_originale = Donnee.query.filter_by(
    client_id=partner_id,
    numeroDemande=contested_number
).first()
```

#### **Étape 3 : Recherche par Nom/Prénom/Date de Naissance (si étapes 1 et 2 échouent)**
```python
# Recherche intelligente avec score de correspondance
# Le système compare :
# - NOM (obligatoire, +10 points)
# - PRÉNOM (optionnel, +10 points si exact, +5 si partiel)
# - DATE DE NAISSANCE (optionnel, +10 points)
# 
# Minimum requis : score >= 10 (au moins le nom)
```

### 📍 Où se trouve cette logique ?

**Fichier** : `backend/import_engine.py`  
**Fonction** : `_handle_contestation()` (lignes 526-606)

### ✅ Résultat

Si l'enquête originale est trouvée :
- `enquete_originale_id` est rempli avec l'ID de l'enquête originale
- Le système établit le lien entre la contestation et l'enquête initiale
- **LOG** : `✅ Enquête originale trouvée via Fallback Nom/Prénom/Date (score: XX)`

Si elle n'est **pas** trouvée :
- `enquete_originale_id` reste NULL
- La contestation est quand même créée (vous pourrez la lier manuellement si besoin)
- **LOG** : `⚠️ Enquête originale NON trouvée pour contestation`

---

## 🚨 2. Gestion du Prénom "URGENT" {#gestion-prenom-urgent}

### Le Problème

Certains fichiers de contestation ont une colonne **URGENCE** qui contient "URGENT" ou "TRES URGENT".  
**Si le mapping est mal configuré**, cette colonne peut être mappée au champ `prenom` au lieu du champ `urgence`.

### ✅ Solution Implémentée

Le système sépare maintenant **clairement** le prénom et l'urgence :

#### **Avant (PROBLÈME)** ❌
```
Column "PRENOM"     -> prenom = "URGENT"  ❌ MAUVAIS !
Column "NOM"        -> nom = "DUPONT"
```

#### **Après (CORRECT)** ✅
```
Column "PRENOM"     -> prenom = "Jean"         ✅ Le vrai prénom
Column "URGENCE"    -> urgence = "1" (True)    ✅ Champ dédié
Column "NOM"        -> nom = "DUPONT"
```

### 📍 Où se trouve cette logique ?

**Fichier** : `backend/import_engine.py`  
**Fonction** : `_preprocess_client_x_record()` (lignes 709-721)

```python
# Si c'est une contestation
if record.get('typeDemande') == 'CON':
    # Si un champ 'urgence' existe, l'utiliser
    if 'urgence' in record:
        urgence_value = str(record.get('urgence', '')).strip().upper()
        if urgence_value in ['URGENT', '1', 'O', 'OUI', 'YES']:
            record['urgence'] = '1'  # True
        else:
            record['urgence'] = '0'  # False
    else:
        record['urgence'] = '0'  # Pas d'urgence par défaut
```

### ⚠️ IMPORTANT : Vérifier les Mappings

Pour que cela fonctionne, il faut que :
1. La colonne "PRENOM" soit mappée à `prenom`
2. La colonne "URGENCE" (ou "URGENT") soit mappée à `urgence`

**Si "URGENT" apparaît dans le prénom**, c'est que le **mapping est incorrect**.

---

## 🔧 3. Vérifier les Mappings {#verifier-mappings}

### Option A : Vérifier via Script SQL

Exécutez le script créé pour vous :

```powershell
cd d:\EOS
.\VERIFIER_MAPPINGS_PARTNER.bat
```

Ce script affiche :
- Toutes les colonnes mappées au champ `prenom`
- Toutes les colonnes mappées au champ `urgence`
- La liste complète des mappings PARTNER

### Option B : Vérifier manuellement dans psql

```sql
-- 1. Vérifier le mapping PRENOM
SELECT column_name, is_required
FROM import_field_mappings
WHERE import_profile_id = (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'prenom';

-- 2. Vérifier le mapping URGENCE
SELECT column_name, is_required
FROM import_field_mappings
WHERE import_profile_id = (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'urgence';
```

### ✅ Résultat Attendu

```
=== PRENOM ===
 column_name | is_required
-------------+-------------
 PRENOM      | f
 
=== URGENCE ===
 column_name | is_required
-------------+-------------
 URGENCE     | f
 URGENT      | f
```

### ❌ Si "URGENCE" ou "URGENT" apparaît dans les mappings de PRENOM

**Problème détecté !** Il faut corriger le mapping.

---

## 🛠️ 4. Diagnostic et Correction {#diagnostic-correction}

### Étape 1 : Vérifier les Données Importées

```sql
-- Voir les dernières contestations importées
SELECT id, "numeroDossier", nom, prenom, urgence, est_contestation
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND "typeDemande" = 'CON'
ORDER BY id DESC
LIMIT 10;
```

### Étape 2 : Identifier le Problème

Si vous voyez :
```
 id | numeroDossier |    nom    |  prenom  | urgence | est_contestation
----+---------------+-----------+----------+---------+------------------
 600|               | DUPONT    | URGENT   |    0    | f
```

**Problèmes identifiés** :
1. ❌ `prenom = "URGENT"` → Devrait être le vrai prénom
2. ❌ `urgence = "0"` → Devrait être "1" (vrai)
3. ❌ `est_contestation = f` → Devrait être TRUE (`t`)

### Étape 3 : Correction Manuelle (si nécessaire)

#### A. Corriger le flag `est_contestation`

```sql
-- Marquer toutes les contestations avec typeDemande = 'CON'
UPDATE donnees
SET est_contestation = TRUE
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND "typeDemande" = 'CON'
AND est_contestation = FALSE;
```

#### B. Corriger les Mappings (si "URGENT" est dans le prénom)

**Option 1 : Ré-exécuter le script de configuration**

```powershell
cd d:\EOS
psql -U postgres -d eos_db -f CONFIGURER_PARTNER.sql
```

**Option 2 : Correction SQL manuelle**

```sql
-- Supprimer les mauvais mappings PRENOM
DELETE FROM import_field_mappings
WHERE import_profile_id = (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'prenom'
AND column_name IN ('URGENCE', 'URGENT');

-- Ajouter le bon mapping si manquant
INSERT INTO import_field_mappings (import_profile_id, internal_field, column_name, is_required, is_unique, created_at)
SELECT 
    id,
    'prenom',
    'PRENOM',
    false,
    false,
    NOW()
FROM import_profiles
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND NOT EXISTS (
    SELECT 1 FROM import_field_mappings
    WHERE import_profile_id = import_profiles.id
    AND internal_field = 'prenom'
    AND column_name = 'PRENOM'
);

-- Ajouter le mapping URGENCE si manquant
INSERT INTO import_field_mappings (import_profile_id, internal_field, column_name, is_required, is_unique, created_at)
SELECT 
    id,
    'urgence',
    'URGENCE',
    false,
    false,
    NOW()
FROM import_profiles
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND NOT EXISTS (
    SELECT 1 FROM import_field_mappings
    WHERE import_profile_id = import_profiles.id
    AND internal_field = 'urgence'
    AND column_name = 'URGENCE'
);
```

#### C. Réimporter le Fichier

Après avoir corrigé les mappings :
1. **Supprimer** les contestations mal importées
2. **Réimporter** le fichier de contestation
3. **Vérifier** que le prénom et l'urgence sont corrects

---

## 📊 Résumé

| Question | Réponse |
|----------|---------|
| **Le système cherche-t-il l'enquête originale ?** | ✅ OUI, automatiquement en 3 étapes (numéro dossier → numéro demande → nom/prénom/date) |
| **Où est la logique ?** | `backend/import_engine.py`, fonction `_handle_contestation()` |
| **Pourquoi "URGENT" dans le prénom ?** | ❌ Mapping incorrect : la colonne "URGENCE" est mappée au champ `prenom` |
| **Comment corriger ?** | Vérifier les mappings avec `VERIFIER_MAPPINGS_PARTNER.bat` et corriger si nécessaire |
| **Le flag `est_contestation` est à FALSE ?** | Corriger avec `UPDATE donnees SET est_contestation = TRUE WHERE typeDemande = 'CON'` |

---

## 🧪 Test Complet

1. **Vérifier les mappings** : `.\VERIFIER_MAPPINGS_PARTNER.bat`
2. **Corriger si nécessaire** (script SQL ci-dessus)
3. **Réimporter** le fichier de contestation
4. **Vérifier l'import** :
```sql
SELECT id, "numeroDossier", nom, prenom, urgence, est_contestation, enquete_originale_id
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND "typeDemande" = 'CON'
ORDER BY id DESC
LIMIT 5;
```

5. **Tester l'export** dans l'interface (après redémarrage du backend)

---

**Dernière mise à jour** : 22 janvier 2026

