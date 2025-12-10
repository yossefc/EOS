# 🧪 Guide de Test - Flux Validation → Export → Archive

## ⚠️ Avant de commencer

**IMPORTANT** : Le serveur Flask doit être relancé pour prendre en compte les modifications.

```bash
# Dans le terminal où le serveur tourne
# Appuyez sur Ctrl+C pour arrêter

# Puis relancez
cd backend
python app.py
```

---

## 📋 Prérequis

Avant de tester, assurez-vous d'avoir :

1. ✅ Une enquête avec le statut `confirmee` (enquêteur a terminé son travail)
2. ✅ Le serveur Flask qui tourne sur `http://localhost:5000`
3. ✅ Le frontend React qui tourne sur `http://localhost:5173`
4. ✅ `python-docx` installé : `pip install python-docx`

---

## 🎯 Test 1 : Validation d'une Enquête

### Objectif
Valider une enquête depuis l'onglet "Données" et vérifier qu'elle apparaît dans "Export des résultats"

### Étapes

1. **Ouvrir l'application** : `http://localhost:5173`

2. **Aller dans l'onglet "Données"**
   - Vous devriez voir la liste des enquêtes

3. **Trouver une enquête avec statut `confirmee`**
   - Cherchez une ligne avec un bouton "✓ Valider" visible
   - Si aucune enquête n'a ce statut, créez-en une :
     a. Aller dans "Interface Enquêteur"
     b. Remplir une enquête
     c. Confirmer l'enquête → statut passe à `confirmee`

4. **Cliquer sur "✓ Valider"**
   - Une confirmation apparaît : "Êtes-vous sûr de vouloir valider cette enquête ?"
   - Cliquer sur "OK"

5. **Vérifications** :
   - ✅ Message de succès : "Enquête validée avec succès !"
   - ✅ L'enquête disparaît du tableau "Données"
   - ✅ Dans les logs backend : `Enquête X validée par Administrateur`

6. **Aller dans l'onglet "Export des résultats"**
   - ✅ L'enquête validée apparaît dans le tableau
   - ✅ Le bouton affiche : "Créer un nouvel export (1)"

### Résultat Attendu
- ✅ Statut de l'enquête : `confirmee` → `validee`
- ✅ Enquête visible dans "Export des résultats"
- ✅ Enquête invisible dans "Données"

---

## 🎯 Test 2 : Création d'un Export Groupé

### Objectif
Créer un export Word avec toutes les enquêtes validées et vérifier l'archivage

### Étapes

1. **Valider plusieurs enquêtes** (si possible 3-5)
   - Répéter le Test 1 pour avoir plusieurs enquêtes validées

2. **Aller dans "Export des résultats"**
   - Vous devriez voir N enquêtes dans le tableau
   - Le bouton affiche : "Créer un nouvel export (N)"

3. **Cliquer sur "Créer un nouvel export (N)"**
   - Une confirmation apparaît : "Vous allez créer un export de N enquête(s) validée(s). Ces enquêtes seront archivées. Continuer ?"
   - Cliquer sur "OK"

4. **Attendre la génération**
   - Le bouton affiche : "Création en cours..."
   - Cela peut prendre quelques secondes

5. **Vérifications** :
   - ✅ Un fichier Word est téléchargé automatiquement
   - ✅ Nom du fichier : `Export_Batch_YYYYMMDD_HHMMSS_N_enquetes.docx`
   - ✅ Message de succès : "Export créé avec succès ! N enquête(s) ont été archivées."
   - ✅ Le tableau "Export des résultats" est maintenant vide
   - ✅ Dans les logs backend : `Export batch créé avec succès: ... (N enquêtes)`

6. **Ouvrir le fichier Word téléchargé**
   - ✅ Le fichier s'ouvre correctement
   - ✅ Chaque enquête est sur une page séparée
   - ✅ Design professionnel avec titre, tableau de données, notes
   - ✅ Toutes les N enquêtes sont présentes

### Résultat Attendu
- ✅ Statut des enquêtes : `validee` → `archivee`
- ✅ Fichier Word généré et téléchargé
- ✅ Fichier sauvegardé dans `backend/exports/batches/`
- ✅ Entrée créée dans la table `export_batches`
- ✅ Tableau "Export des résultats" vide

---

## 🎯 Test 3 : Consultation des Archives

### Objectif
Vérifier que l'export créé apparaît dans "Archives" et peut être re-téléchargé

### Étapes

1. **Aller dans l'onglet "Archives"**
   - Vous devriez voir la liste des exports créés

2. **Vérifier les informations affichées** :
   - ✅ Nom du fichier : `Export_Batch_YYYYMMDD_HHMMSS_N_enquetes.docx`
   - ✅ Nb Enquêtes : N enquêtes (badge violet)
   - ✅ Taille : XX.X KB ou MB
   - ✅ Date création : Date et heure complètes
   - ✅ Utilisateur : Administrateur

3. **Cliquer sur "Télécharger"**
   - Le bouton affiche : "Téléchargement..."
   - Le fichier Word est re-téléchargé

4. **Ouvrir le fichier re-téléchargé**
   - ✅ Le fichier s'ouvre correctement
   - ✅ Le contenu est identique au fichier téléchargé lors de la création

5. **Tester la recherche**
   - Taper le nom du fichier dans la barre de recherche
   - ✅ Le fichier est filtré correctement

