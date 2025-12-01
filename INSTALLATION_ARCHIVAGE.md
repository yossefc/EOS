# Installation du Système d'Archivage - Guide Rapide

## Prérequis

Avant de commencer, assurez-vous que :
- ✅ Le backend Flask est fonctionnel
- ✅ Le frontend React est fonctionnel
- ✅ La bibliothèque `python-docx` est installée

Si `python-docx` n'est pas installé :
```bash
cd backend
pip install python-docx
```

---

## Installation en 5 étapes

### Étape 1 : Exécuter la migration de base de données

```bash
cd backend
python migrations/add_archive_files_table.py
```

**Résultat attendu :**
```
✓ Table enquete_archive_files créée avec succès
✓ Index créés avec succès
```

**En cas d'erreur :**
- Vérifiez que la base de données est accessible
- Vérifiez que vous êtes dans le bon dossier (`backend/`)
- Vérifiez que le fichier `instance/eos.db` existe

---

### Étape 2 : Vérifier la structure des dossiers

Le dossier d'archives doit exister :

```bash
# Depuis la racine du projet
ls backend/exports/archives/
```

**Contenu attendu :**
```
.gitkeep
```

Si le dossier n'existe pas, il sera créé automatiquement lors du premier archivage.

---

### Étape 3 : Redémarrer le backend

```bash
cd backend
python run_server.py
```

**Vérification :**
- Le serveur démarre sans erreur
- Aucun message d'erreur concernant les imports
- Le message "Blueprints enregistrés" apparaît dans les logs

**Test rapide :**
Ouvrez votre navigateur et allez sur :
```
http://localhost:5000/api/archives/enquetes
```

Vous devriez voir :
```json
{
  "success": true,
  "data": [],
  "page": 1,
  "per_page": 50,
  "total": 0,
  "pages": 0
}
```

---

### Étape 4 : Redémarrer le frontend

```bash
cd frontend
npm run dev
```

**Vérification :**
- L'application démarre sans erreur
- Aucune erreur dans la console du navigateur (F12)

---

### Étape 5 : Vérifier l'interface

