# 📋 Flux de Validation → Export → Archive - Documentation Complète

## 🎯 Vue d'ensemble

Ce document décrit le nouveau système de gestion des enquêtes avec 4 statuts distincts et un flux clair entre les onglets.

---

## 📊 Statuts des Enquêtes

### 1. `en_attente`
- **Description** : Enquête créée, en attente de traitement par l'enquêteur
- **Visible dans** : Onglet "Données"
- **Actions possibles** : Assignation à un enquêteur

### 2. `confirmee`
- **Description** : Enquêteur a terminé son enquête (données remplies)
- **Visible dans** : Onglet "Données" (avec boutons de validation)
- **Actions possibles** : Validation ou refus par l'administrateur

### 3. `validee`
- **Description** : Admin a validé l'enquête, prête pour l'export
- **Visible dans** : Onglet "Export des résultats"
- **Actions possibles** : Inclusion dans un export groupé

### 4. `archivee`
- **Description** : Enquête exportée dans un fichier Word et archivée
- **Visible dans** : Onglet "Archives" (via les exports batch)
- **Actions possibles** : Re-téléchargement du fichier Word

---

## 🔄 Flux Utilisateur Complet

### Étape 1 : Remplissage de l'enquête
1. L'utilisateur importe un fichier ou crée une enquête manuellement
2. L'enquête a le statut `en_attente`
3. L'enquête est assignée à un enquêteur

### Étape 2 : Traitement par l'enquêteur
1. L'enquêteur remplit les données de l'enquête
2. L'enquêteur confirme l'enquête → statut passe à `confirmee`

### Étape 3 : Validation par l'admin (Onglet "Données")
1. L'admin voit l'enquête avec le statut `confirmee`
2. L'admin clique sur "Valider" → statut passe à `validee`
3. L'enquête disparaît de l'onglet "Données"
4. L'enquête apparaît dans l'onglet "Export des résultats"

### Étape 4 : Export groupé (Onglet "Export des résultats")
1. L'admin voit toutes les enquêtes avec le statut `validee`
2. L'admin clique sur "Créer un nouvel export (N enquêtes)"
3. Le système :
   - Génère un fichier Word (.docx) avec toutes les enquêtes validées
   - Chaque enquête est sur une page séparée avec un design professionnel
   - Sauvegarde le fichier sur le disque dans `exports/batches/`
   - Crée une entrée `ExportBatch` en base de données
   - Change le statut de toutes les enquêtes exportées à `archivee`
   - Télécharge automatiquement le fichier Word
4. Les enquêtes exportées disparaissent de l'onglet "Export des résultats"

### Étape 5 : Consultation des archives (Onglet "Archives")
1. L'admin voit la liste de tous les exports batch créés
2. Pour chaque export, il voit :
   - Le nom du fichier
   - Le nombre d'enquêtes incluses
   - La taille du fichier
   - La date de création
   - L'utilisateur qui a créé l'export
3. L'admin peut re-télécharger n'importe quel fichier à tout moment

---

## 🗂️ Fichiers Modifiés

### Backend

#### 1. **`backend/routes/validation_v2.py`**
- **Modification** : Changement du statut de `archive` à `validee` lors de la validation
- **Fonction** : `valider_enquete()`
- **Changement clé** : 
  ```python
  donnee.statut_validation = 'validee'  # Au lieu de 'archive'
  ```

#### 2. **`backend/models/export_batch.py`** ✨ NOUVEAU
- **Description** : Modèle pour tracker les exports groupés
- **Champs** :
  - `id` : ID unique
  - `filename` : Nom du fichier Word
  - `filepath` : Chemin relatif depuis `exports/`
  - `file_size` : Taille en octets
  - `enquete_count` : Nombre d'enquêtes dans le batch
  - `created_at` : Date de création
  - `utilisateur` : Utilisateur ayant créé l'export
  - `enquete_ids` : Liste des IDs d'enquêtes (format CSV)

