# 📝 Changelog - Application EOS

Toutes les modifications notables du projet EOS sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.1.0] - 2025-12-13 (en développement)

### Ajouté
- 📘 **DEPLOYMENT_GUIDE.md** : Guide complet de déploiement pour les clients
- 🔄 **UPGRADE_GUIDE.md** : Guide de mise à jour sans perte de données
- 📊 **DEPLOYMENT_OVERVIEW.md** : Vue d'ensemble technique de l'architecture
- 🎯 **MULTI_CLIENT_DEPLOYMENT_IMPLEMENTATION.md** : Rapport d'implémentation complet
- 🔧 **backend/scripts/upgrade_app.py** : Script automatique de mise à jour
- ✅ **CHANGELOG.md** : Ce fichier, pour tracer les versions

### Amélioré
- 📚 **INDEX.md** : Ajout des liens vers les nouveaux guides de déploiement
- 🔧 Scripts d'installation (01, 02, 03) : Validation et documentation

### Documentation
- Guide complet pour installer l'application chez un client
- Guide complet pour mettre à jour sans toucher aux données
- Procédure d'ajout d'un nouveau client documentée (3 méthodes)
- Procédure de restauration en cas de problème
- Troubleshooting complet (10+ problèmes fréquents)

---

## [1.0.0] - 2025-12-10

### Ajouté
- ✨ Support multi-client complet
  - Table `clients` avec gestion de plusieurs clients
  - Colonne `client_id` sur toutes les tables critiques
  - Profils d'import configurables par client (`import_profiles`, `import_field_mappings`)
  - Interface avec sélecteur de client automatique

- 🗄️ Migration PostgreSQL obligatoire
  - Support SQLite supprimé
  - Configuration optimisée pour PostgreSQL (pool de connexions)
  - Migrations Alembic complètes :
    - `001_initial_migration.py` : Structure de base
    - `002_add_multi_client_support.py` : Ajout multi-client non destructif

- 🚀 Scripts de démarrage automatique
  - `start_eos.bat` : Mode local (un seul PC)
  - `start_eos_serveur.bat` : Mode serveur (plusieurs utilisateurs)
  - `start_eos_client.bat` : Mode client (connexion au serveur)

- 📦 Scripts d'installation
  - `01_configurer_postgresql.bat` : Configure PostgreSQL
  - `02_installer_backend.bat` : Installe le backend
  - `03_installer_frontend.bat` : Installe le frontend

- 🔧 Scripts utilitaires
  - `backend/scripts/add_new_client.py` : Ajoute un nouveau client
  - `backend/check_db_state.py` : Diagnostic de la base
  - `backend/fix_missing_columns.py` : Correction/initialisation de la base

- 📚 Documentation complète
  - `GUIDE_INSTALLATION.md` : Installation détaillée
  - `CONFIGURATION_MULTI_UTILISATEURS.md` : Mode réseau
  - `MULTI_CLIENT_GUIDE.md` : Utilisation multi-client
  - `MULTI_CLIENT_IMPLEMENTATION_SUMMARY.md` : Documentation technique
  - `TRANSFERT_PROJET.md` : Guide de transfert
  - `README_DEMARRAGE_RAPIDE.md` : Référence rapide
  - `INDEX.md` : Index de navigation

### Modifié
- 🔧 **backend/config.py** : Configuration PostgreSQL obligatoire
- 🔧 **backend/app.py** : Initialisation avec migrations
- 🔧 **backend/models/** : Tous les modèles mis à jour avec `client_id`
- 🎨 **frontend/src/components/** : Support du sélecteur de client

### Supprimé
- ❌ Support SQLite (migration obligatoire vers PostgreSQL)

---

## [0.9.0] - 2025-12-XX (version pré-multi-client)

### Ajouté
- Gestion des enquêtes pour EOS
- Import de fichiers TXT à positions fixes
- Gestion des enquêteurs
- Validation des enquêtes
- Exports Word, CSV, Excel
- Archivage des enquêtes
- Système de tarification
- Génération de configurations VPN

### Technique
- Backend Flask + SQLAlchemy
- Frontend React + Vite
- Base de données SQLite
- Authentification basique

---

## Format des versions

Le projet suit le [Semantic Versioning](https://semver.org/lang/fr/) :

- **MAJOR version** (X.0.0) : Changements incompatibles de l'API
- **MINOR version** (0.X.0) : Nouvelles fonctionnalités rétrocompatibles
- **PATCH version** (0.0.X) : Corrections de bugs rétrocompatibles

### Types de changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans des fonctionnalités existantes
- **Déprécié** : Fonctionnalités bientôt supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités

---

## Roadmap (versions futures)

### [1.2.0] - À venir
- [ ] Tests automatiques (pytest)
- [ ] CI/CD avec GitHub Actions
- [ ] Docker support (optionnel)
- [ ] API REST documentation (OpenAPI/Swagger)
- [ ] Logs structurés améliorés

### [1.3.0] - À venir
- [ ] Gestion des utilisateurs avec rôles
- [ ] Authentification JWT
- [ ] Dashboard analytics amélioré
- [ ] Export PDF avancé

### [2.0.0] - Futur
- [ ] Refonte complète du frontend (TypeScript)
- [ ] API GraphQL (optionnel)
- [ ] Mode SaaS multi-tenant
- [ ] Mobile app (optionnel)

---

## Notes de mise à jour

### Mise à jour vers 1.1.0 (depuis 1.0.0)

```powershell
# 1. Sauvegarde
pg_dump -U eos_user -d eos_db -F c -f backup.dump

# 2. Mise à jour du code
git pull origin main

# 3. Mise à jour automatique
cd backend
python scripts/upgrade_app.py

# 4. Redémarrage
cd ..
.\start_eos.bat
```

**Changements** : Documentation enrichie, script d'upgrade automatique

**Impact** : Aucun sur les données, aucune migration DB requise

### Mise à jour vers 1.0.0 (depuis 0.9.x)

⚠️ **MIGRATION MAJEURE** : SQLite → PostgreSQL obligatoire

Voir `MIGRATION_POSTGRESQL_RAPPORT.md` pour la procédure complète.

---

## Support et contact

- **Documentation** : Voir `INDEX.md` pour tous les guides
- **Installation** : Voir `DEPLOYMENT_GUIDE.md`
- **Mise à jour** : Voir `UPGRADE_GUIDE.md`
- **Issues** : GitHub Issues (si applicable)

---

**Dernière mise à jour** : 2025-12-13  
**Mainteneur** : yossefc  
**Repository** : yossefc/EOS

