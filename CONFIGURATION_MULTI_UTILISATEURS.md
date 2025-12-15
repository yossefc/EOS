# 🌐 Configuration Multi-Utilisateurs EOS

Guide pour permettre à plusieurs personnes sur différents ordinateurs d'utiliser la même application EOS et la même base de données.

---

## 🎯 Cas d'usage

**Situation** :
- Ordinateur A : Utilisateur 1 entre des données d'enquêtes
- Ordinateur B : Vous ajoutez un nouveau client
- Ordinateur C : Un autre utilisateur valide des enquêtes

**Objectif** : Tous les ordinateurs partagent la même base de données PostgreSQL.

---

## 📋 Architecture recommandée

```
┌─────────────────────────────────────────────────────────────┐
│                    RÉSEAU LOCAL / INTERNET                   │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           │                    │                    │
    ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
    │ Ordinateur A│      │ Ordinateur B│      │ Ordinateur C│
    │  (Client)   │      │  (Client)   │      │  (Client)   │
    │             │      │             │      │             │
    │  Frontend   │      │  Frontend   │      │  Frontend   │
    │  (React)    │      │  (React)    │      │  (React)    │
    └─────────────┘      └─────────────┘      └─────────────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                         ┌──────▼──────┐
                         │ SERVEUR EOS │
                         │  (Central)  │
                         │             │
                         │  Backend    │
                         │  Flask API  │
                         │             │
                         │ PostgreSQL  │
                         │  Database   │
                         └─────────────┘
```

---

## 🏗️ Option 1 : Serveur Central (RECOMMANDÉ)

Un ordinateur devient le serveur, les autres se connectent à lui.

### Étape 1 : Choisir l'ordinateur serveur

**Critères** :
- ✅ Toujours allumé pendant les heures de travail
- ✅ Bonne connexion réseau
- ✅ Configuration minimale : 4 GB RAM, CPU correct

Cet ordinateur hébergera :
- PostgreSQL (base de données)
- Backend Flask (API)
- Optionnellement le frontend

---

### Étape 2 : Configuration du serveur

#### A. Configuration PostgreSQL pour accepter les connexions réseau

**1. Modifier `postgresql.conf`** :

Trouver le fichier (exemple Windows) :
```
C:\Program Files\PostgreSQL\16\data\postgresql.conf
```

Modifier :
```conf
# Écouter sur toutes les interfaces réseau
listen_addresses = '*'

# Port (par défaut)
port = 5432
```

**2. Modifier `pg_hba.conf`** :

Même dossier que `postgresql.conf`.

Ajouter à la fin :
```conf
# Autoriser les connexions depuis le réseau local
# Format : TYPE  DATABASE  USER      ADDRESS        METHOD

# Pour un réseau local 192.168.x.x
host    eos_db    eos_user  192.168.0.0/16    md5

# Pour un réseau local 10.x.x.x
host    eos_db    eos_user  10.0.0.0/8        md5

# Pour autoriser toutes les IPs (ATTENTION : moins sécurisé)
host    eos_db    eos_user  0.0.0.0/0         md5
```

**3. Redémarrer PostgreSQL** :

Windows :
```powershell
# Ouvrir "Services" (services.msc)
# Redémarrer le service "postgresql-x64-16"
```

Ou en ligne de commande (Admin) :
```powershell
net stop postgresql-x64-16
net start postgresql-x64-16
```

**4. Autoriser PostgreSQL dans le pare-feu** :

```powershell
# Exécuter en tant qu'Administrateur
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow
```

#### B. Configuration du Backend Flask

**1. Trouver l'adresse IP du serveur** :

```powershell
ipconfig
# Chercher "IPv4 Address" (exemple : 192.168.1.100)
```

**2. Modifier `backend/start_with_postgresql.py`** :

```python
if __name__ == '__main__':
    app = create_app()
    # Écouter sur toutes les interfaces (0.0.0.0)
    # Pour être accessible depuis le réseau
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False en production
```

**3. Autoriser Flask dans le pare-feu** :

```powershell
# Exécuter en tant qu'Administrateur
New-NetFirewallRule -DisplayName "Flask API (Port 5000)" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**4. Démarrer le serveur** :

```powershell
cd D:\EOS\backend
python start_with_postgresql.py
```

Le backend sera accessible sur : `http://IP_SERVEUR:5000`

---

### Étape 3 : Configuration des clients

Sur chaque ordinateur client (A, B, C, etc.) :

#### A. Installation

Suivre `GUIDE_INSTALLATION.md` MAIS :
- ❌ Ne PAS installer PostgreSQL
- ✅ Installer Python et Node.js
- ✅ Installer les dépendances (backend + frontend)

