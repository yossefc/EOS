# 🔧 Guide d'installation après correction des migrations

## ✅ Problème résolu

Le problème venait d'un **conflit de migrations Alembic** : deux fichiers de migration portaient le numéro `012`, ce qui créait une erreur lors de l'application des migrations.

### Corrections apportées :

1. ✅ Suppression du fichier en doublon `012_augmenter_taille_tarif_codes.py`
2. ✅ Renommage de la révision `012` en `012_enlarge_tarif_code_columns`
3. ✅ Correction de l'ordre des migrations (009 → 010 → 011 → 012 → 003 → 004)

---

## 📋 Étapes d'installation sur le nouvel ordinateur

### 1️⃣ Vérifier que PostgreSQL est installé et démarré

Sur Git Bash ou PowerShell :

```bash
# Vérifier que PostgreSQL est installé
psql --version

# Si PostgreSQL n'est pas démarré, le démarrer :
# Sur Windows avec les droits admin :
net start postgresql-x64-16
```

### 2️⃣ Configurer la base de données PostgreSQL

Si c'est la première installation sur ce PC :

```sql
-- Se connecter à PostgreSQL en tant qu'utilisateur postgres
psql -U postgres

-- Créer l'utilisateur et la base de données
CREATE USER eos_user WITH PASSWORD 'eos_password';
CREATE DATABASE eos_db OWNER eos_user;
GRANT ALL PRIVILEGES ON DATABASE eos_db TO eos_user;

-- Quitter psql
\q
```

**Alternative** : Si vous utilisez l'utilisateur `postgres` par défaut :

```sql
-- Se connecter à PostgreSQL
psql -U postgres

-- Créer la base de données
CREATE DATABASE eos_db;

-- Quitter
\q
```

### 3️⃣ Configurer la variable d'environnement DATABASE_URL

#### Sur Git Bash :

```bash
# Avec l'utilisateur eos_user (recommandé)
export DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# OU avec l'utilisateur postgres
export DATABASE_URL="postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/eos_db"
```

#### Sur PowerShell :

```powershell
# Avec l'utilisateur eos_user (recommandé)
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# OU avec l'utilisateur postgres
$env:DATABASE_URL="postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/eos_db"
```

⚠️ **Important** : Remplacez `VOTRE_MOT_DE_PASSE` par le mot de passe que vous avez configuré pour PostgreSQL.

### 4️⃣ Appliquer les migrations

Une fois PostgreSQL démarré et la variable `DATABASE_URL` configurée :

```bash
cd D:\eos
python backend/apply_migrations.py
```

Si tout est correct, vous devriez voir :

```
✓ Migration appliquée : ...
✓ Migration appliquée : ...
...
[INFO] Toutes les migrations ont été appliquées avec succès !
```

### 5️⃣ Démarrer l'application

```bash
# Démarrer le backend
python backend/app.py

# Dans un autre terminal, démarrer le frontend
cd frontend
npm run dev
```

---

## 🔍 Résolution des problèmes courants

### Erreur : "password authentication failed for user 'postgres'"

**Solution** : Le mot de passe PostgreSQL est incorrect.

1. Trouvez le mot de passe que vous avez utilisé lors de l'installation de PostgreSQL
2. Mettez à jour la variable `DATABASE_URL` avec le bon mot de passe

**OU** réinitialisez le mot de passe :

```bash
# Sur Windows, en tant qu'administrateur
psql -U postgres
\password postgres
# Entrez le nouveau mot de passe deux fois
```

### Erreur : "Revision 012 is present more than once"

**Solution** : Cette erreur est maintenant **résolue** ! Les fichiers de migration ont été corrigés.

Si vous avez encore cette erreur :
1. Vérifiez que vous utilisez bien les fichiers corrigés (pas une ancienne copie)
2. Supprimez le dossier `backend/migrations/versions/__pycache__/`

```bash
rm -rf backend/migrations/versions/__pycache__
```

### Erreur : "Could not connect to PostgreSQL"

**Solution** : PostgreSQL n'est pas démarré.

```bash
# Démarrer PostgreSQL (Windows, en admin)
net start postgresql-x64-16

# Vérifier que PostgreSQL écoute sur le port 5432
netstat -an | findstr 5432
```

### La base de données existe déjà

Si vous voulez repartir de zéro :

```sql
-- Se connecter à PostgreSQL
psql -U postgres

-- Supprimer et recréer la base
DROP DATABASE IF EXISTS eos_db;
CREATE DATABASE eos_db OWNER eos_user;

-- Quitter
\q
```

Puis réappliquez les migrations :

```bash
python backend/apply_migrations.py
```

---

## 📝 Ordre des migrations (pour référence)

L'ordre correct des migrations après correction :

```
001_initial
    ↓
002_multi_client (support multi-client)
    ↓
009 (add_naissance_maj)
    ↓
010 (remove_naissance_from_donnee_enqueteur)
    ↓
011 (partner_tables)
    ↓
012_enlarge_tarif_code_columns (agrandir colonnes tarif)
    ↓
003_client_id_facturation
    ↓
004_tarif_enqueteur_client
```

---

## ✅ Vérification finale

Une fois les migrations appliquées, vérifiez que tout fonctionne :

```bash
# Vérifier les tables créées
psql -U postgres -d eos_db -c "\dt"

# Vous devriez voir toutes les tables :
# - clients
# - import_profiles
# - import_field_mappings
# - fichiers
# - donnees
# - donnees_enqueteur
# - enquete_facturation
# - tarifs_enqueteur
# - partner_request_keywords
# - partner_case_requests
# - partner_tarif_rules
# - etc.
```

---

## 🎯 Résumé rapide

```bash
# 1. Démarrer PostgreSQL (si nécessaire)
net start postgresql-x64-16

# 2. Configurer DATABASE_URL
export DATABASE_URL="postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/eos_db"

# 3. Appliquer les migrations
python backend/apply_migrations.py

# 4. Démarrer l'application
python backend/app.py
```

---

🎉 **C'est terminé !** Votre application devrait maintenant fonctionner correctement sur le nouvel ordinateur.

