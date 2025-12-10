# 📦 Guide d'installation EOS sur un nouvel ordinateur

Ce guide explique comment installer et configurer l'application EOS sur un nouvel ordinateur.

## 📋 Prérequis

### 1. Logiciels à installer

#### PostgreSQL 16+
- Télécharger : https://www.postgresql.org/download/windows/
- Pendant l'installation :
  - Port : **5432**
  - Mot de passe superutilisateur : notez-le bien !

#### Python 3.11+
- Télécharger : https://www.python.org/downloads/
- ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" lors de l'installation

#### Node.js 18+ (avec npm)
- Télécharger : https://nodejs.org/
- Prendre la version LTS recommandée

#### Git (optionnel)
- Télécharger : https://git-scm.com/download/win

---

## 🚀 Installation du projet

### Étape 1 : Transférer les fichiers

Copiez le dossier complet `EOS` sur le nouvel ordinateur.

**Options de transfert :**
- Clé USB
- Google Drive / OneDrive / Dropbox
- Git (si configuré) : `git clone [url-repository]`
- Réseau local / partage réseau

**Fichiers/dossiers à EXCLURE du transfert** (pour réduire la taille) :
```
backend/instance/           # Base de données locale (à recréer)
backend/__pycache__/        # Cache Python
backend/venv/              # Environnement virtuel Python (à recréer)
frontend/node_modules/     # Dépendances npm (à recréer)
frontend/dist/             # Build frontend
*.pyc                      # Fichiers compilés Python
.env                       # Variables d'environnement (à reconfigurer)
```

### Étape 2 : Configurer PostgreSQL

1. **Ouvrir pgAdmin** ou **psql**

2. **Créer l'utilisateur et la base de données** :

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
```

3. **Vérifier la connexion** :
```bash
psql -U eos_user -d eos_db -h localhost
# Mot de passe : eos_password
```

### Étape 3 : Configurer le Backend Python

Ouvrir PowerShell et naviguer vers le dossier du projet :

```powershell
cd D:\EOS\backend
```

1. **Créer un environnement virtuel** (recommandé) :
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si vous avez une erreur de politique d'exécution :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Installer les dépendances** :
```powershell
pip install -r requirements.txt
```

3. **Configurer la base de données** :
```powershell
# Définir l'URL de la base de données
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# Appliquer les migrations
python fix_missing_columns.py
```

### Étape 4 : Configurer le Frontend

Ouvrir un **nouveau** terminal PowerShell :

```powershell
cd D:\EOS\frontend
```

1. **Installer les dépendances npm** :
```powershell
npm install
```

Cela peut prendre quelques minutes (télécharge ~200 MB de dépendances).

---

## ✅ Vérification de l'installation

### Test Backend
```powershell
cd D:\EOS\backend
python start_with_postgresql.py
```

Vous devriez voir :
```
✓ DATABASE_URL définie
✓ Application Flask créée avec succès
* Running on http://127.0.0.1:5000
```

### Test Frontend
Dans un autre terminal :
```powershell
cd D:\EOS\frontend
npm run dev
```

Vous devriez voir :
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Test de l'application
Ouvrir : http://localhost:5173/

---

## 🎯 Démarrage rapide (après installation)

Une fois l'installation terminée, utilisez le script automatique :

```powershell
# À la racine du projet EOS
.\start_eos.bat
```

Ce script démarre automatiquement :
- ✅ Backend Flask
- ✅ Frontend Vite
- ✅ Navigateur sur http://localhost:5173

---

## 🔄 Migration des données (optionnel)

Si vous voulez transférer les données de l'ancien ordinateur :

### Option 1 : Export/Import PostgreSQL

**Sur l'ancien ordinateur** :
```powershell
pg_dump -U eos_user -d eos_db -F c -f eos_backup.dump
```

**Sur le nouvel ordinateur** :
```powershell
pg_restore -U eos_user -d eos_db eos_backup.dump
```

### Option 2 : Export SQL

**Sur l'ancien ordinateur** :
```powershell
pg_dump -U eos_user -d eos_db > eos_backup.sql
```

**Sur le nouvel ordinateur** :
```powershell
psql -U eos_user -d eos_db < eos_backup.sql
```

---

## ⚙️ Configuration avancée

### Changer le mot de passe PostgreSQL

Si vous avez défini un mot de passe différent :

1. Modifier `backend/start_with_postgresql.py` :
```python
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:VOTRE_MOT_DE_PASSE@localhost:5432/eos_db'
```

2. Modifier `start_eos.bat` :
```batch
set DATABASE_URL=postgresql+psycopg2://eos_user:VOTRE_MOT_DE_PASSE@localhost:5432/eos_db
```

### Changer les ports

**Backend (Flask)** - Modifier `backend/start_with_postgresql.py` :
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Changer 5000
```

**Frontend (Vite)** - Modifier `frontend/vite.config.js` :
```javascript
server: {
  port: 5173,  // Changer 5173
}
```

---

## 🆘 Résolution de problèmes

### Erreur : "pg_config not found"
```powershell
# Installer psycopg2-binary au lieu de psycopg2
pip uninstall psycopg2
pip install psycopg2-binary
```

### Erreur : "Port 5000 already in use"
Un autre processus utilise le port. Trouver et arrêter le processus :
```powershell
netstat -ano | findstr :5000
taskkill /PID [PID] /F
```

### Erreur : "column fichiers.client_id does not exist"
La base de données n'est pas à jour :
```powershell
cd backend
python fix_missing_columns.py
```

### Frontend ne se connecte pas au backend
Vérifier que le backend tourne sur http://localhost:5000 et que le frontend est configuré correctement dans `frontend/src/config.js` ou équivalent.

---

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs dans les terminaux
2. Consulter la documentation dans `MULTI_CLIENT_GUIDE.md`
3. Vérifier l'état de la base : `python backend/check_db_state.py`

---

**Version du guide** : 1.0  
**Dernière mise à jour** : Décembre 2025

