# 🖥️ Guide d'Installation EOS sur un Nouveau PC

Ce guide vous permet d'installer et exécuter le projet EOS sur un autre ordinateur.

---

## 📋 Prérequis

### Logiciels à installer sur le nouveau PC

1. **Python 3.10+** : https://www.python.org/downloads/
   - ⚠️ Cocher "Add Python to PATH" lors de l'installation

2. **Node.js 18+** : https://nodejs.org/
   - Télécharger la version LTS

3. **Git** (optionnel, pour cloner) : https://git-scm.com/

---

## 📦 Méthode 1 : Transfert par ZIP (Recommandé)

### Étape 1 : Préparer les fichiers sur le PC actuel

```powershell
# Sur le PC actuel, créer une archive sans les fichiers inutiles
cd D:\EOS

# Créer un dossier temporaire pour l'export
mkdir D:\EOS_EXPORT

# Copier les fichiers essentiels (sans node_modules et venv)
robocopy D:\EOS D:\EOS_EXPORT /E /XD node_modules venv __pycache__ .git instance exports /XF *.db *.log *.pyc
```

### Étape 2 : Fichiers à transférer

Copiez ces dossiers/fichiers sur une clé USB ou via le réseau :

```
EOS/
├── backend/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
└── (ce fichier README)
```

### ⚠️ Fichiers à NE PAS transférer (ils seront recréés)
- `backend/instance/` (base de données)
- `backend/exports/` (fichiers exportés)
- `backend/venv/` (environnement Python)
- `frontend/node_modules/` (dépendances Node)
- `*.log`, `*.pyc`, `__pycache__/`

---

## 🔧 Installation sur le nouveau PC

### Étape 1 : Copier les fichiers

Copiez le dossier EOS à l'emplacement souhaité (ex: `D:\EOS` ou `C:\Projets\EOS`)

### Étape 2 : Installer le Backend (Python/Flask)

```powershell
# Ouvrir PowerShell et aller dans le dossier backend
cd D:\EOS\backend

# Créer un environnement virtuel Python
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\Activate

# Installer les dépendances
pip install -r requirements.txt

# Si requirements.txt n'existe pas, installer manuellement :
pip install flask flask-cors flask-sqlalchemy python-docx openpyxl
```

### Étape 3 : Installer le Frontend (React/Vite)

```powershell
# Ouvrir un nouveau PowerShell et aller dans le dossier frontend
cd D:\EOS\frontend

# Installer les dépendances Node.js
npm install
```

### Étape 4 : Configurer l'adresse IP

**Important** : Si vous accédez à l'application depuis un autre PC sur le réseau, vous devez configurer l'adresse IP.

#### Backend (`backend/app.py`)
Le backend écoute déjà sur `0.0.0.0` (toutes les interfaces).

#### Frontend (`frontend/src/config.js`)
Modifiez l'adresse IP du backend :

```javascript
// Remplacez par l'adresse IP du PC où tourne le backend
const config = {
  API_URL: 'http://192.168.X.X:5000'  // ← Mettre l'IP du serveur
};
```

Pour trouver l'adresse IP du PC :
```powershell
ipconfig
# Cherchez "IPv4 Address" dans la section Ethernet ou Wi-Fi
```

---

## 🚀 Démarrage de l'application

### Terminal 1 : Démarrer le Backend

```powershell
cd D:\EOS\backend
.\venv\Scripts\Activate
python app.py
```

Vous devriez voir :
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.X.X:5000
```

### Terminal 2 : Démarrer le Frontend

```powershell
cd D:\EOS\frontend
npm run dev
```

Vous devriez voir :
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.X.X:5173/
```

### Accéder à l'application

- **Sur le même PC** : http://localhost:5173
- **Depuis un autre PC** : http://192.168.X.X:5173 (IP du PC serveur)

---

## 📂 Méthode 2 : Transfert avec la base de données

Si vous voulez conserver les données existantes :

### Fichiers supplémentaires à transférer

```
backend/
├── instance/
│   └── eos.db          ← Base de données SQLite
└── exports/
    └── batches/        ← Fichiers d'export générés
```

### Copier la base de données

```powershell
# Sur le PC actuel
copy D:\EOS\backend\instance\eos.db D:\EOS_EXPORT\backend\instance\

# Copier aussi les exports si nécessaire
robocopy D:\EOS\backend\exports D:\EOS_EXPORT\backend\exports /E
```

---

## 🔧 Configuration avancée

### Variables d'environnement (optionnel)

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Code prestataire pour les exports EOS (3 lettres)
CODE_PRESTATAIRE=XXX

# Port du serveur (par défaut 5000)
FLASK_PORT=5000

# Mode debug (True/False)
FLASK_DEBUG=True
```

### Configuration CORS

Si vous avez des problèmes d'accès depuis d'autres PC, modifiez `backend/config.py` :

```python
# Ajouter les adresses IP autorisées
CORS_ORIGINS = 'http://localhost:5173,http://192.168.1.100:5173,http://192.168.1.101:5173'
```

---

## ❓ Résolution des problèmes

### Erreur "python n'est pas reconnu"
→ Réinstallez Python en cochant "Add Python to PATH"

### Erreur "npm n'est pas reconnu"
→ Réinstallez Node.js et redémarrez PowerShell

### Erreur "Module not found"
```powershell
# Backend
cd backend
.\venv\Scripts\Activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Erreur "CORS" ou "Network Error"
→ Vérifiez que l'adresse IP dans `frontend/src/config.js` est correcte

### Base de données vide
→ Normal si vous n'avez pas transféré `backend/instance/eos.db`
→ Importez un fichier Excel depuis l'interface

### Port 5000 déjà utilisé
```powershell
# Trouver le processus qui utilise le port
netstat -ano | findstr :5000

# Tuer le processus (remplacer XXXX par le PID)
taskkill /PID XXXX /F
```

---

## 📋 Checklist d'installation

- [ ] Python 3.10+ installé
- [ ] Node.js 18+ installé
- [ ] Dossier EOS copié
- [ ] `pip install -r requirements.txt` exécuté
- [ ] `npm install` exécuté
- [ ] Adresse IP configurée dans `frontend/src/config.js`
- [ ] Backend démarré (`python app.py`)
- [ ] Frontend démarré (`npm run dev`)
- [ ] Application accessible dans le navigateur

---

## 🎉 C'est prêt !

Une fois les deux serveurs démarrés, ouvrez votre navigateur et accédez à :
- http://localhost:5173 (sur le même PC)
- http://[IP_DU_PC]:5173 (depuis un autre PC)

---

## 📞 Support

En cas de problème :
1. Vérifiez les messages d'erreur dans les terminaux
2. Vérifiez que les deux serveurs sont bien démarrés
3. Vérifiez la configuration IP
4. Redémarrez les serveurs si nécessaire

