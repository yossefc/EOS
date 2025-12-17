# 📘 APPLICATION EOS - Guide d'installation et d'utilisation

## 📋 Contenu du projet

```
D:\EOS\
├── backend\          # Serveur Python (Flask + PostgreSQL)
├── frontend\         # Interface React
│
├── 00_ajouter_postgresql_au_path.ps1  # 1️⃣ Ajouter PostgreSQL au PATH
├── 01_configurer_postgresql.bat       # 2️⃣ Créer la base de données
├── 02_installer_backend.bat           # 3️⃣ Installer Python + dépendances
├── 03_installer_frontend.bat          # 4️⃣ Installer Node.js + dépendances
│
├── DEMARRER_EOS_POSTGRESQL.bat        # ▶️  DÉMARRER LE BACKEND
│
├── CORRIGER_BDD.bat                   # 🔧 Si problème avec la base
└── REINITIALISER_MAPPINGS.bat         # 🔧 Si problème d'import de fichiers
```

---

## 🚀 PREMIÈRE INSTALLATION (sur un nouvel ordinateur)

### Prérequis

Avant de commencer, installe sur le nouvel ordinateur :

1. **PostgreSQL 17 ou 18** : https://www.postgresql.org/download/windows/
   - Lors de l'installation, note le **mot de passe** du compte `postgres`

2. **Python 3.11+** : https://www.python.org/downloads/
   - ⚠️ **Coche "Add Python to PATH"** pendant l'installation

3. **Node.js LTS** : https://nodejs.org/
   - Prend la version "LTS" (Long Term Support)

---

### Installation en 4 étapes

#### Étape 1 : Ajouter PostgreSQL au PATH

Ouvre PowerShell et tape :

```powershell
cd D:\EOS
.\00_ajouter_postgresql_au_path.ps1
```

📌 **IMPORTANT** : Ferme et rouvre PowerShell après cette étape !

---

#### Étape 2 : Configurer PostgreSQL

```cmd
cd D:\EOS
01_configurer_postgresql.bat
```

Le script va te demander le **mot de passe de postgres**.  
Entre le mot de passe que tu as choisi lors de l'installation de PostgreSQL.

---

#### Étape 3 : Installer le Backend (Python)

```cmd
02_installer_backend.bat
```

Ce script va :
- Créer un environnement virtuel Python
- Installer toutes les dépendances (Flask, SQLAlchemy, psycopg2...)
- Créer les tables dans PostgreSQL

⏱️ Temps estimé : 2-5 minutes

---

#### Étape 4 : Installer le Frontend (React)

```cmd
03_installer_frontend.bat
```

Ce script va installer toutes les dépendances JavaScript (React, Vite, Axios...).

⏱️ Temps estimé : 2-5 minutes

---

## ▶️ DÉMARRER L'APPLICATION

### Backend (Serveur)

**Terminal 1** - Lance le backend :

```cmd
cd D:\EOS
DEMARRER_EOS_POSTGRESQL.bat
```

Tu dois voir :

```
✓ DATABASE_URL définie dans le processus Python
  postgresql+psycopg2://eos_user:eos_password@localh...

 * Running on http://0.0.0.0:5000
```

✅ Le backend est prêt !

---

### Frontend (Interface)

**Terminal 2** - Dans un AUTRE terminal, lance le frontend :

```powershell
cd D:\EOS\frontend
npm run dev
```

Tu dois voir :

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

✅ Le frontend est prêt !

---

### Accéder à l'application

Ouvre ton navigateur et va sur :

**http://localhost:5173**

🎉 L'application EOS est opérationnelle !

---

## 🔧 EN CAS DE PROBLÈME

### Problème 1 : Erreur "psql" non trouvé

**Solution** : Relance le script 00 et ferme/rouvre PowerShell

```powershell
cd D:\EOS
.\00_ajouter_postgresql_au_path.ps1
```

Puis **FERME** PowerShell et **ROUVRE** un nouveau terminal.

---

### Problème 2 : Erreur "ModuleNotFoundError: No module named 'flask'"

**Cause** : L'environnement virtuel n'est pas activé

**Solution** : Utilise `DEMARRER_EOS_POSTGRESQL.bat` au lieu de lancer Python manuellement

---

### Problème 3 : Erreur lors de l'import de fichiers

Si tu vois :

```
ValueError: Aucun mapping trouvé pour le profil d'import 1
```

**Solution** :

```cmd
cd D:\EOS
CORRIGER_BDD.bat
```

Ce script va créer automatiquement le client "EOS" et ses mappings.

---

### Problème 4 : Import avec données décalées ou bizarres

Si les adresses ou noms sont mal parsés :

```cmd
cd D:\EOS
REINITIALISER_MAPPINGS.bat
```

Ce script va recréer les mappings de colonnes avec les bonnes positions.

---

### Problème 5 : Port déjà utilisé

**Erreur** : `Address already in use: Port 5000`

**Solution** : Un autre processus utilise le port. Ferme l'ancien backend ou change le port dans `backend/start_with_postgresql.py` (ligne 20).

---

## 📂 STRUCTURE DU PROJET

### Backend (`backend/`)

- `app.py` - Application Flask principale
- `models/` - Modèles de données (Client, Donnee, Enqueteur...)
- `routes/` - Routes API
- `migrations/` - Migrations Alembic
- `config.py` - Configuration (DATABASE_URL, CORS...)

### Frontend (`frontend/`)

- `src/components/` - Composants React (DataViewer, ImportHandler...)
- `src/App.jsx` - Application principale
- `index.html` - Page d'entrée

---

## 🔐 CONFIGURATION PAR DÉFAUT

### Base de données PostgreSQL

- **Utilisateur** : `eos_user`
- **Mot de passe** : `eos_password`
- **Base** : `eos_db`
- **Hôte** : `localhost`
- **Port** : `5432`

📌 Pour changer ces valeurs, modifie :
- `backend/config.py`
- `01_configurer_postgresql.bat`
- `DEMARRER_EOS_POSTGRESQL.bat`

---

## 📞 AIDE RAPIDE

| Problème | Solution |
|----------|----------|
| PostgreSQL non trouvé | `.\00_ajouter_postgresql_au_path.ps1` puis fermer/rouvrir PowerShell |
| Base de données vide | `02_installer_backend.bat` |
| Erreur d'import | `CORRIGER_BDD.bat` puis `REINITIALISER_MAPPINGS.bat` |
| Backend ne démarre pas | Vérifier que PostgreSQL tourne, utiliser `DEMARRER_EOS_POSTGRESQL.bat` |
| Frontend ne démarre pas | `cd frontend` puis `npm install` |

---

## ✅ CHECKLIST RAPIDE

Installation réussie si tu vois :

- ✅ `psql --version` affiche PostgreSQL 17 ou 18
- ✅ `python --version` affiche Python 3.11+
- ✅ `node --version` affiche Node.js 16+
- ✅ Backend affiche "Running on http://0.0.0.0:5000"
- ✅ Frontend affiche "Local: http://localhost:5173/"
- ✅ L'import de fichiers TXT fonctionne sans erreur

---

**Bon courage ! 🚀**

Si un problème persiste, vérifie les logs affichés dans les terminaux.


