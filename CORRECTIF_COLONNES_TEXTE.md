# 🔧 CORRECTIF : Colonnes texte dans donnees_enqueteur

## ❌ Problème

Lors de l'application de la migration `007_enlarge_donnees_enqueteur_columns`, l'erreur suivante se produit :

```
psycopg2.errors.StringDataRightTruncation: ERREUR: valeur trop longue pour le type character varying(32)
```

**Cause** : Alembic utilise un type intermédiaire (VARCHAR(32)) lors de la conversion de VARCHAR(10) vers TEXT, ce qui échoue si des données font plus de 32 caractères (ex: "Confirmé par la mairie" = 23 caractères).

---

## ✅ Solution

Au lieu d'utiliser Alembic, on applique la conversion **directement en SQL** dans PostgreSQL, qui gère correctement la conversion sans type intermédiaire.

---

## 📋 Instructions (AUTRE ORDINATEUR)

### Étape 1️⃣ : Récupérer les scripts de correction

```bash
cd /d/eos
git pull origin master
```

### Étape 2️⃣ : Réinitialiser la migration 007

Si la migration 007 a partiellement échoué, réinitialisez-la :

```bash
psql -U postgres -d eos_db -c "UPDATE alembic_version SET version_num = '006_add_confirmation_options';"
```

### Étape 3️⃣ : Appliquer la correction SQL directe

**Exécutez le script batch :**

```bash
./CORRIGER_COLONNES_TEXTE.bat
```

Ce script va :
1. Convertir les 3 colonnes de VARCHAR vers TEXT directement dans PostgreSQL
2. Marquer la migration 007 comme appliquée dans Alembic
3. Afficher les types avant/après pour vérification

### Étape 4️⃣ : Redémarrer l'application

```bash
./DEMARRER_EOS_SIMPLE.bat
```

---

## 🔍 Vérification manuelle (optionnelle)

Si vous voulez vérifier manuellement dans psql :

```sql
-- Voir les types actuels
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'donnees_enqueteur'
  AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone');
```

Résultat attendu après correction :
```
     column_name         | data_type | character_maximum_length
-------------------------+-----------+--------------------------
 elements_retrouves      | text      | NULL
 code_resultat           | text      | NULL
 flag_etat_civil_errone  | text      | NULL
```

---

## 📁 Fichiers créés

- `CORRIGER_COLONNES_TEXTE.sql` : Script SQL de conversion directe
- `CORRIGER_COLONNES_TEXTE.bat` : Script batch pour exécuter automatiquement
- `CORRECTIF_COLONNES_TEXTE.md` : Cette documentation

---

## 🎯 Pourquoi ça marche maintenant ?

| Méthode | Type intermédiaire | Résultat |
|---------|-------------------|----------|
| Alembic `alter_column` | ❌ VARCHAR(32) | ERREUR |
| Alembic `op.execute(TEXT)` | ❌ VARCHAR(32) | ERREUR |
| **SQL direct** | ✅ Aucun | **SUCCESS** |

PostgreSQL en SQL direct convertit **immédiatement** de VARCHAR(10) vers TEXT sans passer par un type intermédiaire, donc aucune troncature.

---

## ⚠️ Note importante

Cette approche contourne Alembic pour cette migration spécifique, mais marque correctement la migration comme appliquée dans `alembic_version`. Les futures migrations fonctionneront normalement.

---

**Date de création** : 31 décembre 2025  
**Migration concernée** : `007_enlarge_donnees_enqueteur_columns`

