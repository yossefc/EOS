# 🔄 UPGRADE_GUIDE.md - Guide de mise à jour EOS

Guide complet pour mettre à jour l'application EOS chez un client **sans perdre aucune donnée**.

**Version** : 1.0  
**Date** : Décembre 2025  
**Principe** : Mise à jour du **code uniquement**, préservation totale des **données**

---

## 📋 Table des matières

1. [Principe fondamental](#principe-fondamental)
2. [Avant la mise à jour](#avant-la-mise-à-jour)
3. [Procédure de mise à jour standard](#procédure-de-mise-à-jour-standard)
4. [Ajout d'un nouveau client](#ajout-dun-nouveau-client)
5. [Restauration en cas de problème](#restauration-en-cas-de-problème)
6. [Cas spécifiques](#cas-spécifiques)

---

## 🎯 Principe fondamental

### Séparation code/données

```
┌─────────────────────────────────────────────────────┐
│                 APPLICATION EOS                      │
├───────────────────────┬─────────────────────────────┤
│       CODE            │         DONNÉES             │
├───────────────────────┼─────────────────────────────┤
│ • backend/            │ • Base PostgreSQL           │
│ • frontend/           │   - Table clients           │
│ • scripts/            │   - Table donnees           │
│ • migrations/         │   - Table fichiers          │
│ • *.bat, *.md        │   - Enquêtes EOS            │
│                       │   - Autres clients          │
│ ✅ MIS À JOUR         │ ❌ JAMAIS TOUCHÉ           │
└───────────────────────┴─────────────────────────────┘
```

### Ce qui est mis à jour

✅ **Code** (peut être remplacé) :
- Fichiers Python (`backend/*.py`, `backend/routes/*.py`, etc.)
- Fichiers React (`frontend/src/**`)
- Scripts BAT/PowerShell
- Documentation Markdown
- Dépendances (`requirements.txt`, `package.json`)

❌ **Données** (jamais touché directement) :
- Base PostgreSQL `eos_db`
- Toutes les tables et leur contenu
- Schéma de base (sauf ajout non destructif via migrations)

### Les migrations sont non destructives

Les migrations Alembic :
- ✅ **Ajoutent** des colonnes, des tables, des index
- ✅ **Migrent** les données existantes vers le nouveau schéma
- ✅ **Remplissent** les nouvelles colonnes avec des valeurs par défaut
- ❌ **Ne suppriment JAMAIS** de tables ou de données
- ❌ **Ne font JAMAIS** de `TRUNCATE` ou `DELETE` sans WHERE précis

---

## 🛡️ Avant la mise à jour

### Checklist obligatoire

- [ ] **Sauvegarde de la base de données** (CRITIQUE)
- [ ] **Fermer l'application** (backend + frontend)
- [ ] **Noter la version actuelle** (pour la restauration si besoin)
- [ ] **Lire les notes de version** (changelog)

### 1. Sauvegarde de la base de données

**CRITIQUE : À FAIRE ABSOLUMENT AVANT TOUTE MISE À JOUR**

```powershell
# Créer un dossier de sauvegarde
cd D:\EOS
mkdir backups -ErrorAction SilentlyContinue

# Créer un dump complet de la base
$date = Get-Date -Format "yyyy-MM-dd_HHmm"
pg_dump -U eos_user -d eos_db -F c -f "backups\eos_backup_$date.dump"

Write-Host "✅ Sauvegarde créée : backups\eos_backup_$date.dump"
```

**Vérification** :
```powershell
# Le fichier doit exister et avoir une taille > 0
Get-ChildItem backups\eos_backup_*.dump | Select-Object Name, Length, LastWriteTime
```

### 2. Fermer l'application

```powershell
# Fermer les fenêtres backend et frontend
# Ou si lancé en tant que service :
Stop-Service EOSBackend
Stop-Service EOSFrontend
```

### 3. Noter la version actuelle

```powershell
cd D:\EOS\backend
python -c "from app import __version__; print(__version__)"
# Ou vérifier le tag Git
git describe --tags
```

---

## 🚀 Procédure de mise à jour standard

### Méthode A : Via Git (RECOMMANDÉ)

Si vous avez installé via Git, c'est la méthode la plus simple.

#### Étape 1 : Récupérer la nouvelle version

```powershell
cd D:\EOS

# Vérifier l'état actuel
git status

# Si vous avez des modifications locales, les sauvegarder
git stash

# Récupérer la nouvelle version
git fetch origin

# Voir les versions disponibles
git tag

# Passer à la nouvelle version (remplacer v2.0.0 par la version souhaitée)
git checkout tags/v2.0.0
```

#### Étape 2 : Mettre à jour le backend

```powershell
cd D:\EOS\backend

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Mettre à jour les dépendances Python
pip install --upgrade pip
pip install -r requirements.txt

# Appliquer les migrations de base de données
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
flask db upgrade

# Ou utiliser le script de mise à jour automatique
python scripts/upgrade_app.py
```

#### Étape 3 : Mettre à jour le frontend

```powershell
cd D:\EOS\frontend

# Mettre à jour les dépendances npm
npm install

# Optionnel : reconstruire le frontend (si mode production)
npm run build
```

#### Étape 4 : Redémarrer l'application

```powershell
cd D:\EOS
.\start_eos.bat
```

#### Étape 5 : Vérifier la mise à jour

1. **Vérifier la version** :
```powershell
cd D:\EOS\backend
python -c "from app import __version__; print(__version__)"
```

2. **Vérifier la base de données** :
```powershell
python check_db_state.py
```

3. **Tester l'application** :
   - Ouvrir `http://localhost:5173`
   - Aller sur l'onglet "Données"
   - Vérifier que vos enquêtes EOS sont toujours là
   - Tester l'import d'un nouveau fichier

---

### Méthode B : Via archive ZIP

Si vous avez reçu une archive ZIP de la nouvelle version.

#### Étape 1 : Préparer la mise à jour

```powershell
cd D:\

# Renommer l'ancien dossier (backup)
Rename-Item EOS EOS_old

# Extraire la nouvelle version
# (extraire le ZIP manuellement dans D:\EOS)
```

#### Étape 2 : Copier les fichiers de configuration

```powershell
# Copier les fichiers de configuration personnalisés (si vous en aviez)
# Par exemple, si vous aviez changé des mots de passe :
Copy-Item D:\EOS_old\backend\config_custom.py D:\EOS\backend\
```

#### Étape 3 : Recréer l'environnement virtuel

```powershell
cd D:\EOS\backend

# Créer le venv
python -m venv venv

# Activer
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

#### Étape 4 : Appliquer les migrations

```powershell
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# Appliquer les migrations
flask db upgrade

# Ou
python fix_missing_columns.py
```

#### Étape 5 : Installer les dépendances frontend

```powershell
cd D:\EOS\frontend
npm install
```

#### Étape 6 : Redémarrer et vérifier

Même procédure que la Méthode A, Étapes 4-5.

---

## 🏢 Ajout d'un nouveau client

### Scénario

Vous avez développé un nouveau client (ex: `CLIENT_B`) avec un format d'import différent. Vous voulez le déployer chez un client qui a déjà des enquêtes EOS.

### Principe

- Le nouveau client est une **fonctionnalité additionnelle**
- Les données EOS existantes ne sont **jamais touchées**
- La migration ajoute seulement une **ligne dans la table `clients`**

### Procédure

#### Option 1 : Via migration incluse (RECOMMANDÉ)

Si la nouvelle version inclut déjà la migration pour le nouveau client.

```powershell
cd D:\EOS

# 1. Sauvegarde (OBLIGATOIRE)
$date = Get-Date -Format "yyyy-MM-dd_HHmm"
pg_dump -U eos_user -d eos_db -F c -f "backups\eos_backup_$date.dump"

# 2. Récupérer la nouvelle version
git pull origin main  # ou git checkout tags/v2.1.0

# 3. Appliquer la mise à jour
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask db upgrade

# 4. Vérifier que le nouveau client est présent
python -c "from app import create_app; from models import Client; from extensions import db; app = create_app(); app.app_context().push(); print([c.code for c in Client.query.all()])"
# Résultat attendu : ['EOS', 'CLIENT_B']

# 5. Redémarrer
cd ..
.\start_eos.bat
```

#### Option 2 : Ajout manuel d'un nouveau client

Si le nouveau client n'est pas inclus dans une migration, mais que vous avez le code.

```powershell
cd D:\EOS\backend
.\venv\Scripts\Activate.ps1

# Utiliser le script d'ajout de client
python scripts/add_new_client.py --code CLIENT_B --name "Client B" --format TXT_FIXED --interactive

# Le script vous guidera pour :
# 1. Créer le client dans la table `clients`
# 2. Créer le profil d'import
# 3. Configurer les mappings de champs
```

**Alternative SQL** :

Si vous avez un fichier SQL fourni (ex: `add_client_b.sql`) :

```powershell
psql -U eos_user -d eos_db -f add_client_b.sql
```

Exemple de contenu `add_client_b.sql` :
```sql
-- Ajouter le nouveau client
INSERT INTO clients (code, nom, actif, date_creation)
VALUES ('CLIENT_B', 'Client B', true, NOW())
ON CONFLICT (code) DO NOTHING;

-- Ajouter le profil d'import
INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
SELECT id, 'Client B - Format TXT', 'TXT_FIXED', 'utf-8', true, NOW()
FROM clients WHERE code = 'CLIENT_B'
ON CONFLICT DO NOTHING;

-- Ajouter les mappings de champs...
-- (détails spécifiques au client)
```

### Vérification après ajout d'un client

1. **Vérifier dans la base** :
```sql
psql -U eos_user -d eos_db

SELECT * FROM clients;
-- Doit afficher EOS + le nouveau client

\q
```

2. **Vérifier dans l'interface** :
   - Aller sur `http://localhost:5173`
   - Aller sur l'onglet "Import"
   - Le sélecteur de client devrait maintenant afficher 2 clients

3. **Vérifier que les données EOS sont toujours là** :
   - Onglet "Données"
   - Sélectionner client "EOS"
   - Toutes les enquêtes doivent être présentes

---

## 🔧 Restauration en cas de problème

### Si quelque chose ne va pas après la mise à jour

#### Étape 1 : Arrêter l'application

```powershell
# Fermer les fenêtres backend/frontend
# Ou Ctrl+C dans les terminaux
```

#### Étape 2 : Restaurer la base de données

```powershell
cd D:\EOS

# Lister les sauvegardes disponibles
Get-ChildItem backups\eos_backup_*.dump

# Restaurer la sauvegarde (remplacer par le bon fichier)
psql -U eos_user -d eos_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
pg_restore -U eos_user -d eos_db backups\eos_backup_2025-12-11_1430.dump
```

**ATTENTION** : Ceci supprime toutes les données ajoutées depuis la sauvegarde.

#### Étape 3 : Revenir à l'ancienne version du code

**Si via Git** :
```powershell
cd D:\EOS
git checkout tags/v1.0.0  # ou la version précédente
```

**Si via ZIP** :
```powershell
cd D:\
Remove-Item EOS -Recurse -Force
Rename-Item EOS_old EOS
```

#### Étape 4 : Redémarrer

```powershell
cd D:\EOS
.\start_eos.bat
```

---

## 📚 Cas spécifiques

### Mise à jour majeure (changement de version PostgreSQL)

Si la mise à jour nécessite PostgreSQL 17 au lieu de 16 :

1. **Dump complet de la base** :
```powershell
pg_dump -U eos_user -d eos_db > backup_full.sql
```

2. **Installer PostgreSQL 17**

3. **Restaurer la base** :
```powershell
psql -U eos_user -d eos_db < backup_full.sql
```

4. **Suivre la procédure standard de mise à jour**

### Mise à jour avec changement de schéma complexe

Si la migration Alembic échoue avec une erreur complexe :

1. **Ne pas paniquer**
2. **Restaurer la sauvegarde** (voir section Restauration)
3. **Contacter le support** avec :
   - Le message d'erreur complet
   - La version actuelle (`git describe --tags`)
   - La version cible
   - Les logs (`backend/app.log`)

### Mise à jour frontend uniquement

Si seul le frontend a changé (pas de migration backend) :

```powershell
cd D:\EOS

# Récupérer les changements
git pull origin main

# Mettre à jour le frontend
cd frontend
npm install

# Redémarrer seulement le frontend
npm run dev
```

Le backend peut rester en cours d'exécution.

### Mise à jour backend uniquement

Si seul le backend a changé (routes, logique métier, pas de migration) :

```powershell
cd D:\EOS

# Récupérer les changements
git pull origin main

# Mettre à jour le backend
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Redémarrer le backend
python start_with_postgresql.py
```

Le frontend peut rester en cours d'exécution.

---

## 🎯 Bonnes pratiques

### À FAIRE

✅ **Toujours** faire une sauvegarde avant une mise à jour
✅ **Toujours** tester sur une copie de la base en dev avant
✅ **Toujours** lire les notes de version (CHANGELOG)
✅ **Toujours** vérifier que les données sont présentes après mise à jour
✅ Planifier les mises à jour pendant les heures creuses
✅ Garder plusieurs sauvegardes (dernière semaine minimum)

### À NE PAS FAIRE

❌ **Jamais** supprimer manuellement des tables
❌ **Jamais** exécuter `DROP TABLE` ou `TRUNCATE` sans sauvegarde
❌ **Jamais** modifier directement le schéma PostgreSQL
❌ **Jamais** sauter une version (toujours passer par les versions intermédiaires)
❌ **Jamais** mettre à jour sans sauvegarde

---

## 📊 Cycle de mise à jour recommandé

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│  1. SAUVEGARDE (CRITIQUE)                           │
│     pg_dump → backup.dump                           │
│                                                      │
│  2. LECTURE DES NOTES DE VERSION                    │
│     Vérifier ce qui change                          │
│                                                      │
│  3. FERMETURE DE L'APPLICATION                      │
│     Stop backend + frontend                         │
│                                                      │
│  4. MISE À JOUR DU CODE                             │
│     git pull ou extraction ZIP                      │
│                                                      │
│  5. MISE À JOUR DES DÉPENDANCES                     │
│     pip install -r requirements.txt                 │
│     npm install                                     │
│                                                      │
│  6. MIGRATIONS BASE DE DONNÉES                      │
│     flask db upgrade (non destructif)               │
│                                                      │
│  7. REDÉMARRAGE                                     │
│     .\start_eos.bat                                 │
│                                                      │
│  8. VÉRIFICATION                                    │
│     - Données toujours présentes ?                  │
│     - Nouvelles fonctionnalités marchent ?          │
│     - Pas d'erreur dans les logs ?                  │
│                                                      │
│  9. SI OK : Conserver la sauvegarde                 │
│     SI KO : Restaurer (voir section dédiée)        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📞 Support

### En cas de problème

1. **Vérifier les logs** :
```powershell
Get-Content D:\EOS\backend\app.log -Tail 100
```

2. **Vérifier l'état de la base** :
```powershell
cd D:\EOS\backend
python check_db_state.py
```

3. **Restaurer la sauvegarde** si nécessaire (voir section dédiée)

4. **Contacter le support** avec :
   - Message d'erreur complet
   - Logs du backend
   - Version actuelle et cible
   - Sortie de `check_db_state.py`

### Ressources

- **Guide de déploiement** : `DEPLOYMENT_GUIDE.md`
- **Guide multi-client** : `MULTI_CLIENT_GUIDE.md`
- **Configuration multi-utilisateurs** : `CONFIGURATION_MULTI_UTILISATEURS.md`
- **Index de navigation** : `INDEX.md`

---

**Version du guide** : 1.0  
**Dernière mise à jour** : Décembre 2025  
**Application** : EOS - Gestion des enquêtes multi-client

**⚠️ RAPPEL IMPORTANT** : Toujours faire une sauvegarde avant une mise à jour !


