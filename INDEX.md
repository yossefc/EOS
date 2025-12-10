# 📚 EOS - Index de la Documentation

Bienvenue dans l'application EOS ! Ce fichier vous guide vers la documentation appropriée selon votre besoin.

---

## 🎯 Je veux...

### ✨ Démarrer l'application rapidement
→ **Double-cliquez sur** : `start_eos.bat`  
→ **Ou lisez** : [`README_DEMARRAGE_RAPIDE.md`](README_DEMARRAGE_RAPIDE.md)

### 📦 Installer l'application pour la première fois
→ **Suivez** : [`GUIDE_INSTALLATION.md`](GUIDE_INSTALLATION.md)

### 📤 Transférer le projet vers un autre ordinateur
→ **Méthode automatique** : Exécutez `creer_archive_transfert.ps1`  
→ **Guide complet** : [`TRANSFERT_PROJET.md`](TRANSFERT_PROJET.md)

### 🏢 Comprendre le système multi-client
→ **Guide utilisateur** : [`MULTI_CLIENT_GUIDE.md`](MULTI_CLIENT_GUIDE.md)  
→ **Documentation technique** : [`MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md`](MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md)

---

## 📋 Scripts disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `start_eos.bat` | ⭐ Démarre backend + frontend + navigateur | Double-clic |
| `creer_archive_transfert.ps1` | Crée une archive ZIP pour transfert | Clic-droit → Exécuter avec PowerShell |
| `backend/start_with_postgresql.py` | Démarre uniquement le backend | `python backend/start_with_postgresql.py` |
| `backend/fix_missing_columns.py` | Corrige/initialise la base de données | `python backend/fix_missing_columns.py` |
| `backend/check_db_state.py` | Vérifie l'état de la base de données | `python backend/check_db_state.py` |

---

## 📖 Documentation complète

### 🚀 Démarrage
- [`README_DEMARRAGE_RAPIDE.md`](README_DEMARRAGE_RAPIDE.md) - Guide rapide de démarrage
- [`GUIDE_INSTALLATION.md`](GUIDE_INSTALLATION.md) - Installation complète étape par étape

### 📤 Transfert et déploiement
- [`TRANSFERT_PROJET.md`](TRANSFERT_PROJET.md) - Comment transférer le projet

### 🏢 Système multi-client
- [`MULTI_CLIENT_GUIDE.md`](MULTI_CLIENT_GUIDE.md) - Guide d'utilisation multi-client
- [`MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md`](MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md) - Documentation technique

### 🛠️ Configuration
- `.gitignore` - Fichiers à exclure du versioning Git

---

## 🔍 Résolution de problèmes rapide

### ❌ L'application ne démarre pas
1. Vérifier que PostgreSQL est installé et démarré
2. Vérifier que Python et Node.js sont installés
3. Consulter [`GUIDE_INSTALLATION.md`](GUIDE_INSTALLATION.md)

### ❌ Erreur "column not found"
```powershell
cd backend
python fix_missing_columns.py
```

### ❌ Erreur "Port already in use"
```powershell
# Trouver le processus
netstat -ano | findstr :5000
# Tuer le processus
taskkill /PID [PID] /F
```

### ❌ Module Python manquant
```powershell
cd backend
pip install -r requirements.txt
```

### ❌ Dépendances npm manquantes
```powershell
cd frontend
npm install
```

---

## 🏗️ Architecture du projet

```
EOS/
│
├── 📄 start_eos.bat                    ⭐ SCRIPT DE DÉMARRAGE PRINCIPAL
├── 📄 creer_archive_transfert.ps1     Script de création d'archive
│
├── 📚 Documentation/
│   ├── README_DEMARRAGE_RAPIDE.md     Guide rapide
│   ├── GUIDE_INSTALLATION.md          Installation complète
│   ├── TRANSFERT_PROJET.md            Guide de transfert
│   ├── MULTI_CLIENT_GUIDE.md          Guide multi-client
│   ├── MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md
│   └── INDEX.md                       Ce fichier
│
├── 🔧 backend/                         Backend Flask + PostgreSQL
│   ├── app.py                         Application principale
│   ├── models/                        Modèles de données
│   ├── routes/                        Routes API
│   ├── migrations/                    Migrations Alembic
│   ├── start_with_postgresql.py       Script de démarrage backend
│   ├── fix_missing_columns.py         Script de correction DB
│   ├── check_db_state.py              Script de diagnostic DB
│   └── requirements.txt               Dépendances Python
│
└── 🎨 frontend/                        Frontend React + Vite
    ├── src/
    │   ├── components/                Composants React
    │   └── ...
    ├── package.json                   Dépendances npm
    └── vite.config.js                 Configuration Vite
```

---

## 🌟 Fonctionnalités principales

| Fonctionnalité | Description |
|----------------|-------------|
| 🏢 **Multi-client** | Gérer plusieurs clients avec profils d'import personnalisés |
| 📊 **Import flexible** | Support TXT fixe, CSV, Excel avec mapping configurable |
| 👥 **Gestion enquêteurs** | Assignation et suivi des enquêtes |
| ✅ **Validation** | Workflow de validation à plusieurs niveaux |
| 📤 **Exports** | Word, CSV, Excel personnalisables |
| 🗄️ **PostgreSQL** | Base robuste scalable jusqu'à 50 000+ enquêtes |
| 🎨 **Interface moderne** | React + Tailwind CSS responsive |

---

## 🎓 Technologies

**Backend** :
- Python 3.11+ | Flask 3.1 | SQLAlchemy | PostgreSQL | Alembic

**Frontend** :
- React 18 | Vite | Tailwind CSS | Axios

---

## 📞 Aide supplémentaire

### Vérifier l'état du système
```powershell
# État de la base de données
python backend/check_db_state.py

# Version Python
python --version

# Version Node.js
node --version

# Version PostgreSQL
psql --version
```

### Logs de l'application
- **Backend** : Affichés dans la fenêtre "EOS Backend"
- **Frontend** : Affichés dans la fenêtre "EOS Frontend"

### Redémarrer proprement
1. Fermer les fenêtres Backend et Frontend (Ctrl+C puis fermer)
2. Relancer `start_eos.bat`

---

## 🚀 Démarrage rapide (récapitulatif)

```powershell
# 1️⃣ Première fois : Installer PostgreSQL, Python, Node.js
# 2️⃣ Configurer PostgreSQL (voir GUIDE_INSTALLATION.md)
# 3️⃣ Installer les dépendances :
cd backend
pip install -r requirements.txt
python fix_missing_columns.py

cd ../frontend
npm install

# 4️⃣ Démarrer l'application :
cd ..
.\start_eos.bat

# 🎉 C'est tout !
```

---

**Version** : 1.0  
**Dernière mise à jour** : Décembre 2025  
**Projet** : EOS - Application de Gestion des Enquêtes

---

💡 **Conseil** : Ajoutez ce fichier à vos favoris pour un accès rapide à la documentation !