#### B. Configuration de la connexion

**1. Modifier `backend/start_with_postgresql.py`** :

Remplacer `localhost` par l'IP du serveur :

```python
# Au lieu de :
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

# Utiliser :
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@192.168.1.100:5432/eos_db'
#                                                                         ^^^^^^^^^^^^^^
#                                                                         IP du serveur
```

**2. Modifier `frontend/src/config.js` ou les appels API** :

Créer/modifier `frontend/src/config.js` :

```javascript
// Configuration de l'API
export const API_BASE_URL = 'http://192.168.1.100:5000';
//                                  ^^^^^^^^^^^^^^
//                                  IP du serveur

export default {
  apiUrl: API_BASE_URL
};
```

**3. Mettre à jour les appels API dans le frontend** :

Dans tous les fichiers qui font des appels API (exemple : `UpdateModal.jsx`, `AdminDashboard.jsx`, etc.) :

```javascript
// Importer la config
import { API_BASE_URL } from './config';

// Utiliser dans les appels
axios.get(`${API_BASE_URL}/api/stats`)
axios.post(`${API_BASE_URL}/api/donnees`, data)
```

**4. Script de démarrage client** :

Créer `start_eos_client.bat` :

```batch
@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║            EOS Client - Mode Multi-utilisateurs           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set SERVEUR_IP=192.168.1.100
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@%SERVEUR_IP%:5432/eos_db

echo [1/2] Démarrage du backend local (proxy)...
cd /d "%~dp0backend"
start "EOS Backend Client" cmd /k "set DATABASE_URL=%DATABASE_URL% && python start_with_postgresql.py"

timeout /t 5 /nobreak >nul

echo [2/2] Démarrage du frontend...
cd /d "%~dp0frontend"
start "EOS Frontend Client" cmd /k "npm run dev"

timeout /t 8 /nobreak >nul

echo.
echo ✅ Application démarrée en mode client
echo    Serveur backend : http://%SERVEUR_IP%:5000
echo    Frontend local  : http://localhost:5173
echo.

start "" "http://localhost:5173"

pause
```

---

## 🏗️ Option 2 : Frontend uniquement sur les clients

**Architecture simplifiée** : Le backend tourne UNIQUEMENT sur le serveur.

### Sur le serveur

Configuration identique à l'Option 1, Étape 2.

### Sur les clients

**Plus besoin de Python !** Seulement Node.js.

**1. Installer uniquement le frontend** :

```powershell
# Copier UNIQUEMENT le dossier frontend
D:\EOS\frontend\

cd D:\EOS\frontend
npm install
```

**2. Configurer l'API distante** :

Modifier `frontend/vite.config.js` :

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Rediriger les appels API vers le serveur distant
      '/api': {
        target: 'http://192.168.1.100:5000',  // IP du serveur
        changeOrigin: true,
      }
    }
  }
})
```

**3. Démarrer** :

```powershell
npm run dev
```

**Avantages** :
- ✅ Installation plus simple sur les clients
- ✅ Moins de ressources utilisées
- ✅ Une seule instance du backend (plus simple à gérer)

---

## 🏗️ Option 3 : Frontend statique (le plus simple)

**Architecture ultra-simplifiée** : 
- Backend sur le serveur
- Frontend compilé et servi par le backend

### Sur le serveur

**1. Compiler le frontend** :

```powershell
cd D:\EOS\frontend

# Configurer l'URL de l'API
# Dans les fichiers source, utiliser des chemins relatifs : '/api/...'

# Compiler
npm run build
# Génère le dossier 'dist/'
```

**2. Configurer Flask pour servir le frontend** :

Modifier `backend/app.py` :

```python
import os
from flask import Flask, send_from_directory

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../frontend/dist')
    
    # ... configuration existante ...
    
    # Route pour servir le frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app
```

**3. Démarrer le serveur** :

```powershell
cd D:\EOS\backend
python start_with_postgresql.py
```

### Sur les clients

**Rien à installer !** 

Les utilisateurs accèdent simplement à :
```
http://192.168.1.100:5000
```

Depuis leur navigateur (Chrome, Firefox, Edge, etc.).

**Avantages** :
- ✅ Aucune installation sur les clients
- ✅ Accessible depuis n'importe quel appareil (PC, tablette, mobile)
- ✅ Mises à jour centralisées (recompiler le frontend sur le serveur)

---

## 🔒 Sécurité et bonnes pratiques

### 1. Changer le mot de passe PostgreSQL

```sql
-- Se connecter à PostgreSQL
psql -U postgres