#### 3. **`backend/routes/export.py`**
- **Nouvelles routes** :
  
  **a) `GET /api/exports/validated`**
  - Récupère toutes les enquêtes avec statut `validee`
  - Pagination supportée
  - Retourne les détails complets pour affichage
  
  **b) `POST /api/exports/create-batch`**
  - Crée un export groupé de toutes les enquêtes validées
  - Génère un fichier Word (.docx)
  - Sauvegarde sur disque dans `exports/batches/`
  - Marque les enquêtes comme `archivee`
  - Crée une entrée `ExportBatch`
  - Retourne le fichier pour téléchargement
  
  **c) `GET /api/exports/batches`**
  - Récupère la liste des exports batch
  - Pagination supportée
  
  **d) `GET /api/exports/batches/<batch_id>/download`**
  - Télécharge un fichier d'export batch existant

#### 4. **`backend/app.py`**
- **Modification** : Import du modèle `ExportBatch` pour création de la table
- **Ligne ajoutée** :
  ```python
  from models.export_batch import ExportBatch
  ```

### Frontend

#### 1. **`frontend/src/components/EnqueteExporter.jsx`**
- **Refonte complète** :
  - Affiche maintenant les enquêtes **validées** (statut `validee`)
  - Au lieu d'afficher les archives
  - Bouton "Créer un nouvel export" appelle `/api/exports/create-batch`
  - Tableau affiche : N° Dossier, Nom, Prénom, Type Demande, Enquêteur, Code Résultat, Date Validation
  - Après export, recharge la liste (qui devrait être vide)

#### 2. **`frontend/src/components/ArchivesViewer.jsx`**
- **Refonte complète** :
  - Affiche maintenant les **exports batch** au lieu des enquêtes individuelles
  - Appelle `/api/exports/batches` pour récupérer les données
  - Tableau affiche : Nom du fichier, Nb Enquêtes, Taille, Date création, Utilisateur
  - Bouton "Télécharger" pour chaque export batch
  - Fonction `formatFileSize()` pour afficher la taille en KB/MB

---

## 🗄️ Structure de la Base de Données

### Nouvelle Table : `export_batches`

```sql
CREATE TABLE export_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    file_size INTEGER,
    enquete_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilisateur VARCHAR(100),
    enquete_ids TEXT
);
```

### Modification de la table `donnees`
- Le champ `statut_validation` accepte maintenant 4 valeurs :
  - `en_attente`
  - `confirmee`
  - `validee`
  - `archivee`

---

## 📁 Structure des Fichiers sur Disque

```
backend/
├── exports/
│   └── batches/
│       ├── Export_Batch_20251201_190000_5_enquetes.docx
│       ├── Export_Batch_20251201_200000_3_enquetes.docx
│       └── ...
```

**Format du nom de fichier** :
```
Export_Batch_{timestamp}_{nombre_enquetes}_enquetes.docx
```

Exemple : `Export_Batch_20251201_190000_5_enquetes.docx`
- Date : 2025-12-01
- Heure : 19:00:00
- Nombre d'enquêtes : 5

---

## 🎨 Design du Fichier Word Exporté

Chaque enquête dans le fichier Word contient :

### Page de couverture (par enquête)
- **Titre** : Enquête n°{id} – {nom} {prenom}
- **Sous-titre** : Date | Enquêteur | Statut

### Tableau des données
- **Colonnes** : Champ | Valeur
- **Lignes** : Toutes les données importantes de l'enquête
  - Informations de base (N° Dossier, Type, etc.)
  - État civil
  - Adresse
  - Employeur
  - Données bancaires
  - Résultats de l'enquête

### Section Notes
- Commentaires de l'enquête
- Notes personnelles de l'enquêteur

---

## 🔒 Sécurité et Validation

### Validation côté Backend

1. **Validation d'une enquête** (`PUT /api/enquetes/<id>/valider`)
   - Vérifie que l'enquête existe
   - Vérifie qu'il y a une réponse d'enquêteur
   - Vérifie que le statut est `confirmee`
   - Empêche la double validation

