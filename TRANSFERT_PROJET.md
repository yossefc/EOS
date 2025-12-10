# 📤 Guide de transfert du projet EOS

Ce guide explique comment transférer le projet EOS d'un ordinateur à un autre.

## 🎯 Vue d'ensemble rapide

### Fichiers à transférer
```
EOS/
├── backend/              ✅ À transférer
│   ├── app.py
│   ├── models/
│   ├── routes/
│   ├── migrations/
│   ├── requirements.txt
│   └── ...
├── frontend/             ✅ À transférer
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── start_eos.bat         ✅ À transférer
├── GUIDE_INSTALLATION.md ✅ À transférer
└── *.md                  ✅ À transférer (documentation)
```

### Fichiers à EXCLURE (pour réduire la taille)
```
❌ backend/venv/                    # ~200 MB - À recréer
❌ backend/__pycache__/             # Cache Python
❌ backend/instance/                # Base de données SQLite locale
❌ frontend/node_modules/           # ~300 MB - À recréer
❌ frontend/dist/                   # Build de production
❌ .git/                            # ~100 MB (optionnel)
❌ **/*.pyc                         # Fichiers compilés
❌ **/__pycache__/                  # Cache Python
```

---

## 📦 Méthode 1 : Transfert par archive ZIP (Recommandé)

### Sur l'ordinateur source

