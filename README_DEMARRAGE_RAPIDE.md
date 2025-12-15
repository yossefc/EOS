# 🚀 EOS - Démarrage Rapide

Application de gestion des enquêtes avec support multi-client et base de données PostgreSQL.

---

## 🎯 Démarrage en 10 secondes

**Si l'application est déjà installée** :

```powershell
# Double-cliquez sur ce fichier :
start_eos.bat
```

✨ L'application démarre automatiquement et ouvre le navigateur !

---

## 📦 Première installation

### Étape 1 : Prérequis (à installer une seule fois)

1. **PostgreSQL 16+** : https://www.postgresql.org/download/
2. **Python 3.11+** : https://www.python.org/downloads/ ⚠️ Cocher "Add to PATH"
3. **Node.js 18+** : https://nodejs.org/

### Étape 2 : Configuration PostgreSQL

Ouvrir **pgAdmin** ou **psql** et exécuter :

```sql
CREATE USER eos_user WITH PASSWORD 'eos_password';
CREATE DATABASE eos_db OWNER eos_user;
GRANT ALL PRIVILEGES ON DATABASE eos_db TO eos_user;
\c eos_db
GRANT ALL ON SCHEMA public TO eos_user;
```

### Étape 3 : Installation des dépendances

**Backend Python** :
```powershell
cd backend
pip install -r requirements.txt
python fix_missing_columns.py
```

**Frontend Node** :
```powershell
cd frontend
npm install
```

### Étape 4 : Lancer l'application

```powershell
# À la racine du projet
.\start_eos.bat
```

🎉 C'est tout ! L'application s'ouvre automatiquement.

---

## 📚 Documentation complète

| Fichier | Description |
|---------|-------------|
| `GUIDE_INSTALLATION.md` | Guide d'installation détaillé étape par étape |
| `TRANSFERT_PROJET.md` | Comment transférer le projet vers un autre PC |
| `MULTI_CLIENT_GUIDE.md` | Guide d'utilisation du système multi-client |
| `MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md` | Documentation technique complète |

---

## 🔧 Commandes utiles

### Démarrage manuel

**Backend** :
```powershell
cd backend
python start_with_postgresql.py
# → http://localhost:5000
```

**Frontend** :
```powershell
cd frontend
npm run dev
# → http://localhost:5173
```

### Vérifications

**État de la base de données** :
```powershell
cd backend
python check_db_state.py
```

**Corriger la base de données** :
```powershell
cd backend
python fix_missing_columns.py
```

---

## 📤 Transférer vers un autre ordinateur

### Méthode 1 : Script automatique (Recommandé)

```powershell
.\creer_archive_transfert.ps1
```

Cela crée une archive ZIP propre (~5-10 MB) prête à transférer.

### Méthode 2 : Copie manuelle

**Fichiers à copier** :
- ✅ `backend/` (SANS venv)
- ✅ `frontend/` (SANS node_modules)
- ✅ `*.md`
- ✅ `start_eos.bat`

**Fichiers à EXCLURE** (seront recréés) :
- ❌ `backend/venv/`
- ❌ `backend/__pycache__/`
- ❌ `frontend/node_modules/`
- ❌ `frontend/dist/`

Sur le nouvel ordinateur : Suivre `GUIDE_INSTALLATION.md`

---

## 🆘 Problèmes fréquents

### ❌ "Port 5000 already in use"
```powershell
# Trouver et tuer le processus
netstat -ano | findstr :5000
taskkill /PID [PID] /F
```

### ❌ "column fichiers.client_id does not exist"
```powershell
cd backend
python fix_missing_columns.py
```

### ❌ "Module not found"
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### ❌ "Cannot connect to database"
Vérifier :
1. PostgreSQL est démarré
2. L'utilisateur `eos_user` existe
3. La base `eos_db` existe
4. Le mot de passe est correct dans `backend/start_with_postgresql.py`

---

## 📊 Structure du projet

```
EOS/
├── backend/                    # API Flask + PostgreSQL
│   ├── app.py                 # Application principale
│   ├── models/                # Modèles de données
│   ├── routes/                # Routes API
│   ├── migrations/            # Migrations Alembic
│   ├── start_with_postgresql.py
│   ├── fix_missing_columns.py
│   └── requirements.txt
├── frontend/                   # Interface React + Vite
│   ├── src/
│   │   ├── components/        # Composants React
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── start_eos.bat              # ⭐ Script de démarrage automatique
├── creer_archive_transfert.ps1 # Créer archive de transfert
├── GUIDE_INSTALLATION.md      # Guide d'installation complet
├── TRANSFERT_PROJET.md        # Guide de transfert
└── README_DEMARRAGE_RAPIDE.md # Ce fichier
```

---

## 🌟 Fonctionnalités principales

- ✅ **Multi-client** : Gérer plusieurs clients avec profils d'import personnalisés
- ✅ **Import flexible** : TXT fixe, CSV, Excel avec mapping configurable
- ✅ **Gestion des enquêtes** : Assignation, suivi, validation
- ✅ **Exports personnalisables** : Word, CSV, Excel
- ✅ **Base PostgreSQL** : Scalable jusqu'à 50 000+ enquêtes
- ✅ **Interface moderne** : React + Vite + Tailwind CSS

---

## 📞 Support

1. **Documentation** : Voir les fichiers `*.md`
2. **Vérifier les logs** : Dans les fenêtres Backend et Frontend
3. **Diagnostic DB** : `python backend/check_db_state.py`

---

## 🔄 Mise à jour de la base de données

Si vous avez modifié les modèles :

```powershell
cd backend
flask db migrate -m "Description des changements"
flask db upgrade
```

---

## 🎓 Technologies utilisées

**Backend** :
- Flask 3.1
- SQLAlchemy + PostgreSQL
- Flask-Migrate (Alembic)
- psycopg2

**Frontend** :
- React 18
- Vite
- Tailwind CSS
- Axios

---

**Version** : 1.0  
**Dernière mise à jour** : Décembre 2025

🚀 **Bon développement !**