2. **Création d'un export batch** (`POST /api/exports/create-batch`)
   - Vérifie qu'il y a des enquêtes validées
   - Génère le fichier Word
   - Sauvegarde sur disque
   - Transaction atomique (tout ou rien)
   - Rollback en cas d'erreur

3. **Téléchargement d'un export** (`GET /api/exports/batches/<id>/download`)
   - Vérifie que l'export existe
   - Vérifie que le fichier existe sur disque
   - Retourne une erreur 404 si introuvable

---

## 🧪 Tests Manuels Recommandés

### Test 1 : Validation d'une enquête
1. Aller dans l'onglet "Données"
2. Trouver une enquête avec statut `confirmee`
3. Cliquer sur "Valider"
4. Vérifier que l'enquête disparaît de "Données"
5. Aller dans "Export des résultats"
6. Vérifier que l'enquête apparaît dans le tableau

### Test 2 : Création d'un export groupé
1. Aller dans "Export des résultats"
2. Vérifier qu'il y a des enquêtes validées
3. Cliquer sur "Créer un nouvel export (N)"
4. Confirmer l'action
5. Vérifier que le fichier Word est téléchargé
6. Ouvrir le fichier Word et vérifier le contenu
7. Vérifier que les enquêtes ont disparu de "Export des résultats"

### Test 3 : Consultation des archives
1. Aller dans l'onglet "Archives"
2. Vérifier que l'export créé apparaît dans le tableau
3. Vérifier les informations (nom, taille, date, utilisateur)
4. Cliquer sur "Télécharger"
5. Vérifier que le fichier est re-téléchargé correctement

### Test 4 : Flux complet
1. Créer une enquête → statut `en_attente`
2. Assigner à un enquêteur
3. Remplir les données enquêteur → statut `confirmee`
4. Valider dans "Données" → statut `validee`
5. Créer un export dans "Export des résultats" → statut `archivee`
6. Vérifier dans "Archives" que l'export est disponible

---

## 📝 Notes Importantes

### Gestion des Statuts
- **Ne jamais** passer directement de `en_attente` à `archivee`
- **Toujours** respecter le flux : `en_attente` → `confirmee` → `validee` → `archivee`
- Le statut `refusee` existe mais n'est pas utilisé dans ce flux

### Fichiers sur Disque
- Les fichiers Word sont sauvegardés dans `backend/exports/batches/`
- Ce dossier doit avoir les permissions d'écriture
- Les fichiers ne sont **jamais supprimés** automatiquement
- Pour nettoyer, il faut supprimer manuellement les fichiers ET les entrées en base

### Performance
- La génération d'un fichier Word avec 100+ enquêtes peut prendre plusieurs secondes
- Le frontend affiche un indicateur de chargement pendant la génération
- Les fichiers générés peuvent être volumineux (plusieurs MB)

### Limitations Actuelles
- Pas de limite sur le nombre d'enquêtes par export
- Pas de sélection manuelle des enquêtes à exporter (toutes les validées sont exportées)
- Pas de prévisualisation avant export
- Pas de suppression d'exports archivés depuis l'interface

---

## 🚀 Améliorations Futures Possibles

1. **Sélection manuelle des enquêtes à exporter**
   - Ajouter des checkboxes dans "Export des résultats"
   - Permettre de créer des exports partiels

2. **Prévisualisation du fichier Word**
   - Générer un aperçu PDF
   - Afficher dans un modal avant téléchargement

3. **Suppression d'exports archivés**
   - Ajouter un bouton "Supprimer" dans "Archives"
   - Supprimer le fichier sur disque ET l'entrée en base

4. **Statistiques d'export**
   - Nombre total d'enquêtes archivées
   - Taille totale des exports
   - Graphiques d'évolution

5. **Notifications**
   - Email à l'admin quand un export est créé
   - Notification quand des enquêtes sont prêtes pour export

---

## 📞 Support

Pour toute question ou problème, consulter :
- Les logs du backend : `backend/logs/`
- Les logs du navigateur : Console DevTools
- Ce document de référence

---

**Date de création** : 2025-12-01  
**Version** : 1.0  
**Auteur** : Système EOS
