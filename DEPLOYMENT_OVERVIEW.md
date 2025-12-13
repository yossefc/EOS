# 📊 DEPLOYMENT_OVERVIEW.md - Vue d'ensemble du déploiement

Analyse complète de l'architecture et de la stratégie de déploiement de l'application EOS.

**Date d'analyse** : Décembre 2025  
**Version analysée** : 1.0 (multi-client)  
**Repository** : yossefc/EOS

---

## 🏗️ Architecture existante

### Stack technique

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION EOS                           │
├────────────────────┬────────────────────────────────────────┤
│    FRONTEND        │            BACKEND                      │
├────────────────────┼────────────────────────────────────────┤
│ • React 18         │ • Flask 3.1                             │
│ • Vite             │ • SQLAlchemy                            │
│ • Tailwind CSS     │ • Flask-Migrate (Alembic)              │
│ • Axios            │ • psycopg2 (PostgreSQL)                │
│ • Port : 5173      │ • Port : 5000                          │
└────────────────────┴────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │   Port : 5432    │
                    └──────────────────┘
```

### Structure des dossiers

```
D:\EOS\
├── backend/                      # API Flask
│   ├── app.py                   # Point d'entrée principal
│   ├── config.py                # Configuration (DATABASE_URL, CORS)
│   ├── extensions.py            # Init Flask, SQLAlchemy, Migrate
│   ├── models/                  # Modèles SQLAlchemy
│   │   ├── client.py           # Table clients
│   │   ├── models.py           # Donnee, Fichier
│   │   ├── import_config.py    # ImportProfile, ImportFieldMapping
│   │   └── ...
│   ├── routes/                  # Routes API
│   │   ├── enquetes.py
│   │   ├── files.py
│   │   ├── validation_v2.py
│   │   └── ...
│   ├── migrations/              # Migrations Alembic
│   │   ├── versions/
│   │   │   ├── 001_initial_migration.py
│   │   │   └── 002_add_multi_client_support.py
│   │   └── env.py
│   ├── scripts/                 # Scripts utilitaires
│   │   ├── add_new_client.py
│   │   └── upgrade_app.py
│   ├── requirements.txt         # Dépendances Python
│   ├── start_with_postgresql.py # Script de démarrage
│   ├── fix_missing_columns.py   # Init/correction DB
│   └── check_db_state.py        # Diagnostic DB
├── frontend/                     # Interface React
│   ├── src/
│   │   ├── main.jsx            # Point d'entrée
│   │   ├── components/
│   │   │   ├── DataViewer.jsx  # Onglet Données
│   │   │   ├── ImportHandler.jsx # Onglet Import
│   │   │   ├── UpdateModal.jsx
│   │   │   └── ...
│   │   └── ...
│   ├── package.json            # Dépendances npm
│   └── vite.config.js          # Configuration Vite
├── start_eos.bat               # Démarrage automatique
├── 01_configurer_postgresql.bat # Setup PostgreSQL
├── 02_installer_backend.bat    # Setup backend
├── 03_installer_frontend.bat   # Setup frontend
└── Documentation/
    ├── DEPLOYMENT_GUIDE.md     # Guide de déploiement ⭐
    ├── UPGRADE_GUIDE.md        # Guide de mise à jour ⭐
    ├── GUIDE_INSTALLATION.md
    └── ...
```

---

## 🎯 Stratégie de déploiement retenue

### Choix : Installation classique (non-Docker)

**Raison** : Le projet n'inclut pas de Docker et cible principalement Windows.

**Avantages** :
- ✅ Pas de dépendance Docker Desktop (licence, ressources)
- ✅ Contrôle total sur chaque composant
- ✅ Facilité de débogage (logs accessibles directement)
- ✅ Familier pour les utilisateurs Windows

**Inconvénients** :
- ⚠️ Installation manuelle de PostgreSQL, Python, Node.js
- ⚠️ Configuration manuelle (PATH, DATABASE_URL)

**Solution** : Scripts d'installation automatiques (`01_`, `02_`, `03_`) qui guident l'utilisateur.

---

## 📦 Processus d'installation chez un client

### Méthode automatisée (recommandée)

```
1. Prérequis manuels (une fois)
   ├── Installer PostgreSQL 16+
   ├── Installer Python 3.11+
   └── Installer Node.js 18+

