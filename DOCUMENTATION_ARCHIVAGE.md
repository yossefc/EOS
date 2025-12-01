# Documentation du Système d'Archivage des Enquêtes

## Vue d'ensemble

Le système d'archivage des enquêtes permet de :
- Archiver les enquêtes terminées avec génération et stockage de fichiers Word
- Masquer les enquêtes archivées des tableaux principaux
- Consulter les enquêtes archivées en lecture seule
- Télécharger les fichiers d'archives générés

## Architecture

### 1. Modèles de données

#### EnqueteArchiveFile (nouveau)
**Fichier:** `backend/models/enquete_archive_file.py`

Table principale pour le stockage des fichiers d'archives :
```python
- id: Integer (PK)
- enquete_id: Integer (FK vers donnees.id, UNIQUE)
- filename: String(255) - Nom du fichier généré
- filepath: String(500) - Chemin relatif depuis exports/
- type_export: String(20) - Type de fichier (word, csv, txt)
- file_size: Integer - Taille en octets
- created_at: DateTime - Date de création
- utilisateur: String(100) - Utilisateur ayant créé l'archive
```

#### EnqueteArchive (existant)
**Fichier:** `backend/models/enquete_archive.py`

Table de compatibilité conservée pour l'historique :
```python
- id: Integer (PK)
- enquete_id: Integer (FK vers donnees.id)
- date_export: DateTime
- nom_fichier: String(255)
- utilisateur: String(100)
```

#### Donnee (modifié)
**Fichier:** `backend/models/models.py`

Le champ `statut_validation` est utilisé pour marquer les enquêtes archivées :
- `'en_attente'` : Enquête non archivée
- `'archive'` : Enquête archivée

### 2. Stockage des fichiers

**Structure des dossiers :**
```
backend/
  exports/
    archives/
      <enquete_id>/
        Enquete_<numeroDossier>_<timestamp>.docx
```

**Exemple :**
```
backend/exports/archives/123/Enquete_D2024001_20241201_143052.docx
```

### 3. Routes API

#### Routes d'archivage

##### GET /api/archives/enquetes
Récupère la liste paginée des enquêtes archivées.

**Paramètres de requête :**
- `page` (int, optionnel) : Numéro de page (défaut: 1)
- `per_page` (int, optionnel) : Nombre d'éléments par page (défaut: 50)

**Réponse :**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "numeroDossier": "D2024001",
      "nom": "Dupont",
      "prenom": "Jean",
      "typeDemande": "ABC",
      "enqueteurNom": "Martin Paul",
      "code_resultat": "P",
      "date_archive": "2024-12-01 14:30:52",
      "archive_file_id": 45,
      "filename": "Enquete_D2024001_20241201_143052.docx",
      "file_size": 52480
    }
  ],
  "page": 1,
  "per_page": 50,
  "total": 150,
  "pages": 3
}
```

##### GET /api/archives/enquetes/<enquete_id>
Récupère les détails complets d'une enquête archivée (lecture seule).

**Réponse :**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "numeroDossier": "D2024001",
    "nom": "Dupont",
    "prenom": "Jean",
    "statut_validation": "archive",
    "donnee_enqueteur": {
      "code_resultat": "P",
      "elements_retrouves": "ATBER",
      "date_retour": "2024-12-01"
    },
    "enqueteur": {
      "id": 5,
      "nom": "Martin",
      "prenom": "Paul",
      "email": "paul.martin@example.com"
    }
  }
}
```

##### POST /api/archives/enquetes/<enquete_id>/archive
Archive une enquête : génère le fichier, le stocke et met à jour le statut.

**Corps de la requête :**
```json
{
  "utilisateur": "Administrateur"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Enquête archivée avec succès",
  "data": {
    "enquete_id": 123,
    "archive_file_id": 45,
    "filename": "Enquete_D2024001_20241201_143052.docx",
    "file_size": 52480,
    "filepath": "archives/123/Enquete_D2024001_20241201_143052.docx"
  }
}
```

##### GET /api/archives/enquetes/<archive_file_id>/download
Télécharge un fichier archivé.

**Réponse :**
Fichier Word (.docx) en téléchargement direct.