1. **Créer une archive propre** :
   - Ouvrir PowerShell à la racine du projet
   ```powershell
   cd D:\EOS
   
   # Créer l'archive en excluant les gros dossiers
   Compress-Archive -Path `
       backend/*.py, `
       backend/models, `
       backend/routes, `
       backend/migrations, `
       backend/requirements.txt, `
       frontend/src, `
       frontend/public, `
       frontend/*.json, `
       frontend/*.js, `
       frontend/*.config.js, `
       *.md, `
       start_eos.bat `
       -DestinationPath EOS_Transfer.zip
   ```

2. **Taille approximative** : ~5-10 MB (sans node_modules ni venv)

3. **Transférer le fichier** :
   - Clé USB
   - Email (si < 25 MB)
   - Google Drive / OneDrive / Dropbox
   - WeTransfer (gratuit jusqu'à 2 GB)

### Sur l'ordinateur de destination

1. **Extraire l'archive** dans le dossier souhaité (ex: `D:\EOS`)

2. **Suivre le guide d'installation** : `GUIDE_INSTALLATION.md`

---

## 📦 Méthode 2 : Transfert par Git (Si configuré)

### Sur l'ordinateur source

```powershell
cd D:\EOS

# Vérifier l'état du repository
git status

# Ajouter les fichiers non trackés (si nécessaire)
git add .

# Commit les changements
git commit -m "Préparation pour transfert"

# Push vers GitHub/GitLab
git push origin master
```

### Sur l'ordinateur de destination

```powershell
# Cloner le repository
git clone https://github.com/votre-username/eos.git D:\EOS

cd D:\EOS

# Suivre le guide d'installation
```

**Avantages** :
- ✅ Versioning automatique
- ✅ Historique des changements
- ✅ Facilite les mises à jour futures

---

## 📦 Méthode 3 : Transfert réseau local

Si les deux ordinateurs sont sur le même réseau :

### Sur l'ordinateur source

1. **Partager le dossier EOS** :
   - Clic droit sur le dossier → Propriétés → Partage
   - Partager avec "Tout le monde" (lecture)

2. **Noter l'adresse réseau** :
   ```
   \\NOM-ORDINATEUR\EOS
   ```

### Sur l'ordinateur de destination

1. **Ouvrir l'Explorateur** et taper :
   ```
   \\NOM-ORDINATEUR\EOS
   ```

2. **Copier le dossier** vers `D:\EOS`

3. **Suivre le guide d'installation**

---

## 🗄️ Migration de la base de données

### Option A : Dump PostgreSQL complet

**Sur l'ordinateur source** :
```powershell
# Créer un dump de la base de données
pg_dump -U eos_user -d eos_db -F c -f eos_backup.dump

# Transférer le fichier eos_backup.dump (avec le projet)
```

**Sur l'ordinateur de destination** :
```powershell
# Créer la base de données vide
psql -U postgres
CREATE DATABASE eos_db OWNER eos_user;
\q

# Restaurer le dump
pg_restore -U eos_user -d eos_db eos_backup.dump
```

### Option B : Export SQL texte

**Sur l'ordinateur source** :
```powershell
pg_dump -U eos_user -d eos_db --inserts > eos_backup.sql
```

**Sur l'ordinateur de destination** :
```powershell
psql -U eos_user -d eos_db < eos_backup.sql
```

### Option C : Nouvelle base vide (Recommandé pour débuter)

Si vous préférez partir d'une base vide :

```powershell
cd D:\EOS\backend
python fix_missing_columns.py
```

Cela créera une base de données fraîche avec la structure correcte.

---

## ✅ Checklist de transfert

### Avant le transfert
- [ ] Sauvegarder la base de données PostgreSQL (si nécessaire)
- [ ] Exporter les données importantes (si nécessaire)
- [ ] Noter les configurations personnalisées
- [ ] Créer l'archive ZIP (sans venv et node_modules)

### Pendant le transfert
- [ ] Copier/transférer l'archive
- [ ] Vérifier l'intégrité (taille du fichier)

### Après le transfert
- [ ] Extraire l'archive sur le nouvel ordinateur
- [ ] Installer PostgreSQL
- [ ] Installer Python 3.11+
- [ ] Installer Node.js 18+
- [ ] Configurer PostgreSQL (utilisateur + base)
- [ ] Installer les dépendances backend (`pip install -r requirements.txt`)
- [ ] Installer les dépendances frontend (`npm install`)
- [ ] Appliquer les migrations (`python fix_missing_columns.py`)
- [ ] Restaurer les données (si dump transféré)
- [ ] Tester avec `start_eos.bat`

---

## 🔧 Configuration post-transfert

### Mettre à jour les chemins (si nécessaire)

Si vous installez dans un chemin différent de `D:\EOS`, vérifier :

1. **start_eos.bat** : Les chemins sont relatifs, pas de modification nécessaire

2. **Frontend - Configuration API** : 
   Vérifier `frontend/src/config.js` ou les appels API pour pointer vers `http://localhost:5000`

### Adapter les variables d'environnement

Si vous utilisez des mots de passe différents pour PostgreSQL :

**Fichier `backend/start_with_postgresql.py`** :
```python
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:NOUVEAU_MDP@localhost:5432/eos_db'
```

**Fichier `start_eos.bat`** :
```batch
set DATABASE_URL=postgresql+psycopg2://eos_user:NOUVEAU_MDP@localhost:5432/eos_db
```

---

## 🆘 Problèmes fréquents après transfert

### "Module not found"
```powershell
# Réinstaller les dépendances
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### "Port already in use"
Un autre service utilise le port 5000 ou 5173 :
```powershell
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus
taskkill /PID [PID] /F
```

### "Cannot connect to database"
Vérifier que :
- PostgreSQL est installé et démarré
- L'utilisateur `eos_user` existe
- La base `eos_db` existe
- Le mot de passe est correct dans les fichiers de config

### "column not found"
La base n'est pas à jour :
```powershell
cd backend
python fix_missing_columns.py
```

---

## 📊 Tailles approximatives

| Élément | Taille |
|---------|--------|
| Code source complet (avec docs) | ~5-10 MB |
| venv Python | ~200 MB |
| node_modules | ~300 MB |
| Base de données PostgreSQL (dump) | Variable (1-100 MB) |
| **Total avec dépendances** | ~500-600 MB |
| **Total sans dépendances** | ~5-10 MB |

💡 **Astuce** : Transférez sans les dépendances (venv, node_modules) pour gagner du temps et de l'espace. Elles seront recréées sur le nouvel ordinateur.

---

## 🎓 Ressources supplémentaires

- **Installation complète** : Voir `GUIDE_INSTALLATION.md`
- **Documentation multi-client** : Voir `MULTI_CLIENT_GUIDE.md`
- **Résumé de l'implémentation** : Voir `MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md`

---

**Bon transfert ! 🚀**