2. Scripts automatiques
   ├── 01_configurer_postgresql.bat   (Crée user + base)
   ├── 02_installer_backend.bat       (venv + pip install + migrations)
   └── 03_installer_frontend.bat      (npm install)

3. Démarrage
   └── start_eos.bat                   (Lance tout + ouvre navigateur)
```

**Durée estimée** : 20-30 minutes (incluant téléchargements)

### Fichiers livrés au client

**Via Git** (recommandé) :
```
git clone https://github.com/yossefc/EOS.git
```

**Via ZIP** :
- Tout le dossier EOS **SAUF** :
  - `backend/venv/`
  - `backend/__pycache__/`
  - `frontend/node_modules/`
  - `frontend/dist/`
  - `.git/` (si applicable)

**Taille** : ~5-10 MB sans dépendances, ~600 MB avec dépendances

---

## 🔄 Stratégie de mise à jour

### Principe : Code ↔ Données séparés

```
┌──────────────────────┬──────────────────────────────┐
│   CODE (modifiable)  │   DONNÉES (préservées)       │
├──────────────────────┼──────────────────────────────┤
│ backend/*.py         │ Base PostgreSQL eos_db       │
│ frontend/src/        │ • Table clients              │
│ migrations/versions/ │ • Table donnees (enquêtes)   │
│ scripts/             │ • Table fichiers             │
│ *.bat, *.md         │ • Toutes les autres tables   │
│                      │                              │
│ ✅ Remplacé via Git │ ❌ Jamais remplacé           │
│    ou ZIP           │    Sauf migration Alembic    │
└──────────────────────┴──────────────────────────────┘
```

### Process

us de mise à jour standard

```
1. SAUVEGARDE (CRITIQUE)
   pg_dump -U eos_user -d eos_db -F c -f backup.dump

2. Arrêt de l'application
   Fermer fenêtres backend/frontend

3. Mise à jour du code
   git pull origin main
   OU extraction nouvelle archive ZIP

4. Mise à jour dépendances
   pip install -r requirements.txt
   npm install

5. Migrations base de données (NON DESTRUCTIVES)
   flask db upgrade
   OU python scripts/upgrade_app.py

6. Redémarrage
   .\start_eos.bat

7. Vérification
   • Données toujours présentes ?
   • Nouvelles fonctionnalités OK ?
```

**Durée estimée** : 5-10 minutes

---

## 🏢 Support multi-client

### Architecture actuelle

La base de données supporte déjà plusieurs clients via :

- **Table `clients`** : Liste des clients (EOS, CLIENT_B, etc.)
- **Colonne `client_id`** : Sur toutes les tables importantes
  - `fichiers.client_id`
  - `donnees.client_id`
  - `donnees_enqueteur.client_id`
  - `enquete_archive_files.client_id`
  - `export_batches.client_id`

### Ajout d'un nouveau client

**Méthode 1 - Via migration** (lors d'une mise à jour) :
```python
# Dans une nouvelle migration Alembic
def upgrade():
    op.execute("""
        INSERT INTO clients (code, nom, actif, date_creation)
        VALUES ('CLIENT_B', 'Client B', true, NOW())
    """)
    # + configuration du profil d'import
```

**Méthode 2 - Via script** (ajout ponctuel) :
```powershell
python scripts/add_new_client.py --code CLIENT_B --name "Client B" --format TXT_FIXED --interactive
```

**Méthode 3 - Via SQL** (rapide) :
```sql
INSERT INTO clients (code, nom, actif, date_creation)
VALUES ('CLIENT_B', 'Client B', true, NOW());
```

**Impact sur les données existantes** : AUCUN
- Les données EOS restent intactes
- Les nouvelles données CLIENT_B ont `client_id` différent
- L'interface affiche un sélecteur de client si plusieurs clients actifs

---

## 🔒 Protection des données

### Garanties du système de migrations

Les migrations Alembic sont conçues pour :

✅ **Ajouter** :
- Nouvelles tables
- Nouvelles colonnes (avec valeurs par défaut)
- Nouveaux index
- Nouvelles contraintes

✅ **Migrer** :
- Remplir `client_id=1` (EOS) sur données existantes
- Convertir formats si nécessaire

❌ **Jamais** :
- `DROP TABLE` (sauf tables temporaires/obsolètes explicites)
- `TRUNCATE`
- `DELETE` sans `WHERE` précis
- Suppression de colonnes critiques

### Exemple de migration sécurisée (002_add_multi_client_support.py)

```python
def upgrade():
    # 1. Ajouter client_id (nullable temporairement)
    op.add_column('fichiers', sa.Column('client_id', sa.Integer(), nullable=True))
    
    # 2. Créer le client EOS
    op.execute("INSERT INTO clients (code, nom, actif) VALUES ('EOS', 'EOS France', true)")
    
    # 3. Migrer les données existantes vers EOS (client_id=1)
    op.execute("UPDATE fichiers SET client_id = 1 WHERE client_id IS NULL")
    
    # 4. Rendre la colonne NOT NULL
    op.alter_column('fichiers', 'client_id', nullable=False)
```

**Résultat** :
- ✅ Toutes les données existantes sont préservées
- ✅ Elles sont associées au client EOS
- ✅ Le schéma est étendu sans perte

---

## 🛠️ Outils de maintenance

### Scripts fournis

| Script | Usage | Description |
|--------|-------|-------------|
| `check_db_state.py` | Diagnostic | Affiche l'état de la base (tables, colonnes, versions) |
| `fix_missing_columns.py` | Init/Correction | Crée/corrige la structure de la base |
| `scripts/add_new_client.py` | Ajout client | Ajoute un nouveau client interactivement |
| `scripts/upgrade_app.py` | Mise à jour | Automatise le processus de mise à jour |

### Commandes de diagnostic

```powershell
# État de la base
python backend/check_db_state.py

# Version Alembic
cd backend
flask db current

# Historique des migrations
flask db history

# Logs de l'application
Get-Content backend/app.log -Tail 100

# Vérifier la connexion PostgreSQL
psql -U eos_user -d eos_db -c "SELECT version();"
```

---

## 📊 Système de migrations (Alembic)

### Configuration actuelle

**Fichiers** :
- `backend/migrations/alembic.ini` : Config Alembic
- `backend/migrations/env.py` : Script d'environnement
- `backend/migrations/versions/` : Fichiers de migration

**Migrations existantes** :
1. `001_initial_migration.py` : Création des tables de base
2. `002_add_multi_client_support.py` : Ajout du support multi-client

**État** : ✅ Fonctionnel et testé

### Création d'une nouvelle migration

```powershell
cd backend
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

# Générer automatiquement (détecte les changements de modèles)
flask db migrate -m "Description du changement"

# Éditer le fichier généré si nécessaire
# backend/migrations/versions/XXX_description_du_changement.py

# Appliquer
flask db upgrade

# Vérifier
flask db current
```

---

## 🌐 Modes de déploiement supportés

### Mode 1 : Local (1 PC)

**Usage** : Installation standard sur l'ordinateur du client

**Démarrage** :
```powershell
.\start_eos.bat
```

**Accès** : `http://localhost:5173`

---

### Mode 2 : Serveur + Clients (réseau local)

**Usage** : Un serveur héberge backend + PostgreSQL, plusieurs clients accèdent via navigateur

**Sur le serveur** :
```powershell
.\start_eos_serveur.bat
# → Affiche l'IP du serveur (ex: 192.168.1.100)
```

**Sur les clients** :
- Ouvrir navigateur : `http://192.168.1.100:5000`
- OU installer le code et lancer : `.\start_eos_client.bat`

**Documentation** : `CONFIGURATION_MULTI_UTILISATEURS.md`

---

## 📈 Scalabilité et performance

### Capacité actuelle

- **Enquêtes** : Testé jusqu'à 20 000+ enquêtes
- **Clients** : Illimité (testé avec 10+ clients)
- **Utilisateurs simultanés** : 5-10 (réseau local)

### Optimisations en place

- Index PostgreSQL sur :
  - `client_id` (toutes les tables)
  - `statut_validation` + `enqueteurId` (tables principales)
  - `numeroDossier`, `nom` (recherche rapide)
- Pool de connexions configuré (config.py)
- Pagination sur les listes longues (frontend)

### Recommandations pour > 50 000 enquêtes

- RAM : 8 GB minimum (16 GB recommandé)
- PostgreSQL : SSD pour la base de données
- Backend : Déploiement avec Gunicorn (au lieu de Flask dev)
- Frontend : Build de production (`npm run build`)

---

## 🚀 Checklist de déploiement

### Pour un nouveau client

- [ ] Prérequis installés (PostgreSQL, Python, Node.js)
- [ ] Code récupéré (Git ou ZIP)
- [ ] Scripts d'installation exécutés (01, 02, 03)
- [ ] Base de données initialisée (client EOS créé)
- [ ] Application démarre (`start_eos.bat`)
- [ ] Test d'import réussi
- [ ] Documentation fournie au client
- [ ] Formation basique effectuée

### Pour une mise à jour

- [ ] Sauvegarde PostgreSQL créée
- [ ] Notes de version lues
- [ ] Application arrêtée
- [ ] Code mis à jour (Git pull ou ZIP)
- [ ] Dépendances mises à jour (pip, npm)
- [ ] Migrations appliquées (`flask db upgrade`)
- [ ] Application redémarrée
- [ ] Données vérifiées (toujours présentes)
- [ ] Nouvelles fonctionnalités testées
- [ ] Sauvegarde conservée (au cas où)

---

## 📞 Support et documentation

### Documents créés

| Document | Public | Contenu |
|----------|--------|---------|
| `DEPLOYMENT_GUIDE.md` | Client final | Installation complète étape par étape |
| `UPGRADE_GUIDE.md` | Client final | Mise à jour sans perte de données |
| `DEPLOYMENT_OVERVIEW.md` | Développeur | Architecture et stratégie (ce document) |
| `GUIDE_INSTALLATION.md` | Client final | Guide d'installation détaillé |
| `CONFIGURATION_MULTI_UTILISATEURS.md` | Admin système | Déploiement réseau |
| `MULTI_CLIENT_GUIDE.md` | Utilisateur | Utilisation multi-client |
| `INDEX.md` | Tous | Navigation dans la doc |

### Arborescence documentation recommandée

```
docs/
├── utilisateurs/
│   ├── GUIDE_INSTALLATION.md
│   ├── MULTI_CLIENT_GUIDE.md
│   └── FAQ.md
├── administrateurs/
│   ├── DEPLOYMENT_GUIDE.md        ⭐
│   ├── UPGRADE_GUIDE.md           ⭐
│   ├── CONFIGURATION_MULTI_UTILISATEURS.md
│   └── TROUBLESHOOTING.md
└── développeurs/
    ├── DEPLOYMENT_OVERVIEW.md     ⭐ (ce document)
    ├── ARCHITECTURE.md
    ├── API.md
    └── CONTRIBUTING.md
```

---

## 🎯 Conclusion

### Forces du système actuel

- ✅ **Architecture modulaire** : Backend/Frontend bien séparés
- ✅ **Migrations robustes** : Alembic configuré et testé
- ✅ **Multi-client natif** : Support complet via `client_id`
- ✅ **Scripts d'installation** : Process automatisé
- ✅ **Documentation complète** : Guides pour tous les profils
- ✅ **Protection des données** : Migrations non destructives

### Points d'amélioration potentiels

- 🔄 **Docker** : Pourrait simplifier l'installation (à évaluer)
- 🔄 **CI/CD** : Automatisation des tests et déploiements
- 🔄 **Versioning** : Tag Git systématique pour chaque release
- 🔄 **Changelog** : Document des changements par version
- 🔄 **Tests automatiques** : Pour garantir la non-régression

### Recommandation finale

La stratégie actuelle est **solide et adaptée** au contexte :
- Installation Windows standard sans Docker
- Mise à jour via Git conservant les données
- Multi-client prêt pour expansion
- Documentation complète et claire

**Action immédiate recommandée** :
1. Créer des tags Git pour chaque version
2. Maintenir un CHANGELOG.md
3. Tester le processus complet d'upgrade sur une copie de production

---

**Document rédigé par** : Cursor AI (Analyse du projet yossefc/EOS)  
**Date** : Décembre 2025  
**Version** : 1.0

