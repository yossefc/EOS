# Guide de démarrage rapide - PostgreSQL

## Installation en 5 étapes

### 1️⃣ Installer PostgreSQL

**Windows** : Télécharger depuis https://www.postgresql.org/download/windows/

**Linux (Ubuntu/Debian)** :
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Mac** :
```bash
brew install postgresql
```

---

### 2️⃣ Créer la base de données

Ouvrir un terminal PostgreSQL :

```bash
# Windows
psql -U postgres

# Linux/Mac
sudo -u postgres psql
```

Puis exécuter :

```sql
CREATE USER eos_user WITH PASSWORD 'eos_password';
CREATE DATABASE eos_db OWNER eos_user;
GRANT ALL PRIVILEGES ON DATABASE eos_db TO eos_user;
\q
```

---

### 3️⃣ Configurer l'application

**Windows PowerShell** :
```powershell
cd D:\EOS\backend
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
pip install -r requirements.txt
```

**Linux/Mac** :
```bash
cd /path/to/EOS/backend
export DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
pip install -r requirements.txt
```

---

### 4️⃣ Créer les tables

```bash
flask db upgrade
```

Vous devriez voir :
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial migration
```

---

### 5️⃣ Migrer les données (optionnel)

Si vous avez des données SQLite existantes :

```bash
python migrate_sqlite_to_postgresql.py
```

Suivre les instructions à l'écran.

---

## Démarrer l'application

### Backend

```bash
cd backend
flask run
```

Ou :

```bash
python app.py
```

### Frontend

```bash
cd frontend
npm run dev
```

---

## Vérification

Ouvrir http://localhost:5173

✅ Vous devriez voir la liste des enquêtes avec pagination
✅ Essayez de changer de page
✅ Essayez les filtres (type de demande, enquêteur, etc.)

---

## Aide rapide

### Voir les tables créées

```bash
psql -U eos_user -d eos_db
\dt
```

### Compter les enquêtes

```sql
SELECT COUNT(*) FROM donnees;
```

### Vérifier les index

```sql
\di
```

### Backup

```bash
pg_dump -U eos_user -d eos_db > backup_$(date +%Y%m%d).sql
```

---

## Problèmes courants

### Erreur : "role eos_user does not exist"

Retour à l'étape 2 : créer l'utilisateur

### Erreur : "could not connect to server"

PostgreSQL n'est pas démarré :

**Windows** : Services → PostgreSQL → Démarrer

**Linux** :
```bash
sudo service postgresql start
```

**Mac** :
```bash
brew services start postgresql
```

### Erreur : "psycopg2 not found" ou erreur de compilation

**Si vous utilisez Python 3.13** :
```bash
pip install psycopg2-binary --upgrade
```

**Si ça ne fonctionne pas** (Python < 3.12), installer Visual C++ Build Tools :
https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## Pour en savoir plus

Voir le rapport complet : `MIGRATION_POSTGRESQL_RAPPORT.md`

