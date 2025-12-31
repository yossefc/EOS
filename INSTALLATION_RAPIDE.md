# 🔧 Installation rapide sur un nouvel ordinateur

## ⚡ Méthode automatique (Windows)

Double-cliquez sur :
```
INSTALLER_BASE_DONNEES.bat
```

Le script va :
1. ✓ Vérifier PostgreSQL et Python
2. ✓ Demander vos identifiants PostgreSQL
3. ✓ Créer la base de données
4. ✓ Appliquer toutes les migrations
5. ✓ Configurer l'environnement

---

## 📝 Méthode manuelle

### 1. Démarrer PostgreSQL

```bash
# Windows (en administrateur)
net start postgresql-x64-16
```

### 2. Créer la base de données

```bash
psql -U postgres
CREATE DATABASE eos_db;
\q
```

### 3. Configurer DATABASE_URL

**Git Bash :**
```bash
export DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"
```

**PowerShell :**
```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"
```

### 4. Appliquer les migrations

```bash
cd D:\eos
python backend/apply_migrations.py
```

### 5. Démarrer l'application

```bash
# Double-cliquez sur :
DEMARRER_EOS_COMPLET.bat

# Ou manuellement :
python backend/app.py
```

---

## 🔍 Vérification (optionnel)

```bash
# Vérifier que les migrations sont cohérentes
python verifier_migrations.py

# Vérifier les tables créées
psql -U postgres -d eos_db -c "\dt"
```

---

## 📚 Documentation complète

- **Guide détaillé** : `GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md`
- **Résumé de la correction** : `CORRECTION_MIGRATIONS_RESUME.md`
- **Historique** : `archives_documentation/CORRECTIF_MIGRATIONS_DOUBLONS_31_12_2025.md`

---

## ❌ Dépannage rapide

### "password authentication failed"
→ Vérifiez le mot de passe dans `DATABASE_URL`

### "could not connect to server"
→ Démarrez PostgreSQL : `net start postgresql-x64-16`

### "Revision 012 is present more than once"
→ Cette erreur est **résolue** ! Utilisez les fichiers corrigés (31/12/2025)

---

**Dernière mise à jour** : 31 décembre 2025  
**Version** : PostgreSQL uniquement (SQLite supprimé depuis le 10/12/2025)

