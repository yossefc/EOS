# 📥 GUIDE D'IMPORT DES FICHIERS MDB

## 🎯 Objectif

Ce guide vous explique comment importer des données depuis des fichiers Microsoft Access (.mdb) vers votre base de données PostgreSQL EOS.

---

## ⚙️ Prérequis

### 1. Microsoft Access Database Engine

Pour lire les fichiers MDB, vous devez installer le pilote ODBC Microsoft Access :

**📥 Téléchargement :**
- [Microsoft Access Database Engine 2016 Redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=54920)

**⚠️ IMPORTANT - Architecture 32-bit vs 64-bit :**

Vous devez installer la version qui correspond à votre installation Python :

1. **Vérifier l'architecture de Python :**
   ```cmd
   python --version --version
   ```
   ou
   ```cmd
   .venv\Scripts\python.exe -c "import platform; print(platform.architecture()[0])"
   ```

2. **Installer la bonne version :**
   - Si Python est **64-bit** → Installer `AccessDatabaseEngine_X64.exe`
   - Si Python est **32-bit** → Installer `AccessDatabaseEngine.exe`

### 2. Installer la dépendance Python

```cmd
cd D:\EOS
.venv\Scripts\pip.exe install pyodbc
```

---

## 🔍 ÉTAPE 1 : Analyser la structure des fichiers MDB

Avant d'importer, il est recommandé d'analyser la structure pour comprendre les tables et colonnes.

### Utilisation du script d'analyse

```cmd
cd D:\EOS
ANALYSER_FICHIERS_MDB.bat
```

Le script vous demandera :
- Le chemin du fichier .mdb ou du dossier contenant plusieurs fichiers

**Résultat :**
- Un ou plusieurs fichiers JSON seront créés avec la structure détaillée
- Exemple : `mdb_structure_fichier_20260204_131500.json`

### Exemple de rapport JSON

```json
{
  "file": "donnees.mdb",
  "analyzed_at": "2026-02-04T13:15:00",
  "tables": [
    {
      "name": "Dossiers",
      "row_count": 1250,
      "columns": [
        {"name": "NumeroDossier", "type": "VARCHAR", "size": 50},
        {"name": "Nom", "type": "VARCHAR", "size": 100},
        {"name": "Prenom", "type": "VARCHAR", "size": 100},
        ...
      ]
    }
  ]
}
```

---

## 📥 ÉTAPE 2 : Importer les données

### Utilisation du script d'import

```cmd
cd D:\EOS
IMPORTER_FICHIERS_MDB.bat
```

Le script vous demandera :
1. **Code du client** (ex: `PARTNER`, `RG_SHERLOCK`)
2. **Chemin du fichier ou dossier** contenant les fichiers .mdb
3. **Mode test** (O/N) - En mode test, aucune donnée n'est insérée

### Import en ligne de commande

Pour plus de contrôle, vous pouvez utiliser directement le script Python :

**Import d'un seul fichier :**
```cmd
.venv\Scripts\python.exe backend\import_from_mdb.py --file "chemin\vers\fichier.mdb" --client-code PARTNER
```

**Import d'un dossier complet :**
```cmd
.venv\Scripts\python.exe backend\import_from_mdb.py --folder "chemin\vers\dossier" --client-code PARTNER
```

**Mode test (dry-run) :**
```cmd
.venv\Scripts\python.exe backend\import_from_mdb.py --file "chemin\vers\fichier.mdb" --client-code PARTNER --dry-run
```

**Spécifier une table particulière :**
```cmd
.venv\Scripts\python.exe backend\import_from_mdb.py --file "chemin\vers\fichier.mdb" --client-code PARTNER --table "NomTable"
```

---

## 🗺️ Mapping des colonnes

Le script utilise un mapping par défaut entre les colonnes MDB et les champs PostgreSQL :

| Colonne MDB | Champ PostgreSQL |
|-------------|------------------|
| NumeroDossier | numeroDossier |
| Nom | nom |
| Prenom | prenom |
| DateNaissance | dateNaissance |
| Adresse1 | adresse1 |
| CodePostal | codePostal |
| ... | ... |

### Personnaliser le mapping

