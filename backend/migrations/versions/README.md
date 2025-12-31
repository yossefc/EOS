# Migrations Alembic

Ce dossier contient les migrations de base de données générées par Alembic.

## Commandes utiles

### Créer une nouvelle migration
```bash
flask db migrate -m "Description de la migration"
```

### Appliquer les migrations
```bash
flask db upgrade
```

### Revenir en arrière
```bash
flask db downgrade
```

### Voir l'historique
```bash
flask db history
```

### Voir le statut actuel
```bash
flask db current
```

## Première utilisation

Si vous démarrez avec une base PostgreSQL vide :

1. Configurer la variable d'environnement DATABASE_URL :
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
   
   # Linux/Mac
   export DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
   ```

2. Appliquer les migrations :
   ```bash
   flask db upgrade
   ```

## Migration depuis SQLite

Utilisez le script `migrate_sqlite_to_postgresql.py` fourni pour migrer vos données existantes.






