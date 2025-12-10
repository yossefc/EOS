# Guide Multi-Client - Application EOS

## 📋 Vue d'ensemble

L'application EOS supporte désormais plusieurs clients. Chaque client peut avoir son propre format de fichier d'import (TXT à positions fixes, Excel, etc.).

### ✨ Fonctionnalités

- **Support multi-client** : Gérez plusieurs clients dans la même application
- **Profils d'import configurables** : Chaque client peut avoir son propre format de fichier
- **Isolation des données** : Les données de chaque client sont complètement isolées
- **Rétro-compatibilité** : EOS reste le client par défaut, l'application fonctionne sans changement

---

## 🏗️ Architecture

### Modèles de données

1. **Client** (`clients`)
   - `id`: Identifiant unique
   - `code`: Code unique (ex: 'EOS', 'CLIENT_B')
   - `nom`: Nom du client
   - `actif`: Client actif/inactif

2. **ImportProfile** (`import_profiles`)
   - `client_id`: Référence au client
   - `name`: Nom du profil
   - `file_type`: Type de fichier ('TXT_FIXED', 'EXCEL')
   - `sheet_name`: Nom de la feuille (pour Excel)
   - `encoding`: Encodage du fichier

3. **ImportFieldMapping** (`import_field_mappings`)
   - `import_profile_id`: Référence au profil
   - `internal_field`: Nom du champ dans le modèle `Donnee`
   - `start_pos` / `length`: Position et longueur (pour TXT_FIXED)
   - `column_name`: Nom de la colonne (pour EXCEL)

### Modifications des tables existantes

Toutes les tables principales ont maintenant une colonne `client_id` :
- `fichiers`
- `donnees`
- `donnees_enqueteur`
- `enquete_archive_files`
- `export_batches`

---

## 🚀 Utilisation

### Backend (API)

#### 1. Import de fichier avec client

```python
# Importer un fichier pour un client spécifique
POST /parse
Content-Type: multipart/form-data

file: fichier.txt
client_id: 1  # Optionnel, EOS par défaut
# OU
client_code: EOS  # Optionnel
date_butoir: 2025-12-31  # Optionnel
```

#### 2. Lister les données d'un client

```python
# Récupérer les données d'un client
GET /api/donnees-complete?client_id=1
# OU
GET /api/donnees-complete?client_code=EOS
# Sans paramètre = EOS par défaut
GET /api/donnees-complete
```

#### 3. Récupérer la liste des clients actifs

```python
GET /api/clients

Response:
{
  "success": true,
  "clients": [
    {
      "id": 1,
      "code": "EOS",
      "nom": "EOS France",
      "actif": true
    }
  ]
}
```

### Frontend (React)

Le frontend détecte automatiquement s'il y a plusieurs clients :

- **1 seul client (EOS)** : Interface normale, pas de sélecteur
- **Plusieurs clients** : Sélecteur de client affiché dans ImportHandler et DataViewer

```jsx
// Le client est sélectionné automatiquement
// Les données sont automatiquement filtrées par client
```

---

## 🔧 Configuration d'un nouveau client

### 1. Créer le client en base

```python
from models import Client, ImportProfile, ImportFieldMapping
from extensions import db

# Créer le client
nouveau_client = Client(
    code='CLIENT_B',
    nom='Client B',
    actif=True
)
db.session.add(nouveau_client)
db.session.commit()
```

### 2. Créer le profil d'import

#### Pour un fichier TXT à positions fixes

```python
# Créer le profil
profil = ImportProfile(
    client_id=nouveau_client.id,
    name='Client B - Format TXT',
    file_type='TXT_FIXED',
    encoding='utf-8',
    actif=True
)
db.session.add(profil)
db.session.commit()

# Créer les mappings de champs
mappings = [
    ('numeroDossier', 0, 10),
    ('nom', 10, 30),
    ('prenom', 40, 20),
    # ... etc
]

for field, start, length in mappings:
    mapping = ImportFieldMapping(
        import_profile_id=profil.id,
        internal_field=field,
        start_pos=start,
        length=length,
        strip_whitespace=True
    )
    db.session.add(mapping)

db.session.commit()
```

#### Pour un fichier Excel

```python
# Créer le profil
profil = ImportProfile(
    client_id=nouveau_client.id,
    name='Client B - Format Excel',
    file_type='EXCEL',
    sheet_name='Enquetes',  # Nom de la feuille
    encoding='utf-8',
    actif=True
)
db.session.add(profil)
db.session.commit()

# Créer les mappings de champs
mappings = [
    ('numeroDossier', 'N° Dossier'),
    ('nom', 'Nom'),
    ('prenom', 'Prénom'),
    # ... etc
]

for field, column_name in mappings:
    mapping = ImportFieldMapping(
        import_profile_id=profil.id,
        internal_field=field,
        column_name=column_name,
        strip_whitespace=True
    )
    db.session.add(mapping)

db.session.commit()
```

---

## 🧪 Tests

### Lancer les tests multi-client

```bash
cd backend
pytest tests/test_multi_client.py -v
```

### Tests inclus

- Création de clients
- Création de profils d'import
- Isolation des données entre clients
- Contestations au sein d'un même client
- Rétro-compatibilité (EOS par défaut)

---

## 📝 Migration depuis SQLite/PostgreSQL existant

La migration `002_multi_client` effectue automatiquement :

1. Création des tables `clients`, `import_profiles`, `import_field_mappings`
2. Ajout de `client_id` aux tables existantes
3. Création du client EOS par défaut
4. Création du profil d'import EOS avec les mappings actuels
5. Migration des données existantes vers le client EOS

```bash
# Lancer la migration
flask db upgrade
```

---

## ⚠️ Points d'attention

### Sécurité

- Les données sont isolées par `client_id`
- Une contestation ne peut lier que des enquêtes du même client
- Les exports sont filtrés par client

### Performance

- Indexes ajoutés sur `client_id` dans toutes les tables
- Index composites `(client_id, statut_validation)` pour les requêtes fréquentes

### Rétro-compatibilité

- Si aucun `client_id` n'est fourni, EOS est utilisé par défaut
- Les anciennes routes API continuent de fonctionner
- Le frontend s'adapte automatiquement (sélecteur masqué si un seul client)

---

## 🔄 Workflow typique

### Pour EOS (comportement par défaut)

1. Importer un fichier TXT (aucun changement)
2. Les données sont automatiquement associées à EOS
3. L'interface ne montre aucun sélecteur de client

### Pour un nouveau client

1. Créer le client en base
2. Configurer son profil d'import (TXT ou Excel)
3. Définir les mappings de champs
4. Le sélecteur de client apparaît automatiquement dans l'interface
5. Importer un fichier en sélectionnant le client

---

## 📚 Ressources

- **Modèles** : `backend/models/client.py`, `backend/models/import_config.py`
- **Utilitaires** : `backend/client_utils.py`
- **Moteur d'import** : `backend/import_engine.py`
- **Migration** : `backend/migrations/versions/002_add_multi_client_support.py`
- **Tests** : `backend/tests/test_multi_client.py`

---

## 🎯 Exemple complet

Voir le fichier `backend/scripts/add_new_client.py` pour un exemple complet de création d'un nouveau client avec son profil d'import.

```bash
# Créer un nouveau client
python backend/scripts/add_new_client.py --code CLIENT_B --name "Client B" --format TXT_FIXED
```

