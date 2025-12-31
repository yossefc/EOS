# 🔧 GUIDE : Résolution problèmes Frontend

## ❌ Symptôme : Le script REBUILD_FRONTEND.bat se ferme automatiquement

### Causes possibles :

1. **Node.js n'est pas installé**
2. **Le dossier frontend n'existe pas à l'emplacement attendu**
3. **Erreur npm qui ferme la fenêtre**
4. **Problème de permissions**

---

## 🔍 ÉTAPE 1 : Diagnostic

Avant de rebuilder, vérifiez votre environnement :

```bash
./CHECK_FRONTEND_ENV.bat
```

Ce script vérifie :
- ✅ Présence du dossier `frontend/`
- ✅ Node.js installé
- ✅ npm installé
- ✅ `package.json` présent
- ✅ Fichiers source présents
- ✅ Script build disponible

---

## 🚀 ÉTAPE 2 : Rebuild robuste

Si le diagnostic est OK, utilisez le script robuste :

```bash
./REBUILD_FRONTEND_ROBUSTE.bat
```

**Avantages :**
- Ne se ferme JAMAIS automatiquement
- Affiche toutes les erreurs en détail
- Vérifie chaque étape
- Propose des solutions si erreur

---

## 🛠️ SOLUTIONS AUX PROBLÈMES COURANTS

### Problème 1 : "npm n'est pas reconnu..."

**Cause** : Node.js n'est pas installé ou pas dans le PATH

**Solution** :
1. Téléchargez Node.js : https://nodejs.org/ (version LTS)
2. Installez-le (cocher "Add to PATH")
3. Redémarrez le terminal
4. Testez : `node --version` et `npm --version`

### Problème 2 : "Le dossier frontend n'existe pas"

**Cause** : Vous êtes dans le mauvais répertoire

**Solution** :
```bash
# Vérifiez où vous êtes
cd

# Allez dans le bon répertoire (à adapter)
cd /d/eos
# ou
cd D:\EOS

# Vérifiez que frontend existe
dir
```

### Problème 3 : "Erreur lors de npm install"

**Causes** :
- Connexion internet coupée
- Proxy/firewall bloque npm
- Cache npm corrompu
- Permissions insuffisantes

**Solutions** :

**A. Nettoyer le cache npm**
```bash
cd frontend
npm cache clean --force
npm install
```

**B. Supprimer node_modules et réinstaller**
```bash
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
```

**C. Exécuter en tant qu'administrateur**
- Clic droit sur le script → "Exécuter en tant qu'administrateur"

**D. Désactiver temporairement l'antivirus**
- Parfois l'antivirus bloque npm

### Problème 4 : "Build échoue avec erreur de syntaxe"

**Cause** : Erreur dans le code React

**Solution** :
1. Regardez l'erreur affichée (fichier + ligne)
2. Vérifiez le fichier concerné
3. Si c'est un fichier que vous n'avez pas modifié :
   ```bash
   git status
   git diff
   # Si besoin, annuler les modifications
   git checkout -- frontend/src/le_fichier_problematique.jsx
   ```

### Problème 5 : "dist/ n'est pas créé"

**Cause** : Build échoue silencieusement

**Solution** :
```bash
cd frontend
# Essayez manuellement
npm run build

# Si erreur "vite: command not found"
npm install vite --save-dev

# Puis réessayez
npm run build
```

### Problème 6 : "Impossible de supprimer dist/"

**Cause** : Fichiers verrouillés par un processus

**Solution** :
1. Fermez TOUS les terminaux/éditeurs
2. Arrêtez le serveur de dev (Ctrl+C si en cours)
3. Réessayez

Ou manuellement :
```bash
cd frontend
# Forcer la suppression
rmdir /s /q dist
```

---

## 🎯 MÉTHODE MANUELLE (si les scripts échouent)

Si TOUS les scripts échouent, faites-le manuellement :

```bash
# 1. Aller dans frontend
cd D:\EOS\frontend

# 2. Vérifier Node.js
node --version
npm --version

# 3. Installer les dépendances
npm install

# 4. Nettoyer l'ancien build
rmdir /s /q dist

# 5. Builder
npm run build

# 6. Vérifier que dist existe
dir dist
```

---

## 🌐 VIDER LE CACHE DU NAVIGATEUR

Après le rebuild, il est CRITIQUE de vider le cache :

### Chrome / Edge :
1. `F12` pour ouvrir DevTools
2. Onglet "Réseau" / "Network"
3. Clic droit sur "Disable cache" → cocher
4. `Ctrl + Shift + R` pour hard refresh

### Firefox :
1. `Ctrl + Shift + Delete`
2. Cocher "Cache"
3. Période : "Dernière heure"
4. Effacer

### Méthode radicale (si rien ne marche) :
1. Paramètres du navigateur
2. Confidentialité et sécurité
3. Effacer les données de navigation
4. Cocher :
   - Cache
   - Cookies et données de sites (ATTENTION : déconnexion de tous les sites)
5. Période : "Tout"
6. Effacer

---

## 📝 CHECKLIST POST-BUILD

Après avoir rebuild avec succès :

- [ ] Le dossier `frontend/dist/` existe
- [ ] Il contient des fichiers (minimum index.html, assets/)
- [ ] Redémarrer l'application : `DEMARRER_EOS_SIMPLE.bat`
- [ ] Fermer TOUTES les fenêtres du navigateur
- [ ] Ouvrir http://localhost:5173
- [ ] `Ctrl + Shift + R` pour hard refresh
- [ ] Vérifier que les champs RECHERCHE et INSTRUCTIONS apparaissent

---

## 🆘 SI RIEN NE MARCHE

1. **Testez sur CET ordinateur (qui marche)** :
   ```bash
   ./REBUILD_FRONTEND_ROBUSTE.bat
   ```
   Si ça marche ici mais pas sur l'autre, c'est un problème d'environnement.

2. **Comparez les versions Node.js** :
   ```bash
   # Sur chaque ordinateur
   node --version
   npm --version
   ```

3. **Copiez le dossier `frontend/dist/` de CET ordinateur vers l'autre** (solution temporaire)

4. **Vérifiez les différences Git** :
   ```bash
   git status
   git diff frontend/
   ```

---

## 📁 Fichiers créés

- `REBUILD_FRONTEND_ROBUSTE.bat` : Script robuste qui ne se ferme jamais
- `CHECK_FRONTEND_ENV.bat` : Diagnostic pre-build
- `GUIDE_PROBLEMES_FRONTEND.md` : Ce guide

---

**Date** : 31 décembre 2025

