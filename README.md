# EOS - Système de Gestion d'Enquêtes

Application web de gestion d'enquêtes avec Flask (backend) et React (frontend) utilisant PostgreSQL.

## 📖 Documentation

➡️ **Tout est dans le guide** : **[LISEZ-MOI.md](LISEZ-MOI.md)**

---

## ⚡ Démarrage rapide

### Première installation

```cmd
# 1. Ajouter PostgreSQL au PATH (PowerShell)
.\00_ajouter_postgresql_au_path.ps1

# 2. Configurer la base de données
01_configurer_postgresql.bat

# 3. Installer le backend
02_installer_backend.bat

# 4. Installer le frontend
03_installer_frontend.bat
```

### Démarrer l'application

**Terminal 1** - Backend :
```cmd
DEMARRER_EOS_POSTGRESQL.bat
```

**Terminal 2** - Frontend :
```cmd
cd frontend
npm run dev
```

**Accès** : http://localhost:5173

---

## 🔧 En cas de problème

| Commande | Utilité |
|----------|---------|
| `CORRIGER_BDD.bat` | Réparer la base de données |
| `REINITIALISER_MAPPINGS.bat` | Corriger l'import de fichiers |

---

📘 **Guide complet** : [LISEZ-MOI.md](LISEZ-MOI.md)
