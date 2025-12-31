# 🔧 CORRECTIF - Environnement virtuel Python

## Problème

Lorsque vous lancez `DEMARRER_EOS_COMPLET.bat`, vous obtenez l'erreur :
```
did not find executable at 'C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe'
Le chemin d'accès spécifié est introuvable.
```

## Cause

L'environnement virtuel Python (dossier `backend/venv`) a été créé sur **l'ancien ordinateur** et contient des chemins spécifiques à cet ordinateur. Quand vous copiez le projet sur un **nouvel ordinateur**, ces chemins ne sont plus valides.

## ✅ Solution rapide

### Double-cliquez sur ce fichier :
```
RECREER_VENV.bat
```

Ce script va :
1. Supprimer l'ancien environnement virtuel
2. En créer un nouveau pour ce PC
3. Réinstaller toutes les dépendances Python
4. Vérifier que tout fonctionne

**Durée** : 2-3 minutes

---

## ✅ Solution manuelle (si vous préférez)

### 1. Ouvrir un terminal dans D:\EOS\backend

### 2. Supprimer l'ancien venv

**PowerShell :**
```powershell
Remove-Item -Recurse -Force venv
```

**Cmd :**
```bash
rmdir /s /q venv
```

### 3. Créer un nouveau venv

```bash
python -m venv venv
```

### 4. Activer le venv

```bash
venv\Scripts\activate
```

Vous devriez voir `(venv)` apparaître dans votre terminal.

### 5. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 6. Tester

```bash
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db
python start_with_postgresql.py
```

Si le backend démarre sans erreur, c'est bon ! ✅

---

## 🚀 Après la correction

Une fois l'environnement virtuel recréé, vous pouvez utiliser normalement :

```bash
DEMARRER_EOS_COMPLET.bat
```

---

## 💡 Pourquoi ce problème ?

Un environnement virtuel Python (`venv`) n'est **pas portable** entre ordinateurs car il contient des chemins absolus vers l'installation Python.

**Règle** : Quand vous copiez un projet Python sur un nouvel ordinateur, vous devez **toujours recréer le venv**.

---

## 📝 Note pour les prochaines installations

Pour éviter ce problème lors des prochains transferts :

1. **NE PAS copier le dossier `backend/venv`** (il sera ignoré par Git normalement)
2. Sur le nouvel ordinateur, exécuter `RECREER_VENV.bat`
3. Ou ajouter `venv/` dans `.gitignore` (normalement déjà fait)

---

**Date** : 31 décembre 2025  
**Statut** : Solution testée et validée