Si vos fichiers MDB ont des noms de colonnes différents, modifiez le dictionnaire `DEFAULT_COLUMN_MAPPING` dans le fichier [import_from_mdb.py](file:///d:/EOS/backend/import_from_mdb.py) :

```python
DEFAULT_COLUMN_MAPPING = {
    'VotreColonneMDB': 'champPostgreSQL',
    'NumDossier': 'numeroDossier',  # Exemple de personnalisation
    ...
}
```

---

## ✅ ÉTAPE 3 : Vérifier l'import

### Dans l'interface web

1. Démarrez l'application :
   ```cmd
   DEMARRER_EOS_SIMPLE.bat
   ```

2. Connectez-vous et vérifiez que les données apparaissent

### Dans PostgreSQL

```cmd
psql -U postgres -d eos_db
```

```sql
-- Compter les enregistrements importés
SELECT COUNT(*) FROM donnees WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER');

-- Voir les derniers imports
SELECT f.nom, f.date_import, COUNT(d.id) as nb_dossiers
FROM fichiers f
LEFT JOIN donnees d ON d.fichier_id = f.id
GROUP BY f.id, f.nom, f.date_import
ORDER BY f.date_import DESC
LIMIT 10;
```

---

## 🔄 ÉTAPE 4 : Synchroniser avec l'autre ordinateur

Une fois les données importées sur cet ordinateur, vous pouvez les synchroniser avec l'autre :

### Sur cet ordinateur (source) :
```cmd
SYNCHRONISER_VERS_AUTRE_ORDI.bat
```

### Sur l'autre ordinateur (cible) :
```cmd
IMPORTER_DEPUIS_AUTRE_ORDI.bat
```

Consultez [LISEZMOI_SYNCHRONISATION.txt](file:///d:/EOS/LISEZMOI_SYNCHRONISATION.txt) pour plus de détails.

---

## ❓ Résolution de problèmes

### ❌ "Aucun pilote Microsoft Access ODBC trouvé"

**Solution :**
1. Installez Microsoft Access Database Engine 2016 Redistributable
2. Vérifiez que la version (32-bit/64-bit) correspond à votre Python
3. Testez avec : `ANALYSER_FICHIERS_MDB.bat`

---

### ❌ "Erreur de connexion au fichier MDB"

**Causes possibles :**
- Le fichier est ouvert dans Microsoft Access → Fermez-le
- Le fichier .ldb (verrouillage) existe → Supprimez-le
- Permissions insuffisantes → Exécutez en tant qu'administrateur

---

### ❌ "Client 'XXX' introuvable"

**Solution :**
Vérifiez que le client existe dans la base de données :

```sql
SELECT code, nom FROM clients;
```

Si le client n'existe pas, créez-le via l'interface web ou avec un script SQL.

---

### ❌ Colonnes manquantes ou mal mappées

**Solution :**
1. Analysez d'abord la structure avec `ANALYSER_FICHIERS_MDB.bat`
2. Consultez le rapport JSON généré
3. Modifiez `DEFAULT_COLUMN_MAPPING` dans `import_from_mdb.py` si nécessaire

---

## 📝 Récapitulatif rapide

```cmd
# 1. Installer le pilote ODBC (une seule fois)
# Télécharger et installer Access Database Engine 2016

# 2. Installer pyodbc (une seule fois)
cd D:\EOS
.venv\Scripts\pip.exe install pyodbc

# 3. Analyser la structure (optionnel mais recommandé)
ANALYSER_FICHIERS_MDB.bat

# 4. Importer les données
IMPORTER_FICHIERS_MDB.bat

# 5. Vérifier dans l'interface web
DEMARRER_EOS_SIMPLE.bat
```

---

## 📚 Fichiers créés

| Fichier | Description |
|---------|-------------|
| `backend/analyze_mdb_structure.py` | Script d'analyse de structure MDB |
| `backend/import_from_mdb.py` | Script d'import MDB vers PostgreSQL |
| `ANALYSER_FICHIERS_MDB.bat` | Script batch d'analyse |
| `IMPORTER_FICHIERS_MDB.bat` | Script batch d'import |
| `GUIDE_IMPORT_MDB.md` | Ce guide |

---

**Bonne importation ! 🚀**