#### Modifications des routes existantes

##### GET /api/donnees-complete
**Modification :** Filtre automatiquement les enquêtes archivées.
```python
.filter(Donnee.statut_validation != 'archive')
```

##### GET /api/enquetes/enqueteur/<enqueteur_id>
**Modification :** Exclut les enquêtes archivées de la liste.
```python
.filter(Donnee.statut_validation != 'archive')
```

##### GET /api/enquetes/enqueteur/<enqueteur_id>/completed
**Modification :** Exclut les enquêtes archivées des enquêtes complétées.
```python
.filter(Donnee.statut_validation != 'archive')
```

### 4. Frontend

#### Composant ArchivesViewer
**Fichier:** `frontend/src/components/ArchivesViewer.jsx`

**Fonctionnalités :**
- Affichage paginé des enquêtes archivées
- Recherche par n° dossier, nom, prénom, enquêteur
- Consultation des détails en modal (lecture seule)
- Téléchargement des fichiers d'archives
- Interface responsive et moderne

**Intégration dans tabs.jsx :**
```jsx
{
  id: 'archives',
  label: 'Archives',
  icon: <Archive className="w-4 h-4" />,
  component: <ArchivesViewer />
}
```

## Workflow d'archivage

### Scénario complet

1. **Création d'enquête**
   - Une enquête est créée avec `statut_validation = 'en_attente'`
   - Elle apparaît dans l'onglet "Données"

2. **Traitement par l'enquêteur**
   - L'enquêteur remplit les données
   - Le `code_resultat` est renseigné

3. **Validation**
   - L'administrateur valide l'enquête depuis l'onglet "Données"
   - Le statut passe à `'archive'` (peut être fait manuellement ou via une route de validation)

4. **Export et archivage**
   - Depuis l'onglet "Export des résultats", l'administrateur clique sur "Archiver & exporter"
   - Le système :
     - Génère un document Word avec toutes les données
     - Crée le dossier `exports/archives/<enquete_id>/`
     - Sauvegarde le fichier sur disque
     - Crée une entrée dans `EnqueteArchiveFile`
     - Crée une entrée dans `EnqueteArchive` (compatibilité)

5. **Disparition des tableaux**
   - L'enquête n'apparaît plus dans "Données"
   - L'enquête n'apparaît plus dans "Données enquêteur"
   - L'enquête n'apparaît plus dans les listes d'enquêtes de l'enquêteur

6. **Consultation et téléchargement**
   - L'enquête apparaît dans l'onglet "Archives"
   - L'administrateur peut :
     - Consulter les détails complets (lecture seule)
     - Télécharger le fichier Word généré

## Installation et migration

### 1. Exécuter la migration

```bash
cd backend
python migrations/add_archive_files_table.py
```

**Ce script crée :**
- La table `enquete_archive_files`
- Les index sur `enquete_id` et `created_at`

### 2. Vérifier le dossier d'archives

Le dossier `backend/exports/archives/` doit exister avec un fichier `.gitkeep`.

### 3. Redémarrer le serveur backend

```bash
cd backend
python run_server.py
```

### 4. Redémarrer le frontend

```bash
cd frontend
npm run dev
```

## Tests

### Test d'archivage

1. Créer une enquête de test
2. Assigner un enquêteur
3. Remplir les données enquêteur avec un `code_resultat`
4. Mettre le `statut_validation` à `'archive'` :
   ```sql
   UPDATE donnees SET statut_validation = 'archive' WHERE id = <enquete_id>;
   ```
5. Aller dans l'onglet "Export des résultats"
6. Cliquer sur "Archiver & exporter"
7. Vérifier que :
   - Le fichier est créé dans `backend/exports/archives/<enquete_id>/`
   - Une entrée est créée dans `enquete_archive_files`
   - L'enquête disparaît des tableaux principaux

### Test de consultation

1. Aller dans l'onglet "Archives"
2. Vérifier que l'enquête archivée apparaît
3. Cliquer sur "Consulter"
4. Vérifier que toutes les données sont affichées
5. Cliquer sur "Télécharger"
6. Vérifier que le fichier Word se télécharge correctement

