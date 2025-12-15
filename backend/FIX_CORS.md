# 🔧 Fix CORS - Problème résolu

## Problème

Le frontend sur `http://172.18.240.1:5173` ne pouvait pas accéder au backend car l'IP n'était pas autorisée dans la configuration CORS.

## Solution appliquée

L'IP `172.18.240.1:5173` a été ajoutée aux origines CORS autorisées dans `backend/config.py`.

## Pour appliquer le fix

**1. Arrêter le serveur Flask** (Ctrl+C dans le terminal)

**2. Redémarrer le serveur** :

```powershell
cd D:\EOS\backend
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
python app.py
```

Ou double-cliquer sur `START_POSTGRESQL.ps1`

**3. Rafraîchir le frontend** (F5 dans le navigateur)

## Vérification

Le frontend devrait maintenant pouvoir accéder au backend sans erreur CORS.

---

## Configuration CORS actuelle

**Origines autorisées** :
- `http://localhost:5173`
- `http://192.168.175.1:5173`
- `http://172.18.240.1:5173` ⭐ AJOUTÉ

## Si vous avez encore des problèmes CORS

### Option 1 : Autoriser toutes les origines (DÉVELOPPEMENT uniquement)

Dans `backend/app.py`, remplacer la configuration CORS par :

```python
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Autorise toutes les origines
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

### Option 2 : Ajouter une nouvelle IP

Si vous accédez depuis une autre IP (ex: `192.168.1.100`), ajoutez-la dans `config.py` :

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 
    'http://localhost:5173,http://192.168.175.1:5173,http://172.18.240.1:5173,http://192.168.1.100:5173'
).split(',')
```

### Option 3 : Variable d'environnement

Définir `CORS_ORIGINS` avant de lancer Flask :

```powershell
$env:CORS_ORIGINS="http://localhost:5173,http://172.18.240.1:5173,http://VOTRE_IP:5173"
```

---

**✅ Le problème CORS devrait être résolu après redémarrage du serveur !**


