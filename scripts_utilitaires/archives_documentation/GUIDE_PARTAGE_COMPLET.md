# Guide de Partage Complet - Système EOS

## Vue d'ensemble
Ce guide explique comment partager le système EOS complet avec toutes ses fonctionnalités, y compris la base de données et toutes les configurations.

## Architecture du Projet

### Structure des dossiers
```
EOS/
├── backend/                    # Serveur Flask Python
│   ├── app.py                 # Application principale
│   ├── models/                # Modèles de données
│   ├── routes/                # Routes API
│   ├── instance/              # Base de données SQLite
│   │   └── eos.db            # Base de données principale
│   ├── requirements.txt       # Dépendances Python
│   └── config.py             # Configuration
├── frontend/                  # Interface utilisateur React
│   ├── src/                  # Code source React
│   ├── package.json          # Dépendances Node.js
│   └── vite.config.js        # Configuration Vite
└── documentation/            # Documentation
```

## Composants du Système

### 1. Backend (Flask)
- **Gestion des enquêtes** - CRUD complet
- **Système d'authentification** - Enquêteurs et admin
- **Gestion des fichiers** - Import/Export
- **Base de données SQLite** - Stockage des données
- **API REST** - Communication avec frontend
- **Génération de documents** - Export Word/PDF
- **Système de tarification** - Calculs automatiques

### 2. Frontend (React)
- **Interface d'administration** - Gestion complète
- **Interface enquêteurs** - Saisie de données
- **Visualisation des données** - Tableaux et graphiques
- **Import/Export** - Gestion des fichiers
- **Responsive design** - Compatible tous écrans

### 3. Base de Données
- **SQLite intégrée** - `backend/instance/eos.db`
- **Tables principales** :
  - `enquetes` - Données d'enquêtes
  - `enqueteurs` - Informations enquêteurs
  - `tarifs` - Grilles tarifaires
  - `archives` - Enquêtes terminées

## Prérequis pour l'Installation

### Système d'exploitation
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+)

### Logiciels requis
1. **Python 3.8+** - https://python.org/downloads/
2. **Node.js 16+** - https://nodejs.org/
3. **Git** - https://git-scm.com/

## Installation Complète

### Étape 1 : Préparation
1. Télécharger tout le dossier EOS
2. S'assurer que tous les fichiers sont présents
3. Vérifier que la base de données `eos.db` est incluse

### Étape 2 : Configuration Backend
```bash
# Naviguer vers le backend
cd EOS/backend

# Créer environnement virtuel Python
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate
# Ou sur macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 3 : Configuration Frontend
```bash
# Naviguer vers le frontend
cd EOS/frontend

# Installer les dépendances Node.js
npm install
```

### Étape 4 : Configuration de la Base de Données
La base de données SQLite est déjà incluse dans `backend/instance/eos.db`

Si besoin de réinitialiser :
```bash
cd EOS/backend
python init_db.py
```

## Démarrage du Système

### Démarrage Automatique
Utiliser les scripts fournis :

**Windows :**
```bash
# Depuis le dossier EOS
start_server.bat
```

**macOS/Linux :**
```bash
# Depuis le dossier EOS
./start_server.sh
```

### Démarrage Manuel

**Backend (Terminal 1) :**
```bash
cd EOS/backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python app.py
```

**Frontend (Terminal 2) :**
```bash
cd EOS/frontend
npm run dev
```

## Accès au Système

### URLs d'accès
- **Interface Admin** : http://localhost:5173
- **Interface Enquêteurs** : http://localhost:5173/enqueteur.html
- **API Backend** : http://localhost:5000

### Comptes par défaut
- **Admin** : admin / admin123
- **Enquêteur test** : enq001 / pass123

## Fonctionnalités Principales

### Administration
- Gestion des enquêteurs
- Validation des enquêtes
- Export des données (Excel, Word, PDF)
- Statistiques et rapports
- Gestion des tarifs

### Enquêteurs
- Saisie des enquêtes
- Upload de fichiers
- Consultation de l'historique
- Calcul automatique des gains

## Sauvegarde et Partage

### Éléments à partager obligatoirement
1. **Tout le dossier EOS/** - Structure complète
2. **Base de données** - `backend/instance/eos.db`
3. **Fichiers de configuration** - `backend/config.py`
4. **Dépendances** - `requirements.txt` et `package.json`

### Archive complète
Pour partager, créer une archive contenant :
```
EOS-COMPLET.zip
├── EOS/                      # Dossier principal complet
├── GUIDE_PARTAGE_COMPLET.md  # Ce guide
└── SCRIPT_INSTALLATION.bat   # Script d'installation automatique
```

### Exclusions (optionnelles)
Peuvent être exclus pour réduire la taille :
- `node_modules/` (sera recréé par npm install)
- `venv/` (sera recréé par pip install)
- `__pycache__/` (cache Python)
- `.git/` (historique Git)

## Dépannage

### Problèmes courants

**Port déjà utilisé :**
- Backend : Modifier le port dans `app.py` (ligne avec `app.run()`)
- Frontend : Modifier dans `vite.config.js`

**Base de données corrompue :**
```bash
cd backend
python reset_db.py
```

**Dépendances manquantes :**
```bash
# Backend
pip install -r requirements.txt --force-reinstall

# Frontend
npm install --force
```

## Support et Maintenance

### Logs et diagnostics
- **Backend** : `backend/app.log`
- **Frontend** : Console du navigateur (F12)

### Mise à jour
1. Sauvegarder la base de données
2. Remplacer les fichiers du code
3. Conserver `backend/instance/eos.db`
4. Réinstaller les dépendances si nécessaire

## Sécurité

### Points d'attention
- Changer les mots de passe par défaut
- Configurer HTTPS en production
- Sauvegarder régulièrement la base de données
- Limiter l'accès réseau si nécessaire

### Recommandations
- Utiliser un serveur dédié pour la production
- Mettre en place des sauvegardes automatiques
- Surveiller les logs d'erreurs
- Tester régulièrement les fonctionnalités

---

**Note :** Ce système est complètement autonome et peut fonctionner hors ligne une fois installé.