-- Changer le mot de passe
ALTER USER eos_user WITH PASSWORD 'VotreMotDePasseSecurise123!';
```

### 2. Utiliser HTTPS (production)

Pour une utilisation en dehors du réseau local :
- Configurer un certificat SSL/TLS
- Utiliser un reverse proxy (nginx, Apache)
- Ou utiliser un service cloud (Heroku, AWS, Azure, etc.)

### 3. Limiter les accès

Dans `pg_hba.conf`, être précis :

```conf
# Autoriser seulement les IPs spécifiques
host    eos_db    eos_user  192.168.1.10/32    md5  # Ordinateur A
host    eos_db    eos_user  192.168.1.11/32    md5  # Ordinateur B
host    eos_db    eos_user  192.168.1.12/32    md5  # Ordinateur C
```

### 4. Sauvegardes régulières

```powershell
# Script de sauvegarde automatique (sur le serveur)
pg_dump -U eos_user -d eos_db -F c -f "backup_eos_%date:~-4,4%%date:~-10,2%%date:~-7,2%.dump"
```

---

## 🧪 Test de la configuration

### 1. Tester PostgreSQL

Depuis un ordinateur client :

```powershell
psql -h 192.168.1.100 -U eos_user -d eos_db
# Mot de passe : eos_password

# Si ça se connecte : ✅ PostgreSQL est accessible
```

### 2. Tester le backend

Depuis un ordinateur client, ouvrir le navigateur :

```
http://192.168.1.100:5000/api/stats
```

Si vous voyez du JSON : ✅ Backend accessible

### 3. Tester le frontend

```
http://192.168.1.100:5173
```

Ou selon votre configuration.

---

## 📊 Comparaison des options

| Critère | Option 1 | Option 2 | Option 3 |
|---------|----------|----------|----------|
| **Complexité** | Moyenne | Moyenne | Simple |
| **Installation client** | Backend + Frontend | Frontend seul | Aucune |
| **Ressources client** | Python + Node | Node seul | Navigateur |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Flexibilité** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Maintenance** | Moyenne | Facile | Très facile |
| **Utilisation** | Réseau local | Réseau local | Réseau local/Internet |

**Recommandation** :
- **Petite équipe (2-5 personnes)** : Option 3 (le plus simple)
- **Équipe moyenne (5-15 personnes)** : Option 2 ou 3
- **Grande équipe ou besoins spécifiques** : Option 1

---

## 🆘 Problèmes fréquents

### ❌ "Could not connect to server"

**Cause** : Le serveur PostgreSQL n'accepte pas les connexions réseau.

**Solution** :
1. Vérifier `postgresql.conf` : `listen_addresses = '*'`
2. Vérifier `pg_hba.conf` : Ligne ajoutée pour le réseau
3. Redémarrer PostgreSQL
4. Vérifier le pare-feu

### ❌ "Connection refused on port 5000"

**Cause** : Le backend Flask n'est pas accessible depuis le réseau.

**Solution** :
1. Vérifier que Flask écoute sur `0.0.0.0` (pas `127.0.0.1`)
2. Vérifier le pare-feu Windows
3. Tester avec : `telnet IP_SERVEUR 5000`

### ❌ "CORS error"

**Cause** : Le frontend ne peut pas appeler le backend distant.

**Solution** :

Dans `backend/app.py`, vérifier la configuration CORS :

```python
from flask_cors import CORS

CORS(app, resources={
    r"/*": {
        "origins": "*",  # En développement
        # En production, lister les IPs autorisées
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

### ❌ Les données ne se synchronisent pas

**Vérification** :
1. Tous les clients utilisent la même DATABASE_URL
2. L'IP du serveur est correcte
3. Rafraîchir le navigateur (F5) pour voir les nouvelles données

---

## 🎯 Résumé : Configuration recommandée

### Pour démarrer rapidement (Option 3 - Recommandée)

**Sur l'ordinateur serveur** :

1. Installer PostgreSQL, Python, Node.js
2. Configurer PostgreSQL pour le réseau (étapes ci-dessus)
3. Compiler le frontend : `npm run build`
4. Démarrer le serveur : `python start_with_postgresql.py`

**Sur les autres ordinateurs** :

1. Ouvrir le navigateur
2. Aller sur : `http://IP_SERVEUR:5000`
3. ✅ Terminé !

**Avantages** :
- ✅ Simple à configurer
- ✅ Aucune installation sur les clients
- ✅ Mises à jour centralisées
- ✅ Fonctionne sur tous les appareils (PC, tablette, mobile)

---

**Version** : 1.0  
**Dernière mise à jour** : Décembre 2025


