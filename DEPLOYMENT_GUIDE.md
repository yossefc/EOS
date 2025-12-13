# 📘 DEPLOYMENT_GUIDE.md - Guide de déploiement EOS

Guide complet pour installer et déployer l'application EOS chez un client (acheteur du logiciel).

**Version** : 1.0  
**Date** : Décembre 2025  
**Base de données** : PostgreSQL obligatoire

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis système](#prérequis-système)
3. [Installation initiale](#installation-initiale)
4. [Configuration](#configuration)
5. [Premier démarrage](#premier-démarrage)
6. [Vérification de l'installation](#vérification-de-linstallation)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Vue d'ensemble

### Architecture de l'application

```
┌─────────────────────────────────────────────────────┐
│                  EOS APPLICATION                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌───────────────┐         ┌──────────────────┐   │
│  │   Frontend    │ ←────→  │    Backend API    │   │
│  │   (React)     │  HTTP   │    (Flask)        │   │
│  │  Port: 5173   │         │   Port: 5000      │   │
│  └───────────────┘         └──────────────────┘   │
│                                      │              │
│                                      ↓              │
│                            ┌──────────────────┐   │
│                            │   PostgreSQL     │   │
│                            │   Port: 5432     │   │
│                            └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Composants

- **Frontend** : Interface React + Vite (gestion des enquêtes, imports, exports)
- **Backend** : API Flask + SQLAlchemy (logique métier, accès base de données)
- **Base de données** : PostgreSQL (stockage des enquêtes, clients, configurations)

---

## 💻 Prérequis système

### Configuration minimale recommandée

- **OS** : Windows 10/11 (64-bit) ou Windows Server 2016+
- **RAM** : 4 GB minimum (8 GB recommandé)
- **Disque** : 2 GB d'espace libre (+ espace pour les données)
- **Processeur** : Intel Core i3 ou équivalent

### Logiciels à installer

#### 1. PostgreSQL 16+

**Téléchargement** : https://www.postgresql.org/download/windows/

**Installation** :
- Accepter les paramètres par défaut
- **IMPORTANT** : Notez le mot de passe du superutilisateur `postgres`
- Port par défaut : `5432`
- Locale : `French, France` ou `English, United States`

**Vérification** :
```powershell
psql --version
# Résultat attendu : psql (PostgreSQL) 16.x
```

#### 2. Python 3.11+

**Téléchargement** : https://www.python.org/downloads/

**Installation** :
- ⚠️ **CRITIQUE** : Cocher **"Add Python to PATH"**
- Cocher "Install for all users" (optionnel)
- Installation personnalisée : inclure pip, tcl/tk, documentation

**Vérification** :
```powershell
python --version
# Résultat attendu : Python 3.11.x ou 3.12.x

pip --version
# Résultat attendu : pip 23.x ou supérieur
```

#### 3. Node.js 18+ (LTS)

**Téléchargement** : https://nodejs.org/

**Installation** :
- Prendre la version **LTS (Long Term Support)**
- Accepter les paramètres par défaut
- Installation automatique des outils de compilation (optionnel)

**Vérification** :
```powershell
node --version
# Résultat attendu : v18.x.x ou v20.x.x

npm --version
# Résultat attendu : 9.x.x ou 10.x.x
```

#### 4. Git (optionnel mais recommandé)

**Téléchargement** : https://git-scm.com/download/win

**Installation** :
- Accepter les paramètres par défaut
- Recommandé : "Use Git from Git Bash only"

---

## 🚀 Installation initiale

### Méthode A : Installation automatisée (RECOMMANDÉ)

Le projet inclut des scripts d'installation automatique qui simplifient grandement le processus.

#### Étape 1 : Récupérer les fichiers

**Option 1 - Via Git** (recommandé) :
```powershell
cd D:\
git clone https://github.com/yossefc/EOS.git
cd EOS
```

**Option 2 - Via archive ZIP** :
1. Télécharger l'archive EOS depuis GitHub (ou reçue par email)
2. Extraire dans `D:\EOS` (ou un autre emplacement de votre choix)
3. Ouvrir PowerShell et naviguer vers le dossier :
   ```powershell
   cd D:\EOS
   ```

#### Étape 2 : Exécuter les scripts d'installation

Les scripts d'installation sont numérotés dans l'ordre d'exécution :

```powershell
# Script 1 : Configuration PostgreSQL
.\01_configurer_postgresql.bat
# Ce script crée :
# - L'utilisateur eos_user
# - La base de données eos_db
# - Les privilèges nécessaires

# Script 2 : Installation du backend
.\02_installer_backend.bat
# Ce script :
# - Crée un environnement virtuel Python
# - Installe toutes les dépendances Python
# - Initialise la base de données
# - Crée le client EOS par défaut

# Script 3 : Installation du frontend
.\03_installer_frontend.bat
# Ce script :
# - Installe toutes les dépendances npm
# - Prépare le frontend React
```

#### Étape 3 : Démarrage de l'application

```powershell
# Démarrage automatique (backend + frontend + navigateur)
.\start_eos.bat
```

L'application devrait s'ouvrir automatiquement dans votre navigateur sur `http://localhost:5173`.

---

### Méthode B : Installation manuelle détaillée

Si vous préférez une installation manuelle ou si les scripts automatiques ne fonctionnent pas.

#### Étape 1 : Configuration PostgreSQL

1. **Ouvrir psql** (menu Démarrer → PostgreSQL → SQL Shell)

2. **Se connecter** :
   - Server : `localhost` (Entrée)
   - Database : `postgres` (Entrée)
   - Port : `5432` (Entrée)
   - Username : `postgres` (Entrée)
   - Password : *votre mot de passe postgres*

3. **Créer l'utilisateur et la base** :

```sql
-- Créer l'utilisateur
CREATE USER eos_user WITH PASSWORD 'eos_password';

-- Créer la base de données
CREATE DATABASE eos_db OWNER eos_user;

-- Donner tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE eos_db TO eos_user;

-- Se connecter à la base eos_db
\c eos_db

-- Donner les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO eos_user;

-- Quitter
\q
```

4. **Vérifier la connexion** :

```powershell
psql -U eos_user -d eos_db -h localhost
# Mot de passe : eos_password
# Si ça se connecte, tapez \q pour quitter
```

#### Étape 2 : Installation du Backend

1. **Naviguer vers le dossier backend** :

```powershell
cd D:\EOS\backend
```

2. **Créer un environnement virtuel** :

```powershell
python -m venv venv
```

3. **Activer l'environnement virtuel** :

```powershell
.\venv\Scripts\Activate.ps1
```

Si vous avez une erreur de politique d'exécution :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. **Installer les dépendances** :

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configurer la variable d'environnement DATABASE_URL** :

```powershell
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
```

6. **Initialiser la base de données** :

```powershell
python fix_missing_columns.py
```

Vous devriez voir :
```
✅ Base de données mise à jour avec succès !
✅ Client EOS créé (ID: 1)
✅ Profil d'import EOS configuré
```

#### Étape 3 : Installation du Frontend

1. **Ouvrir un NOUVEAU terminal PowerShell**

2. **Naviguer vers le dossier frontend** :

```powershell
cd D:\EOS\frontend
```

3. **Installer les dépendances npm** :

```powershell
npm install
```

Cela peut prendre 3-5 minutes (télécharge ~300 MB de dépendances).

---

## ⚙️ Configuration

### Configuration de base

La configuration par défaut devrait fonctionner immédiatement. Voici les paramètres principaux :

#### Backend (`backend/config.py`)

```python
# Base de données
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

# CORS (autorisations frontend)
CORS_ORIGINS = 'http://localhost:5173'

# Port du backend
PORT = 5000
```

#### Frontend (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  server: {
    port: 5173,
  }
})
```

### Configuration personnalisée

#### Changer le mot de passe PostgreSQL

Si vous voulez utiliser un mot de passe différent :

1. **Dans PostgreSQL** :
```sql
ALTER USER eos_user WITH PASSWORD 'votre_nouveau_mot_de_passe';
```

2. **Dans `backend/start_with_postgresql.py`** :
```python
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:votre_nouveau_mot_de_passe@localhost:5432/eos_db'
```

3. **Dans `start_eos.bat`** :
```batch
set DATABASE_URL=postgresql+psycopg2://eos_user:votre_nouveau_mot_de_passe@localhost:5432/eos_db
```

#### Changer les ports

**Backend (port 5000)** :

Modifier `backend/start_with_postgresql.py` :
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Changer 5000
```

**Frontend (port 5173)** :

Modifier `frontend/vite.config.js` :
```javascript
server: {
  port: 5173,  // Changer 5173
}
```

---

## 🎬 Premier démarrage

### Démarrage automatique (RECOMMANDÉ)

```powershell
cd D:\EOS
.\start_eos.bat
```

Ce script :
1. ✅ Vérifie que Python et Node.js sont installés
2. ✅ Démarre le backend Flask (nouvelle fenêtre)
3. ✅ Démarre le frontend Vite (nouvelle fenêtre)
4. ✅ Ouvre automatiquement le navigateur sur `http://localhost:5173`

**Attendez 10-15 secondes** pour que tout démarre.

### Démarrage manuel

Si vous préférez démarrer manuellement (pour le développement ou le débogage) :

**Terminal 1 - Backend** :
```powershell
cd D:\EOS\backend
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
python start_with_postgresql.py
```

**Terminal 2 - Frontend** :
```powershell
cd D:\EOS\frontend
npm run dev
```

**Navigateur** :
Ouvrir `http://localhost:5173`

---

## ✅ Vérification de l'installation

### 1. Vérifier le backend

Ouvrir `http://localhost:5000/api/stats` dans un navigateur.

**Résultat attendu** : Un JSON avec des statistiques
```json
{
  "total_donnees": 0,
  "total_enqueteurs": 0,
  "total_fichiers": 0,
  "clients": [
    {"id": 1, "code": "EOS", "nom": "EOS France"}
  ]
}
```

### 2. Vérifier le frontend

Ouvrir `http://localhost:5173` dans un navigateur.

**Résultat attendu** :
- ✅ L'interface EOS s'affiche
- ✅ Onglets visibles : Données, Import, Enquêteurs, etc.
- ✅ Pas d'erreur dans la console du navigateur (F12)

### 3. Vérifier la base de données

```powershell
cd D:\EOS\backend
python check_db_state.py
```

**Résultat attendu** :
```
✅ client_id existe dans fichiers
✅ client_id existe dans donnees
✅ 1 client EOS créé
✅ Version Alembic : 002_multi_client
```

### 4. Test fonctionnel complet

1. **Aller sur l'onglet "Import"**
2. **Sélectionner un fichier de test** (TXT format EOS)
3. **Cliquer sur "Importer"**
4. **Aller sur l'onglet "Données"**
5. **Vérifier que les données apparaissent**

Si toutes ces étapes fonctionnent : ✅ **Installation réussie !**

---

## 🆘 Troubleshooting

### Problème : "psql n'est pas reconnu comme commande"

**Cause** : PostgreSQL n'est pas dans le PATH.

**Solution** :
1. Trouver l'installation PostgreSQL (ex: `C:\Program Files\PostgreSQL\16\bin`)
2. Ajouter au PATH système :
   - Panneau de configuration → Système → Paramètres système avancés
   - Variables d'environnement → Path → Modifier
   - Ajouter `C:\Program Files\PostgreSQL\16\bin`
3. Redémarrer PowerShell

### Problème : "python n'est pas reconnu comme commande"

**Cause** : Python n'a pas été installé avec "Add to PATH".

**Solution** :
1. Désinstaller Python
2. Réinstaller en cochant **"Add Python to PATH"**
3. Ou ajouter manuellement au PATH (comme PostgreSQL ci-dessus)

### Problème : "Port 5000 already in use"

**Cause** : Un autre processus utilise le port 5000.

**Solution** :
```powershell
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID [PID] /F
```

### Problème : "column fichiers.client_id does not exist"

**Cause** : La base de données n'est pas à jour.

**Solution** :
```powershell
cd D:\EOS\backend
python fix_missing_columns.py
```

### Problème : Frontend ne se connecte pas au backend

**Vérification** :
1. Le backend tourne-t-il ? (fenêtre "EOS Backend" ouverte)
2. Tester : `http://localhost:5000/api/stats` dans le navigateur
3. Vérifier la console du navigateur (F12) pour les erreurs CORS

**Solution** :
- Redémarrer le backend
- Vérifier que `CORS_ORIGINS` inclut `http://localhost:5173` dans `backend/config.py`

### Problème : "pg_config not found" lors de pip install

**Solution** :
```powershell
pip uninstall psycopg2
pip install psycopg2-binary
```

### Problème : Erreur de politique d'exécution PowerShell

**Solution** :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📞 Support

### Ressources

- **Documentation complète** : Voir `INDEX.md` pour naviguer dans tous les guides
- **Configuration multi-utilisateurs** : Voir `CONFIGURATION_MULTI_UTILISATEURS.md`
- **Guide de mise à jour** : Voir `UPGRADE_GUIDE.md`
- **Guide multi-client** : Voir `MULTI_CLIENT_GUIDE.md`

### Diagnostic rapide

```powershell
# Vérifier l'état de la base
cd D:\EOS\backend
python check_db_state.py

# Voir les logs du backend
Get-Content D:\EOS\backend\app.log -Tail 50

# Vérifier les versions
python --version
node --version
psql --version
```

### Contacts

Pour toute question ou problème technique, consulter la documentation dans le dossier `D:\EOS\` ou contacter le support.

---

## 📝 Notes importantes

1. **Sauvegarde** : Pensez à sauvegarder régulièrement votre base de données PostgreSQL
   ```powershell
   pg_dump -U eos_user -d eos_db -F c -f backup_eos.dump
   ```

2. **Mises à jour** : Ne jamais supprimer manuellement des tables ou données
   - Toujours suivre le guide `UPGRADE_GUIDE.md`
   - Les mises à jour sont conçues pour préserver vos données

3. **Performance** : Pour de meilleures performances avec de nombreuses enquêtes
   - Minimum 8 GB RAM recommandé
   - SSD recommandé pour PostgreSQL

4. **Sécurité** : Changez les mots de passe par défaut (`eos_password`) en production

---

**Version du guide** : 1.0  
**Dernière mise à jour** : Décembre 2025  
**Application** : EOS - Gestion des enquêtes multi-client

