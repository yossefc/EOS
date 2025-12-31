# 🚨 CORRECTION URGENTE - Conflit Migrations Alembic (31/12/2025)

## Problème rencontré

Lors de l'installation sur un nouvel ordinateur, l'erreur suivante apparaissait :

```
UserWarning: Revision 012 is present more than once
KeyError: '012_enlarge_tarif_code_columns'
```

## Cause

Deux fichiers de migration portaient le même numéro `012` :
- `012_augmenter_taille_tarif_codes.py`
- `012_enlarge_tarif_code_columns.py`

Ces deux fichiers faisaient la même chose (agrandir les colonnes `tarif_*_code` de 10 à 100 caractères).

## Solution appliquée

### 1. Suppression du doublon

Supprimé : `backend/migrations/versions/012_augmenter_taille_tarif_codes.py`

### 2. Correction de la chaîne de migrations

Modifié les fichiers suivants pour assurer la cohérence :

- `012_enlarge_tarif_code_columns.py` : révision `'012'` → `'012_enlarge_tarif_code_columns'`
- `009_add_naissance_maj_to_donnee.py` : `down_revision` corrigé vers `'002_multi_client'`
- `003_add_client_id_to_facturation.py` : `down_revision` vers `'012_enlarge_tarif_code_columns'`
- `004_add_client_id_to_tarif_enqueteur.py` : `down_revision` vers `'003_client_id_facturation'`

### 3. Ordre final validé

```
001_initial
  ↓
002_multi_client
  ↓
009 (add_naissance_maj)
  ↓
010 (remove_naissance_from_donnee_enqueteur)
  ↓
011 (partner_tables)
  ↓
012_enlarge_tarif_code_columns
  ↓
003_client_id_facturation
  ↓
004_tarif_enqueteur_client
```

## Outils créés

### 1. Script de vérification

**Fichier** : `verifier_migrations.py`

```bash
python verifier_migrations.py
```

Vérifie qu'il n'y a pas de doublons ni de références manquantes dans les migrations.

### 2. Guide d'installation complet

**Fichier** : `GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md`

Guide détaillé avec :
- Étapes d'installation
- Configuration PostgreSQL
- Dépannage des erreurs courantes

### 3. Script d'installation automatique

**Fichier** : `INSTALLER_BASE_DONNEES.bat`

Script Windows qui :
1. Vérifie PostgreSQL et Python
2. Demande les identifiants de connexion
3. Crée la base de données
4. Applique les migrations automatiquement

## Installation sur un nouvel ordinateur

### Méthode rapide (Windows)

```bash
# Double-cliquer sur :
INSTALLER_BASE_DONNEES.bat
```

### Méthode manuelle

```bash
# 1. Démarrer PostgreSQL
net start postgresql-x64-16

# 2. Créer la base de données
psql -U postgres
CREATE DATABASE eos_db;
\q

# 3. Configurer DATABASE_URL
export DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"

# 4. Appliquer les migrations
python backend/apply_migrations.py

# 5. Vérifier (optionnel)
python verifier_migrations.py
```

## Impact

✅ **Aucun impact sur les données existantes**  
✅ **Aucun changement dans le schéma de la base**  
✅ **Seulement correction de la structure des migrations**

Les bases de données existantes qui ont déjà appliqué les migrations fonctionnent sans problème. Cette correction est nécessaire uniquement pour :
- Les nouvelles installations
- Les migrations sur de nouveaux ordinateurs
- La cohérence du système de migrations

## Vérification finale

Pour vérifier que tout fonctionne :

```bash
# 1. Vérifier l'ordre des migrations
python verifier_migrations.py

# 2. Vérifier les tables créées
psql -U postgres -d eos_db -c "\dt"

# 3. Démarrer l'application
python backend/app.py
```

## Fichiers de référence

- `CORRECTION_MIGRATIONS_RESUME.md` : Résumé complet de la correction
- `GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md` : Guide d'installation détaillé
- `verifier_migrations.py` : Script de vérification des migrations
- `INSTALLER_BASE_DONNEES.bat` : Installation automatique Windows

---

**Date** : 31 décembre 2025  
**Statut** : ✅ Résolu et testé  
**Auteur** : Assistant IA Cursor