6. **Tester la pagination** (si plus de 20 exports)
   - Cliquer sur les boutons "Précédent" / "Suivant"
   - ✅ La pagination fonctionne

### Résultat Attendu
- ✅ Export visible dans "Archives"
- ✅ Toutes les informations correctes
- ✅ Re-téléchargement fonctionnel
- ✅ Fichier identique à l'original

---

## 🎯 Test 4 : Flux Complet de Bout en Bout

### Objectif
Tester le cycle de vie complet d'une enquête

### Étapes

1. **Créer une nouvelle enquête**
   - Onglet "Import de fichiers" ou création manuelle
   - ✅ Statut : `en_attente`

2. **Assigner à un enquêteur**
   - Onglet "Assignations"
   - Assigner l'enquête à un enquêteur
   - ✅ Statut : toujours `en_attente`

3. **Remplir l'enquête (Interface Enquêteur)**
   - Se connecter en tant qu'enquêteur
   - Remplir toutes les données requises
   - Confirmer l'enquête
   - ✅ Statut : `en_attente` → `confirmee`

4. **Valider l'enquête (Admin)**
   - Onglet "Données"
   - Cliquer sur "✓ Valider"
   - ✅ Statut : `confirmee` → `validee`
   - ✅ Enquête apparaît dans "Export des résultats"

5. **Créer un export**
   - Onglet "Export des résultats"
   - Cliquer sur "Créer un nouvel export"
   - ✅ Statut : `validee` → `archivee`
   - ✅ Fichier Word téléchargé

6. **Consulter les archives**
   - Onglet "Archives"
   - ✅ Export visible avec toutes les infos
   - ✅ Re-téléchargement possible

### Résultat Attendu
- ✅ Flux complet : `en_attente` → `confirmee` → `validee` → `archivee`
- ✅ Enquête visible dans les bons onglets à chaque étape
- ✅ Fichier Word généré et accessible

---

## 🔍 Vérifications en Base de Données

### Vérifier les statuts

```bash
cd backend
python -c "
from app import create_app
from extensions import db
from models.models import Donnee

app = create_app()
with app.app_context():
    statuts = db.session.query(
        Donnee.statut_validation, 
        db.func.count(Donnee.id)
    ).group_by(Donnee.statut_validation).all()
    
    print('Répartition des statuts:')
    for statut, count in statuts:
        print(f'  - {statut}: {count} enquête(s)')
"
```

### Vérifier les exports batch

```bash
cd backend
python -c "
from app import create_app
from extensions import db
from models.export_batch import ExportBatch

app = create_app()
with app.app_context():
    batches = ExportBatch.query.all()
    print(f'Nombre d\'exports batch: {len(batches)}')
    for batch in batches:
        print(f'  - {batch.filename}: {batch.enquete_count} enquêtes')
"
```

### Vérifier les fichiers sur disque

```bash
cd backend/exports/batches
dir
# Ou sur Linux/Mac: ls -lh
```

---

## 🐛 Problèmes Courants et Solutions

### Problème 1 : "Aucune enquête validée à exporter"
**Cause** : Aucune enquête avec statut `validee` en base

**Solution** :
1. Vérifier les statuts en base (voir commande ci-dessus)
2. Valider au moins une enquête depuis "Données"
3. Vérifier que le statut passe bien à `validee` (pas `archivee`)

### Problème 2 : "python-docx n'est pas installé"
**Cause** : Module manquant

**Solution** :
```bash
cd backend
pip install python-docx
```

### Problème 3 : Erreur 500 lors de la création d'export
**Cause** : Permissions d'écriture ou erreur dans la génération du Word

**Solution** :
1. Vérifier les logs backend
2. Vérifier que le dossier `backend/exports/batches/` existe et est accessible en écriture
3. Vérifier que toutes les enquêtes validées ont des données complètes

### Problème 4 : Fichier non trouvé lors du re-téléchargement
**Cause** : Fichier supprimé du disque ou chemin incorrect

**Solution** :
1. Vérifier que le fichier existe dans `backend/exports/batches/`
2. Vérifier le chemin dans la table `export_batches`
3. Re-créer un export si nécessaire

### Problème 5 : Enquête ne disparaît pas de "Données" après validation
**Cause** : Filtre côté frontend ou statut non mis à jour

**Solution** :
1. Actualiser la page (F5)
2. Vérifier le statut en base de données
3. Vérifier les logs backend pour voir si la validation a réussi

---

## 📊 Métriques de Succès

À la fin des tests, vous devriez avoir :

- ✅ Au moins 1 enquête avec statut `validee`
- ✅ Au moins 1 export batch créé
- ✅ Au moins 1 fichier Word dans `backend/exports/batches/`
- ✅ Au moins 1 enquête avec statut `archivee`
- ✅ Aucune erreur dans les logs backend
- ✅ Aucune erreur dans la console navigateur

---

## 📞 Aide

Si vous rencontrez un problème :

1. **Consulter les logs backend** : Terminal où `python app.py` tourne
2. **Consulter la console navigateur** : F12 → Console
3. **Vérifier la base de données** : Utiliser les commandes ci-dessus
4. **Consulter la documentation** : `FLUX_VALIDATION_EXPORT_ARCHIVE.md`

---

**Bonne chance avec les tests ! 🚀**

