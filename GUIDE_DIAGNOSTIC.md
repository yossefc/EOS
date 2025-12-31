# 📋 GUIDE D'UTILISATION : DIAGNOSTIC BASE DE DONNÉES

## 🎯 Objectif

Ce script génère un rapport complet de l'état de votre base de données EOS pour :
- ✅ Vérifier que toutes les tables existent
- ✅ Vérifier que toutes les relations (Foreign Keys) sont en place
- ✅ Vérifier que les clients et profils d'import sont configurés
- ✅ Comparer deux installations (ordinateur 1 vs ordinateur 2)
- ✅ Identifier rapidement ce qui manque

---

## 🚀 Utilisation

### Sur CET ordinateur (qui marche)

```bash
./DIAGNOSTIC_BASE_DONNEES.bat
```

Cela va créer un fichier `RAPPORT_DIAGNOSTIC.txt` qui s'ouvrira automatiquement.

### Sur l'AUTRE ordinateur (à réparer)

```bash
./DIAGNOSTIC_BASE_DONNEES.bat
```

Cela va créer un fichier `RAPPORT_DIAGNOSTIC_AUTRE.txt` (renommez-le manuellement).

---

## 📊 Contenu du rapport

Le rapport contient **12 sections** :

### 1. **Version Alembic**
- Quelle migration est actuellement appliquée
- Exemple : `007_enq_cols` ou `008_tarifs_client`

### 2. **Tables principales**
- Liste toutes les tables requises (16 tables)
- Indique si elles existent (✅) ou manquent (❌)
- Nombre de colonnes par table

### 3. **Relations (Foreign Keys)**
- Nombre total de Foreign Keys
- Détail par table

### 4. **Index**
- Nombre total d'index créés

### 5. **Clients**
- Liste des clients configurés (EOS, PARTNER, etc.)
- Statut actif/inactif

### 6. **Profils d'import**
- Pour chaque client, les profils d'import configurés
- Nombre de mappings de champs

### 7. **Tarifs client**
- Liste des tarifs PARTNER (code lettre, montant)
- Vérifie que la table `tarifs_client` existe

### 8. **Options de confirmation**
- Options pour les résultats (POS, NEG, etc.)
- Options pour les éléments retrouvés

### 9. **Colonnes PARTNER dans `donnees`**
- Vérifie que les 6 colonnes PARTNER existent :
  - `tarif_lettre`
  - `recherche`
  - `instructions`
  - `date_jour`
  - `nom_complet`
  - `motif`

### 10. **Colonnes texte dans `donnees_enqueteur`**
- Vérifie que les colonnes sont en TEXT (pas VARCHAR(10)) :
  - `elements_retrouves`
  - `code_resultat`
  - `flag_etat_civil_errone`

### 11. **Statistiques générales**
- Nombre de lignes dans chaque table principale

### 12. **Résumé final**
- ✅/❌ pour chaque élément critique
- Actions à faire si quelque chose manque

---

## 🔍 Interpréter le résumé final

Exemple de résumé :

```
✅ Table tarifs_client          | OK
✅ Table confirmation_options   | OK
✅ Colonnes PARTNER dans donnees| OK
❌ Colonnes TEXT dans donnees_enqueteur | MANQUANT - Exécuter CORRIGER_COLONNES_TEXTE.bat
✅ Client PARTNER configuré     | OK
✅ Profil import PARTNER        | OK
```

**Si vous voyez des ❌**, suivez les actions indiquées.

---

## 📥 Comparer deux installations

1. **Sur CET ordinateur** :
   ```bash
   ./DIAGNOSTIC_BASE_DONNEES.bat
   ```
   Renommez le fichier : `RAPPORT_DIAGNOSTIC_ORDINATEUR_1.txt`

2. **Sur l'AUTRE ordinateur** :
   ```bash
   ./DIAGNOSTIC_BASE_DONNEES.bat
   ```
   Renommez le fichier : `RAPPORT_DIAGNOSTIC_ORDINATEUR_2.txt`

3. **Comparez les deux fichiers** avec un outil de diff :
   - Notepad++ (Plugin "Compare")
   - WinMerge
   - VS Code (Compare files)

---

## 🛠️ Actions correctives

Si le diagnostic révèle des problèmes, voici les scripts à exécuter :

| Problème détecté | Script à exécuter |
|------------------|-------------------|
| ❌ Table `tarifs_client` manquante | `CONFIGURER_TARIFS_PARTNER.bat` |
| ❌ Table `confirmation_options` manquante | `APPLIQUER_MIGRATIONS_SIMPLE.bat` |
| ❌ Colonnes PARTNER manquantes | `APPLIQUER_MIGRATIONS_PARTNER.bat` |
| ❌ Colonnes pas en TEXT | `CORRIGER_COLONNES_TEXTE.bat` |
| ❌ Client PARTNER manquant | `CONFIGURER_PARTNER.bat` |
| ❌ Profil import PARTNER manquant | `CONFIGURER_PARTNER.bat` |

---

## 📁 Fichiers créés

- `DIAGNOSTIC_BASE_DONNEES.sql` : Script SQL de diagnostic
- `DIAGNOSTIC_BASE_DONNEES.bat` : Script batch pour exécuter le diagnostic
- `RAPPORT_DIAGNOSTIC.txt` : Rapport généré (créé à chaque exécution)

---

## ⚠️ Pré-requis

- PostgreSQL doit être démarré
- La base de données `eos_db` doit exister
- L'utilisateur `postgres` doit avoir accès à la base

---

## 💡 Conseil

**Exécutez ce diagnostic AVANT et APRÈS chaque correction** pour vérifier que le problème est résolu.

---

**Date de création** : 31 décembre 2025