### Test de filtrage

1. Aller dans l'onglet "Données"
2. Vérifier que l'enquête archivée n'apparaît pas
3. Aller dans l'onglet "Données enquêteur" (interface enquêteur)
4. Vérifier que l'enquête archivée n'apparaît pas

## Fichiers modifiés et créés

### Fichiers créés

1. **Backend - Modèles**
   - `backend/models/enquete_archive_file.py`

2. **Backend - Routes**
   - `backend/routes/archives.py`

3. **Backend - Migrations**
   - `backend/migrations/add_archive_files_table.py`

4. **Backend - Dossiers**
   - `backend/exports/archives/` (avec `.gitkeep`)

5. **Frontend - Composants**
   - `frontend/src/components/ArchivesViewer.jsx`

6. **Documentation**
   - `DOCUMENTATION_ARCHIVAGE.md` (ce fichier)

### Fichiers modifiés

1. **Backend**
   - `backend/app.py` : Ajout de l'import et enregistrement du blueprint archives
   - `backend/routes/enquetes.py` : Ajout de filtres pour exclure les enquêtes archivées

2. **Frontend**
   - `frontend/src/components/tabs.jsx` : Ajout de l'onglet Archives

## Bonnes pratiques

### Sécurité

- Les fichiers archivés sont stockés dans un dossier non accessible directement via HTTP
- Le téléchargement se fait via une route API sécurisée
- Les enquêtes archivées sont en lecture seule

### Performance

- Pagination des archives (50 par page par défaut)
- Index sur `enquete_id` et `created_at` pour des requêtes rapides
- Lazy loading du composant ArchivesViewer

### Maintenance

- Les fichiers archivés sont organisés par `enquete_id`
- Le chemin relatif est stocké en base pour faciliter les migrations
- La taille du fichier est enregistrée pour monitoring

### Évolutions futures possibles

1. **Export CSV en plus du Word**
   - Modifier `type_export` pour supporter 'csv'
   - Ajouter une fonction de génération CSV

2. **Suppression d'archives**
   - Ajouter une route DELETE pour supprimer une archive
   - Supprimer le fichier du disque et l'entrée en base

3. **Recherche avancée**
   - Filtrer par date d'archivage
   - Filtrer par enquêteur
   - Filtrer par code résultat

4. **Export multiple**
   - Permettre de télécharger plusieurs archives en ZIP

5. **Statistiques d'archives**
   - Nombre d'archives par mois
   - Espace disque utilisé
   - Archives les plus téléchargées

## Dépannage

### Le fichier d'archive n'est pas trouvé

**Symptôme :** Erreur 404 lors du téléchargement

**Solutions :**
1. Vérifier que le dossier `backend/exports/archives/<enquete_id>/` existe
2. Vérifier que le fichier existe dans ce dossier
3. Vérifier les permissions du dossier (lecture/écriture)
4. Vérifier le chemin dans `EnqueteArchiveFile.filepath`

### Les enquêtes archivées apparaissent toujours dans les tableaux

**Symptôme :** Les enquêtes avec `statut_validation = 'archive'` sont visibles

**Solutions :**
1. Vérifier que le filtre est bien appliqué dans la route API
2. Rafraîchir le cache du navigateur (Ctrl+F5)
3. Vérifier que le backend a bien été redémarré après modifications

### Erreur lors de la génération du document Word

**Symptôme :** Erreur 500 lors de l'archivage

**Solutions :**
1. Vérifier que `python-docx` est installé : `pip install python-docx`
2. Vérifier les permissions d'écriture du dossier `exports/archives/`
3. Vérifier les logs du backend pour plus de détails

### La migration échoue

**Symptôme :** Erreur lors de l'exécution du script de migration

**Solutions :**
1. Vérifier que la base de données est accessible
2. Vérifier que la table n'existe pas déjà
3. Exécuter manuellement les commandes SQL depuis un client SQLite

## Support

Pour toute question ou problème, consulter :
- Les logs du backend : `backend/logs/`
- La console du navigateur (F12)
- Cette documentation

---

**Version :** 1.0  
**Date :** 1er décembre 2024  
**Auteur :** Système EOS
