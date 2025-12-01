# 🚀 Démarrage Rapide - EOS

## ✅ Problèmes Résolus

1. **Backend "Not Found"** ✅ - Page d'accueil ajoutée
2. **Frontend "react-query"** ✅ - Import supprimé

---

## 📋 Démarrage Backend

### 1. Ouvrir PowerShell dans le dossier backend
```powershell
cd D:\EOS\backend
```

### 2. Lancer le serveur
```powershell
python run_server.py
```

**OU** si run_server.py ne fonctionne pas :
```powershell
python app.py
```

### 3. Tester
Ouvrez votre navigateur : **http://localhost:5000/**

Vous devriez voir une belle page d'accueil ! 🎉

---

## 📋 Démarrage Frontend

### 1. Ouvrir un NOUVEAU PowerShell dans le dossier frontend
```powershell
cd D:\EOS\frontend
```

### 2. Installer les dépendances (première fois uniquement)
```powershell
npm install
```

### 3. Lancer le serveur de développement
```powershell
npm run dev
```

### 4. Ouvrir le frontend
Le terminal affichera l'URL, généralement : **http://localhost:5173**

---

## 🔧 Si ça ne marche pas

### Backend

**Erreur : "can't open file run_server.py"**
```powershell
# Utilisez app.py à la place
python app.py
```

**Erreur : "ModuleNotFoundError"**
```powershell
pip install -r requirements.txt
```

### Frontend

**Erreur : "react-query"**
✅ **RÉSOLU !** Le fichier main.jsx a été corrigé.

Si vous voyez encore l'erreur :
```powershell
# Arrêtez le serveur (Ctrl+C) et relancez
npm run dev
```

**Erreur : "command not found: npm"**
- Installez Node.js depuis https://nodejs.org/

---

## 📊 URLs Disponibles

### Backend (API)
- **Page d'accueil** : http://localhost:5000/
- **Infos API** : http://localhost:5000/api
- **Stats** : http://localhost:5000/api/stats
- **Données** : http://localhost:5000/api/donnees
- **Enquêteurs** : http://localhost:5000/api/enqueteurs

### Frontend (Interface)
- **Application** : http://localhost:5173

---

## ✅ Vérification

### Backend OK si vous voyez :
```
======================================================================
Serveur Flask EOS démarré avec succès!
URL: http://localhost:5000
======================================================================
 * Running on http://0.0.0.0:5000
```

### Frontend OK si vous voyez :
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🎯 Ordre de Démarrage

1. **D'ABORD** : Démarrer le backend (port 5000)
2. **ENSUITE** : Démarrer le frontend (port 5173)

---

## 💡 Astuce

Gardez **2 fenêtres PowerShell ouvertes** :
- Une pour le backend (D:\EOS\backend)
- Une pour le frontend (D:\EOS\frontend)

---

**Tout est prêt ! Lancez les deux serveurs et ouvrez http://localhost:5000/ 🚀**





