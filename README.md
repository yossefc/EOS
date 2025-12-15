# 🚀 EOS - Application de Gestion des Enquêtes

Application multi-client de gestion des enquêtes avec support PostgreSQL.

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](CHANGELOG.md)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-green.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)

---

## ⚡ Démarrage rapide

```powershell
# Démarrer l'application (si déjà installée)
.\start_eos.bat
```

➜ L'application s'ouvre automatiquement sur http://localhost:5173

---

## 📦 Installation

### Pour un nouveau client (acheteur du logiciel)

**Guide complet** : [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Installation rapide** :
```powershell
# 1. Installer PostgreSQL 16+, Python 3.11+, Node.js 18+
# 2. Récupérer le code
git clone https://github.com/yossefc/EOS.git
cd EOS

# 3. Exécuter les scripts d'installation
.\01_configurer_postgresql.bat
.\02_installer_backend.bat
.\03_installer_frontend.bat

# 4. Démarrer
.\start_eos.bat
```

---

## 🔄 Mise à jour

**Guide complet** : [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md)

```powershell
# Mise à jour automatique (avec sauvegarde)
git pull origin main
cd backend
python scripts/upgrade_app.py
```

✅ **Garantie** : Aucune perte de données

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [INDEX.md](INDEX.md) | 📖 Index de toute la documentation |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | 📦 Installation chez un client |
| [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) | 🔄 Mise à jour sans perte de données |
| [MULTI_CLIENT_GUIDE.md](MULTI_CLIENT_GUIDE.md) | 🏢 Utilisation multi-client |
| [CONFIGURATION_MULTI_UTILISATEURS.md](CONFIGURATION_MULTI_UTILISATEURS.md) | 🌐 Mode réseau |
| [CHANGELOG.md](CHANGELOG.md) | 📝 Historique des versions |

**Point d'entrée** : Ouvrir [INDEX.md](INDEX.md) pour naviguer dans toute la documentation.

---

## 🌟 Fonctionnalités

- ✅ **Multi-client** : Gérer plusieurs clients avec profils d'import personnalisés
- ✅ **Import flexible** : TXT fixe, CSV, Excel avec mapping configurable
- ✅ **Gestion enquêteurs** : Assignation et suivi des enquêtes
- ✅ **Validation** : Workflow de validation multi-niveaux
- ✅ **Exports** : Word, CSV, Excel personnalisables
- ✅ **Base PostgreSQL** : Scalable jusqu'à 50 000+ enquêtes
- ✅ **Interface moderne** : React + Vite + Tailwind CSS
- ✅ **Mode réseau** : Un serveur, plusieurs clients

---

## 🏗️ Architecture

**Backend** :
- Flask 3.1 + SQLAlchemy
- PostgreSQL (psycopg2)
- Flask-Migrate (Alembic)
- API RESTful

**Frontend** :
- React 18
- Vite (build tool)
- Tailwind CSS
- Axios (HTTP client)

---

## 🚀 Scripts disponibles

### Démarrage
```powershell
.\start_eos.bat                # Mode local (1 PC)
.\start_eos_serveur.bat        # Mode serveur (plusieurs PCs)
.\start_eos_client.bat         # Mode client (se connecte au serveur)
```

### Installation
```powershell
.\01_configurer_postgresql.bat  # Configure PostgreSQL
.\02_installer_backend.bat      # Installe backend
.\03_installer_frontend.bat     # Installe frontend
```

### Maintenance
```powershell
python backend/scripts/upgrade_app.py     # Mise à jour automatique
python backend/scripts/add_new_client.py  # Ajouter un client
python backend/check_db_state.py          # Diagnostic DB
```

---

## 📊 Structure du projet

```
EOS/
├── backend/                # API Flask + PostgreSQL
│   ├── app.py             # Point d'entrée
│   ├── models/            # Modèles SQLAlchemy
│   ├── routes/            # Routes API
│   ├── migrations/        # Migrations Alembic
│   └── scripts/           # Scripts utilitaires
├── frontend/              # Interface React
│   ├── src/
│   │   └── components/    # Composants React
│   └── package.json
├── start_eos.bat          # Démarrage automatique ⭐
└── Documentation/         # Guides complets
    ├── INDEX.md           # Navigation
    ├── DEPLOYMENT_GUIDE.md
    └── UPGRADE_GUIDE.md
```

---

## 🔧 Configuration

### Variables d'environnement

```powershell
# Base de données (obligatoire)
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# Ports (optionnels)
$env:BACKEND_PORT="5000"
$env:FRONTEND_PORT="5173"
```

### Fichiers de configuration

- `backend/config.py` : Configuration Flask (DB, CORS, logging)
- `frontend/vite.config.js` : Configuration Vite (port, proxy)

---

## 🆘 Support

### Problèmes fréquents

| Problème | Solution |
|----------|----------|
| Port déjà utilisé | `netstat -ano \| findstr :5000` puis `taskkill /PID [PID] /F` |
| Module not found | `pip install -r requirements.txt` |
| column not found | `python backend/fix_missing_columns.py` |

**Troubleshooting complet** : Voir [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📈 Versions

- **1.1.0** (actuelle) : Documentation de déploiement complète
- **1.0.0** : Support multi-client + PostgreSQL obligatoire
- **0.9.x** : Version initiale EOS seul + SQLite

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet.

---

## 📞 Contact

- **Repository** : yossefc/EOS
- **Documentation** : Voir [INDEX.md](INDEX.md)
- **Issues** : GitHub Issues

---

## 📄 Licence

Copyright © 2025 - Application EOS

---

**Dernière mise à jour** : Décembre 2025  
**Mainteneur** : yossefc


