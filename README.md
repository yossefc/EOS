# 🏢 EOS - Système de Gestion d'Enquêtes

Application web de gestion d'enquêtes multi-clients avec support EOS et PARTNER.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Structure du projet](#-structure-du-projet)
- [Documentation](#-documentation)

---

## ✨ Fonctionnalités

### 🔹 **Multi-clients**
- Support de plusieurs clients (EOS, PARTNER, etc.)
- Configuration spécifique par client
- Isolation des données

### 🔹 **Gestion d'enquêtes**
- Import de fichiers Excel
- Assignation automatique aux enquêteurs
- Suivi des statuts (en attente, validée, archivée)
- Historique complet des modifications

### 🔹 **Exports personnalisés**
- **EOS** : Export texte CP1252
- **PARTNER** : Export Word (.docx) + Excel (.xls)
- Détection automatique des demandes
- Archivage des exports

### 🔹 **PARTNER - Fonctionnalités avancées**
- Détection automatique des demandes (ADRESSE, TÉLÉPHONE, EMPLOYEUR, BANQUE, NAISSANCE)
- Calcul automatique POS/NEG par demande
- Tarification combinée selon les demandes
- Interface d'administration des mots-clés et tarifs

### 🔹 **Interface utilisateur**
- Interface administrateur moderne et responsive
- Interface enquêteur simplifiée
- Tableaux de bord avec statistiques
- Filtres et recherche avancée

---

## 🛠️ Technologies

### Backend
- **Python 3.11+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de données
- **Alembic** - Migrations de base de données
- **python-docx** - Génération de documents Word
- **xlwt** - Génération de fichiers Excel

### Frontend
- **React 18** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - Requêtes HTTP
- **Lucide React** - Icônes

---

## 📦 Installation

### ⚠️ **Correction importante (31/12/2025)**

Un conflit de migrations Alembic a été corrigé. Si vous installez sur un **nouvel ordinateur**, utilisez :

**Méthode rapide :**
```bash
# Double-cliquez sur le fichier
INSTALLER_BASE_DONNEES.bat
```

**Ou consultez :**
- 📄 **[INSTALLATION_RAPIDE.md](INSTALLATION_RAPIDE.md)** - Guide d'installation 1 page
- 📄 **[__CORRECTION_MIGRATIONS_LISEZMOI__.txt](__CORRECTION_MIGRATIONS_LISEZMOI__.txt)** - Résumé de la correction

---

### Prérequis
- Python 3.11 ou supérieur
- Node.js 18 ou supérieur
- PostgreSQL 14 ou supérieur

### 1️⃣ Configuration PostgreSQL

Exécutez les scripts d'installation dans l'ordre :

```bash
# 1. Ajouter PostgreSQL au PATH
.\00_ajouter_postgresql_au_path.ps1

# 2. Configurer PostgreSQL
.\01_configurer_postgresql.bat
```

### 2️⃣ Installation Backend

```bash
# Installer les dépendances Python
.\02_installer_backend.bat
```

### 3️⃣ Installation Frontend

```bash
# Installer les dépendances Node.js
.\03_installer_frontend.bat
```

---

## 🚀 Démarrage rapide

### Démarrage complet (Backend + Frontend)

```bash
# Démarre le backend et le frontend en une seule commande
.\DEMARRER_EOS_COMPLET.bat
```

### Démarrage séparé

**Backend uniquement :**
```bash
.\REDEMARRER_BACKEND.bat
```

**Frontend uniquement :**
```bash
.\REDEMARRER_FRONTEND.bat
```

### Accès à l'application

- **Interface administrateur** : http://localhost:5173
- **Interface enquêteur** : http://localhost:5173/enqueteur.html
- **API Backend** : http://localhost:5000

---

## 📁 Structure du projet

```
EOS/
├── backend/                    # Backend Flask
│   ├── models/                 # Modèles SQLAlchemy
│   ├── routes/                 # Routes API
│   ├── services/               # Logique métier
│   ├── migrations/             # Migrations Alembic
│   └── scripts/                # Scripts utilitaires
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/         # Composants React
│   │   ├── styles/             # Fichiers CSS
│   │   └── config.js           # Configuration
│   └── dist/                   # Build de production
│
├── documentation_partner/      # Documentation PARTNER
├── archives_documentation/     # Documentation archivée
│
└── *.bat                       # Scripts de démarrage
```

---

## 📚 Documentation

### Documentation principale
- **[LISEZ-MOI.md](LISEZ-MOI.md)** - Guide d'utilisation détaillé

### Installation et migrations
- **[INSTALLATION_RAPIDE.md](INSTALLATION_RAPIDE.md)** - Guide d'installation rapide (1 page)
- **[GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md](GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md)** - Guide complet avec dépannage
- **[__CORRECTION_MIGRATIONS_LISEZMOI__.txt](__CORRECTION_MIGRATIONS_LISEZMOI__.txt)** - Résumé de la correction du 31/12/2025

### Documentation PARTNER
- **[00_INDEX_DOCUMENTATION_PARTNER.md](documentation_partner/00_INDEX_DOCUMENTATION_PARTNER.md)** - Index de la documentation PARTNER
- **[GUIDE_INSTALLATION_PARTNER_COMPLET.md](documentation_partner/GUIDE_INSTALLATION_PARTNER_COMPLET.md)** - Installation complète PARTNER
- **[FINAL_INSTRUCTIONS_23_12.md](documentation_partner/FINAL_INSTRUCTIONS_23_12.md)** - Instructions finales

### Corrections et améliorations
Consultez le dossier `documentation_partner/` pour les corrections spécifiques :
- Corrections de naissance
- Corrections d'exports
- Corrections de tarification
- Améliorations UI

---

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost:5432/eos_db
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete
```

### Configuration frontend

Modifiez `frontend/src/config.js` si nécessaire :

```javascript
const config = {
    API_URL: `http://${window.location.hostname}:5000`,
    FRONTEND_URL: `http://${window.location.hostname}:5173`
};
```

---

## 🐛 Dépannage

### Le backend ne démarre pas
1. Vérifiez que PostgreSQL est démarré
2. Vérifiez la variable `DATABASE_URL` dans `.env`
3. Exécutez `.\REDEMARRER_BACKEND.bat`

### Le frontend ne démarre pas
1. Vérifiez que Node.js est installé (`node --version`)
2. Supprimez `node_modules/` et réinstallez : `cd frontend && npm install`
3. Exécutez `.\REDEMARRER_FRONTEND.bat`

### Erreurs de base de données
1. Vérifiez que PostgreSQL est accessible
2. Vérifiez les migrations : `cd backend && alembic current`
3. Appliquez les migrations : `alembic upgrade head`

---

## 👥 Contributeurs

Développé pour la gestion d'enquêtes EOS et PARTNER.

---

## 📄 Licence

Propriétaire - Tous droits réservés

---

## 📞 Support

Pour toute question ou problème :
1. Consultez la documentation dans `documentation_partner/`
2. Vérifiez les fichiers de correction spécifiques
3. Consultez l'historique des modifications

---

**Version** : 2.0 (Décembre 2025)  
**Dernière mise à jour** : 31/12/2025 (Correction migrations Alembic)
