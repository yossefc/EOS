# ✅ CHECKLIST - Installation sur nouvel ordinateur

Date : 31 décembre 2025

---

## 📋 AVANT DE COMMENCER

- [ ] PostgreSQL est installé (version 14 ou supérieure)
- [ ] Python est installé (version 3.11 ou supérieure)
- [ ] Vous avez le mot de passe PostgreSQL

---

## 🚀 MÉTHODE RAPIDE (Recommandée)

### Option 1 : Script automatique

- [ ] Double-cliquez sur `INSTALLER_BASE_DONNEES.bat`
- [ ] Entrez vos identifiants PostgreSQL quand demandé
- [ ] Attendez que les migrations s'appliquent
- [ ] Notez la commande `DATABASE_URL` affichée à la fin
- [ ] Lancez `DEMARRER_EOS_COMPLET.bat`

✅ **C'est terminé !**

---

## 📝 MÉTHODE MANUELLE (Si nécessaire)

### Étape 1 : Démarrer PostgreSQL

- [ ] Ouvrir un terminal en **Administrateur**
- [ ] Exécuter : `net start postgresql-x64-16`
- [ ] Vérifier qu'il n'y a pas d'erreur

### Étape 2 : Créer la base de données

- [ ] Ouvrir un terminal
- [ ] Exécuter : `psql -U postgres`
- [ ] Taper : `CREATE DATABASE eos_db;`
- [ ] Taper : `\q` pour quitter

### Étape 3 : Configurer DATABASE_URL

**Git Bash :**
- [ ] Copier et modifier cette commande avec votre mot de passe :
  ```bash
  export DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"
  ```

**PowerShell :**
- [ ] Copier et modifier cette commande avec votre mot de passe :
  ```powershell
  $env:DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"
  ```

### Étape 4 : Appliquer les migrations

- [ ] Ouvrir un terminal dans `D:\eos`
- [ ] Exécuter : `python backend/apply_migrations.py`
- [ ] Vérifier qu'il n'y a pas d'erreur
- [ ] Voir les messages `INFO [alembic.runtime.migration]`

### Étape 5 : Vérifier (Optionnel)

- [ ] Exécuter : `python verifier_migrations.py`
- [ ] Vérifier que le message final est : `✓ Vérification terminée avec succès !`

### Étape 6 : Démarrer l'application

- [ ] Double-cliquer sur `DEMARRER_EOS_COMPLET.bat`
- [ ] Attendre que le backend démarre (http://localhost:5000)
- [ ] Attendre que le frontend démarre (http://localhost:5173)
- [ ] Ouvrir http://localhost:5173 dans votre navigateur

---

## ❌ EN CAS DE PROBLÈME

### Erreur : "password authentication failed"

- [ ] Vérifier que le mot de passe dans `DATABASE_URL` est correct
- [ ] Tester la connexion : `psql -U postgres -d eos_db`
- [ ] Si le mot de passe est oublié, le réinitialiser :
  ```bash
  psql -U postgres
  \password postgres
  ```

### Erreur : "could not connect to server"

- [ ] Vérifier que PostgreSQL est démarré :
  ```bash
  net start postgresql-x64-16
  ```
- [ ] Vérifier que PostgreSQL écoute sur le port 5432 :
  ```bash
  netstat -an | findstr 5432
  ```

### Erreur : "Revision 012 is present more than once"

Cette erreur est **normalement résolue**. Si elle persiste :

- [ ] Supprimer le cache Python :
  ```powershell
  Remove-Item -Recurse backend\migrations\versions\__pycache__
  ```
- [ ] Vérifier que vous utilisez les fichiers corrigés (date : 31/12/2025)
- [ ] Réessayer : `python backend/apply_migrations.py`

### Le backend ou frontend ne démarre pas

Backend :
- [ ] Vérifier que `DATABASE_URL` est défini
- [ ] Vérifier que les dépendances sont installées : `pip install -r backend/requirements.txt`
- [ ] Relancer : `REDEMARRER_BACKEND.bat`

Frontend :
- [ ] Vérifier que Node.js est installé : `node --version`
- [ ] Réinstaller les dépendances : `cd frontend && npm install`
- [ ] Relancer : `REDEMARRER_FRONTEND.bat`

### Je veux recommencer à zéro

- [ ] Se connecter à PostgreSQL : `psql -U postgres`
- [ ] Supprimer la base : `DROP DATABASE IF EXISTS eos_db;`
- [ ] Recréer la base : `CREATE DATABASE eos_db;`
- [ ] Quitter : `\q`
- [ ] Réappliquer les migrations : `python backend/apply_migrations.py`

---

## 📚 DOCUMENTATION DISPONIBLE

Documents de référence créés pour vous aider :

- [ ] **PROBLEME_RESOLU_LISEZMOI.md** - Explication simple du problème et solution
- [ ] **INSTALLATION_RAPIDE.md** - Guide d'installation (1 page)
- [ ] **GUIDE_INSTALLATION_APRES_CORRECTION_MIGRATIONS.md** - Guide complet avec dépannage
- [ ] **__CORRECTION_MIGRATIONS_LISEZMOI__.txt** - Résumé technique détaillé
- [ ] **CORRECTION_MIGRATIONS_RESUME.md** - Résumé de la correction
- [ ] **verifier_migrations.py** - Script de vérification des migrations

---

## ✅ VÉRIFICATION FINALE

Une fois l'installation terminée, vérifiez que :

- [ ] Le backend démarre sans erreur (`python backend/app.py`)
- [ ] Le frontend s'ouvre dans le navigateur (http://localhost:5173)
- [ ] Vous pouvez vous connecter à l'interface administrateur
- [ ] Les tables de la base de données existent :
  ```bash
  psql -U postgres -d eos_db -c "\dt"
  ```

---

## 🎉 FÉLICITATIONS !

Si toutes les étapes sont cochées, votre installation est **complète et fonctionnelle** !

Vous pouvez maintenant :
- Importer des fichiers d'enquêtes
- Assigner des enquêtes aux enquêteurs
- Exporter les résultats (EOS et PARTNER)
- Gérer les tarifs et la facturation

---

**Besoin d'aide ?**

Consultez les documents de référence listés ci-dessus ou relisez les messages d'erreur dans le terminal pour identifier le problème.

**Date de création** : 31 décembre 2025  
**Version du correctif** : 1.0