1. Ouvrez l'application dans votre navigateur
2. Vérifiez que l'onglet **"Archives"** est visible dans la barre de navigation
3. Cliquez sur l'onglet "Archives"
4. Vous devriez voir : "Aucune archive trouvée" (normal si aucune enquête n'a été archivée)

---

## Test du système

### Test 1 : Archiver une enquête

#### Méthode manuelle (pour tester rapidement)

1. **Préparer une enquête de test**
   
   Ouvrez un client SQLite (par exemple DB Browser for SQLite) et exécutez :
   
   ```sql
   -- Trouver une enquête avec des données enquêteur
   SELECT d.id, d.numeroDossier, d.nom, d.prenom, d.statut_validation, de.code_resultat
   FROM donnees d
   LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
   WHERE de.code_resultat IS NOT NULL
   LIMIT 1;
   ```

2. **Mettre l'enquête en statut 'archive'**
   
   ```sql
   UPDATE donnees 
   SET statut_validation = 'archive' 
   WHERE id = <ID_DE_L_ENQUETE>;
   ```

3. **Archiver via l'API**
   
   Utilisez un outil comme Postman ou curl :
   
   ```bash
   curl -X POST http://localhost:5000/api/archives/enquetes/<ID_DE_L_ENQUETE>/archive \
     -H "Content-Type: application/json" \
     -d '{"utilisateur": "Test"}'
   ```

4. **Vérifier le résultat**
   
   - Allez dans l'onglet "Archives" de l'application
   - L'enquête doit apparaître dans la liste
   - Cliquez sur "Télécharger" pour obtenir le fichier Word
   - Vérifiez que le fichier existe dans `backend/exports/archives/<ID_ENQUETE>/`

### Test 2 : Vérifier le filtrage

1. **Onglet "Données"**
   - L'enquête archivée ne doit PAS apparaître

2. **Onglet "Archives"**
   - L'enquête archivée DOIT apparaître

3. **Bouton "Consulter"**
   - Cliquez sur "Consulter" dans l'onglet Archives
   - Vérifiez que toutes les données s'affichent correctement

### Test 3 : Téléchargement

1. Dans l'onglet "Archives", cliquez sur "Télécharger"
2. Un fichier Word doit se télécharger
3. Ouvrez le fichier Word
4. Vérifiez que les données de l'enquête sont présentes

---

## Dépannage rapide

### Problème : La migration échoue

**Erreur :** `no such table: donnees`

**Solution :**
```bash
cd backend
python init_db.py
python migrations/add_archive_files_table.py
```

---

### Problème : Erreur 404 sur /api/archives/enquetes

**Cause :** Le blueprint n'est pas enregistré

**Solution :**
1. Vérifiez que `backend/app.py` contient :
   ```python
   from routes.archives import register_archives_routes
   register_archives_routes(app)
   ```
2. Redémarrez le backend

---

### Problème : L'onglet "Archives" n'apparaît pas

**Cause :** Le composant n'est pas importé

**Solution :**
1. Vérifiez que `frontend/src/components/tabs.jsx` contient :
   ```jsx
   const ArchivesViewer = lazy(() => import('./ArchivesViewer'));
   ```
2. Vérifiez que l'onglet est dans la liste `tabs`
3. Rafraîchissez le navigateur (Ctrl+F5)

---

### Problème : Erreur lors de l'archivage

**Erreur :** `python-docx n'est pas installé`

**Solution :**
```bash
cd backend
pip install python-docx
```

Redémarrez le backend.

---

### Problème : Le fichier n'est pas trouvé lors du téléchargement

**Erreur :** 404 lors du téléchargement

**Solution :**
1. Vérifiez que le dossier existe :
   ```bash
   ls backend/exports/archives/<ID_ENQUETE>/
   ```
2. Vérifiez les permissions :
   ```bash
   chmod -R 755 backend/exports/archives/
   ```
3. Vérifiez dans la base de données :
   ```sql
   SELECT * FROM enquete_archive_files WHERE enquete_id = <ID>;
   ```

---

## Vérification complète

### Checklist de vérification

- [ ] Migration exécutée sans erreur
- [ ] Dossier `backend/exports/archives/` existe
- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sans erreur
- [ ] Onglet "Archives" visible dans l'interface
- [ ] Route `/api/archives/enquetes` retourne une réponse JSON
- [ ] Test d'archivage réussi
- [ ] Fichier Word téléchargeable
- [ ] Enquête archivée disparaît de "Données"
- [ ] Enquête archivée apparaît dans "Archives"

---

## Commandes utiles

### Voir les archives en base de données

```sql
SELECT * FROM enquete_archive_files;
```

### Voir les enquêtes archivées

```sql
SELECT id, numeroDossier, nom, prenom, statut_validation 
FROM donnees 
WHERE statut_validation = 'archive';
```

### Supprimer une archive de test

```sql
-- Supprimer l'entrée en base
DELETE FROM enquete_archive_files WHERE enquete_id = <ID>;
DELETE FROM enquete_archives WHERE enquete_id = <ID>;

-- Remettre l'enquête en statut normal
UPDATE donnees SET statut_validation = 'en_attente' WHERE id = <ID>;
```

Puis supprimer le dossier :
```bash
rm -rf backend/exports/archives/<ID>/
```

---

## Support

### Documentation complète

Pour plus de détails, consultez :
- **DOCUMENTATION_ARCHIVAGE.md** : Documentation technique complète
- **RAPPORT_ARCHIVAGE_ENQUETES.md** : Rapport détaillé des modifications

### Logs

En cas de problème, consultez :
- **Backend :** Console où le serveur Flask est lancé
- **Frontend :** Console du navigateur (F12 → Console)
- **Base de données :** Utilisez DB Browser for SQLite

---

## Résumé

Le système d'archivage est maintenant installé et fonctionnel ! 🎉

**Fonctionnalités disponibles :**
- ✅ Archivage d'enquêtes avec génération de fichiers Word
- ✅ Stockage persistant des fichiers sur disque
- ✅ Consultation des archives en lecture seule
- ✅ Téléchargement des fichiers d'archives
- ✅ Filtrage automatique des enquêtes archivées

**Prochaines étapes :**
1. Tester avec des enquêtes réelles
2. Former les utilisateurs
3. Surveiller l'espace disque utilisé

---

**Version :** 1.0  
**Date :** 1er décembre 2024
