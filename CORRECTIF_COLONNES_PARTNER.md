# 🔧 CORRECTIF - Colonnes PARTNER manquantes

## ❌ Problème sur l'ancien ordinateur

Lorsque vous lancez l'application, vous obtenez l'erreur :
```
psycopg2.errors.UndefinedColumn: ERREUR: la colonne donnees.tarif_lettre n'existe pas
```

## 🔍 Cause

Les colonnes PARTNER ont été ajoutées au modèle `Donnee` dans le code, mais la migration pour les créer dans la base de données n'avait jamais été générée.

**Colonnes manquantes :**
- `tarif_lettre` - Code lettre du tarif (A, B, C, etc.)
- `recherche` - Texte de recherche PARTNER
- `instructions` - Instructions particulières
- `date_jour` - Date du jour
- `nom_complet` - Nom complet formaté
- `motif` - Motif de la demande

---

## ✅ Solution

### Sur l'ANCIEN ordinateur (celui qui a l'erreur)

**Option 1 : Script automatique (RECOMMANDÉ)**

Double-cliquez sur :
```
APPLIQUER_MIGRATIONS_PARTNER.bat
```

**Option 2 : Manuellement**

```bash
# 1. Configurer DATABASE_URL
set DATABASE_URL=postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db

# 2. Appliquer les migrations
cd D:\eos
python backend/apply_migrations.py
```

Vous devriez voir :
```
✓ Colonne tarif_lettre ajoutée
✓ Colonne recherche ajoutée
✓ Colonne instructions ajoutée
✓ Colonne date_jour ajoutée
✓ Colonne nom_complet ajoutée
✓ Colonne motif ajoutée
✅ Migration 005 : Colonnes PARTNER ajoutées à la table donnees
```

### Sur le NOUVEL ordinateur

Rien à faire ! Les migrations ont déjà été appliquées lors de l'installation initiale.

---

## 📋 Ordre des migrations (mis à jour)

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
  ↓
005_add_partner_columns ← NOUVEAU !
```

---

## ✅ Vérification

Pour vérifier que toutes les migrations sont appliquées :

```bash
python verifier_migrations.py
```

Vous devriez voir :
```
✓ 9 fichiers de migration trouvés
✓ Pas d'erreurs détectées !
```

---

## 🔄 Synchronisation entre les ordinateurs

Pour éviter ce genre de problème à l'avenir :

### Sur l'ordinateur où vous développez :

```bash
# 1. Commiter la nouvelle migration
git add backend/migrations/versions/005_add_partner_columns.py
git commit -m "Ajout migration 005 : colonnes PARTNER dans table donnees"

# 2. Pousser vers GitHub
git push origin master
```

### Sur l'autre ordinateur :

```bash
# 1. Récupérer les mises à jour
git pull origin master

# 2. Appliquer les nouvelles migrations
python backend/apply_migrations.py
```

---

## 📝 Fichiers créés

1. **005_add_partner_columns.py** - Migration pour ajouter les colonnes PARTNER
2. **APPLIQUER_MIGRATIONS_PARTNER.bat** - Script automatique
3. **CORRECTIF_COLONNES_PARTNER.md** - Ce fichier (documentation)

---

## 🎯 Résumé rapide

**Sur l'ancien ordinateur :**
1. Lancez `APPLIQUER_MIGRATIONS_PARTNER.bat`
2. Redémarrez l'application
3. ✅ L'erreur devrait disparaître !

**Sur le nouvel ordinateur :**
- Rien à faire, déjà à jour ! ✅

---

**Date** : 31 décembre 2025  
**Migration ajoutée** : 005_add_partner_columns  
**Statut** : Testé et validé

