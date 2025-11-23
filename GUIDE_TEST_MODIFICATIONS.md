# 🧪 Guide de Test - Nouvelles Fonctionnalités

## 🚀 Démarrage Rapide

### 1. Lancer le Backend
```powershell
cd D:\EOS\backend
python app.py
```

**Vérification** : Le serveur doit démarrer sur http://localhost:5000

### 2. Lancer le Frontend
```powershell
cd D:\EOS\frontend
npm run dev
```

**Vérification** : L'application doit démarrer sur http://localhost:5173

---

## ✅ Tests à Effectuer

### Test 1 : Affichage de la Colonne "Enquêteur"

**Objectif** : Vérifier que la colonne "Enquêteur" s'affiche correctement dans l'onglet Données

**Étapes** :
1. Ouvrir http://localhost:5173
2. Aller dans l'onglet **"Données"**
3. Observer le tableau

**Résultat attendu** :
- ✅ Une nouvelle colonne "Enquêteur" apparaît entre "Éléments" et "Actions"
- ✅ Les enquêtes assignées affichent un badge avec le nom de l'enquêteur (ex: "Jean Dupont")
- ✅ Les enquêtes non assignées affichent "Non assigné" en gris italique

**Capture d'écran** : [À ajouter]

---

### Test 2 : Export des Enquêtes Visibles

**Objectif** : Exporter uniquement les enquêtes actuellement affichées après filtrage

**Étapes** :
1. Dans l'onglet **"Données"**
2. Appliquer un filtre (ex: Type = "Enquête", Statut = "Positif")
3. Observer le nombre d'enquêtes affichées
4. Cliquer sur le bouton **"Exporter (X)"** (où X = nombre d'enquêtes)
5. Attendre le téléchargement

**Résultat attendu** :
- ✅ Le bouton affiche le nombre correct d'enquêtes
- ✅ Un fichier `EOSExp_YYYYMMDD.txt` est téléchargé
- ✅ Le fichier contient uniquement les enquêtes filtrées
- ✅ Le format du fichier est conforme au cahier des charges EOS

**Test négatif** :
- Appliquer des filtres qui ne retournent aucun résultat
- Le bouton doit être désactivé (grisé)

---

### Test 3 : Export des Enquêtes d'un Enquêteur Spécifique

**Objectif** : Exporter toutes les enquêtes assignées à un enquêteur

**Étapes** :
1. Aller dans l'onglet **"Enquêteurs"**
2. Choisir un enquêteur qui a des enquêtes assignées
3. Cliquer sur **"Exporter ses enquêtes"** dans sa carte
4. Attendre le téléchargement

**Résultat attendu** :
- ✅ Un fichier `EOSExp_NomEnqueteur_YYYYMMDD.txt` est téléchargé
- ✅ Le fichier contient uniquement les enquêtes de cet enquêteur
- ✅ Un message de succès s'affiche : "Enquêtes de [Nom] exportées avec succès"
- ✅ Le bouton affiche un spinner pendant l'export

**Test négatif** :
- Tester avec un enquêteur qui n'a aucune enquête assignée
- Un message d'erreur doit s'afficher : "Aucune enquête trouvée pour l'enquêteur X"

---

### Test 4 : Export de Toutes les Enquêtes

**Objectif** : Exporter toutes les enquêtes de tous les enquêteurs

**Étapes** :
1. Dans l'onglet **"Enquêteurs"**
2. Cliquer sur le bouton **"Exporter tout"** en haut de la page
3. Attendre le téléchargement

**Résultat attendu** :
- ✅ Un fichier `EOSExp_Toutes_YYYYMMDD.txt` est téléchargé
- ✅ Le fichier contient toutes les enquêtes de la base de données
- ✅ Un message de succès s'affiche : "Toutes les enquêtes exportées avec succès"
- ✅ Le bouton affiche un spinner pendant l'export

---

### Test 5 : Vérification de l'API Backend

**Objectif** : Tester directement les endpoints de l'API

#### Test 5.1 : API `/api/donnees-complete`

```bash
# Tester avec curl ou Postman
curl http://localhost:5000/api/donnees-complete
```

**Résultat attendu** :
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "numeroDossier": "123456",
      "nom": "Dupont",
      "prenom": "Jean",
      "enqueteur_nom": "Martin",
      "enqueteur_prenom": "Pierre",
      ...
    }
  ]
}
```

#### Test 5.2 : API `/api/export-enquetes` (GET avec enqueteur_id)

```bash
# Exporter les enquêtes de l'enquêteur 1
curl -o export_enq1.txt http://localhost:5000/api/export-enquetes?enqueteur_id=1
```

**Résultat attendu** :
- ✅ Un fichier `export_enq1.txt` est créé
- ✅ Le fichier contient les enquêtes de l'enquêteur 1 au format EOS

#### Test 5.3 : API `/api/export-enquetes` (GET sans paramètre)

```bash
# Exporter toutes les enquêtes
curl -o export_all.txt http://localhost:5000/api/export-enquetes
```

**Résultat attendu** :
- ✅ Un fichier `export_all.txt` est créé
- ✅ Le fichier contient toutes les enquêtes au format EOS

#### Test 5.4 : API `/api/export-enquetes` (POST avec IDs spécifiques)

```bash
# Exporter des enquêtes spécifiques
curl -X POST http://localhost:5000/api/export-enquetes \
  -H "Content-Type: application/json" \
  -d '{"enquetes": [{"id": 1}, {"id": 2}, {"id": 3}]}' \
  -o export_specific.txt
```

**Résultat attendu** :
- ✅ Un fichier `export_specific.txt` est créé
- ✅ Le fichier contient uniquement les enquêtes 1, 2 et 3

---

## 🐛 Tests de Gestion d'Erreurs

### Erreur 1 : Aucune Enquête à Exporter

**Test** :
1. Dans l'onglet "Données", appliquer des filtres très restrictifs (aucun résultat)
2. Le bouton "Exporter" doit être désactivé

**Résultat attendu** : ✅ Bouton grisé et non cliquable

### Erreur 2 : Enquêteur Sans Enquête

**Test** :
1. Créer un nouvel enquêteur sans lui assigner d'enquêtes
2. Cliquer sur "Exporter ses enquêtes"

**Résultat attendu** : ✅ Message d'erreur "Aucune enquête trouvée pour l'enquêteur X"

### Erreur 3 : Problème Réseau

**Test** :
1. Arrêter le backend
2. Essayer d'exporter des enquêtes

**Résultat attendu** : ✅ Message d'erreur réseau affiché

---

## 📊 Vérification du Format d'Export

### Structure du Fichier

Ouvrir un fichier exporté et vérifier :

1. **Encodage** : UTF-8
2. **Longueur de ligne** : 1854 caractères par ligne
3. **Format** : Texte à longueur fixe
4. **Contenu** : Toutes les données d'enquête et d'enquêteur

### Exemple de Vérification

```python
# Script Python pour vérifier le format
with open('EOSExp_20251123.txt', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if len(line.rstrip('\n')) != 1854:
            print(f"Ligne {i}: Longueur incorrecte ({len(line.rstrip('\n'))} au lieu de 1854)")
        else:
            print(f"Ligne {i}: OK")
```

---

## 🎯 Checklist Complète

### Backend
- [ ] Le serveur démarre sans erreur
- [ ] `/api/donnees-complete` retourne `enqueteur_nom` et `enqueteur_prenom`
- [ ] `/api/export-enquetes?enqueteur_id=X` fonctionne
- [ ] `/api/export-enquetes` (sans paramètre) fonctionne
- [ ] `/api/export-enquetes` (POST) fonctionne toujours
- [ ] Les erreurs sont gérées correctement (404, 500)

### Frontend - DataViewer
- [ ] La colonne "Enquêteur" s'affiche
- [ ] Les noms d'enquêteurs sont corrects
- [ ] "Non assigné" s'affiche pour les enquêtes non assignées
- [ ] Le bouton "Exporter (X)" s'affiche
- [ ] Le nombre d'enquêtes est correct
- [ ] L'export fonctionne
- [ ] Le fichier téléchargé est correct
- [ ] Le spinner s'affiche pendant l'export

### Frontend - ImprovedEnqueteurViewer
- [ ] Le bouton "Exporter tout" s'affiche
- [ ] L'export global fonctionne
- [ ] Le bouton "Exporter ses enquêtes" s'affiche pour chaque enquêteur
- [ ] L'export par enquêteur fonctionne
- [ ] Les messages de succès s'affichent
- [ ] Les spinners s'affichent pendant les exports
- [ ] Les noms de fichiers sont corrects

### Gestion d'Erreurs
- [ ] Aucune enquête : bouton désactivé ou message d'erreur
- [ ] Problème réseau : message d'erreur affiché
- [ ] Enquêteur inexistant : message d'erreur approprié

---

## 📝 Rapport de Test

### Template de Rapport

```markdown
# Rapport de Test - [Date]

## Environnement
- OS : Windows 10
- Backend : Python 3.x, Flask
- Frontend : React + Vite
- Navigateur : Chrome/Firefox/Edge

## Tests Effectués

### Test 1 : Affichage Enquêteur
- [ ] Réussi
- [ ] Échoué
- Notes : 

### Test 2 : Export Visible
- [ ] Réussi
- [ ] Échoué
- Notes : 

### Test 3 : Export par Enquêteur
- [ ] Réussi
- [ ] Échoué
- Notes : 

### Test 4 : Export Global
- [ ] Réussi
- [ ] Échoué
- Notes : 

### Test 5 : API Backend
- [ ] Réussi
- [ ] Échoué
- Notes : 

## Bugs Trouvés
1. [Description du bug]
2. [Description du bug]

## Améliorations Suggérées
1. [Suggestion]
2. [Suggestion]

## Conclusion
- [ ] Toutes les fonctionnalités fonctionnent correctement
- [ ] Des corrections sont nécessaires
```

---

## 🆘 Dépannage

### Problème : Le backend ne démarre pas

**Solution** :
```powershell
cd D:\EOS\backend
pip install -r requirements.txt
python app.py
```

### Problème : Le frontend ne démarre pas

**Solution** :
```powershell
cd D:\EOS\frontend
npm install
npm run dev
```

### Problème : La colonne "Enquêteur" ne s'affiche pas

**Vérification** :
1. Vérifier que l'API `/api/donnees-complete` retourne bien `enqueteur_nom` et `enqueteur_prenom`
2. Vider le cache du navigateur (Ctrl+Shift+R)
3. Vérifier la console du navigateur pour les erreurs

### Problème : L'export ne fonctionne pas

**Vérification** :
1. Vérifier que le backend est bien lancé
2. Vérifier la console du navigateur pour les erreurs
3. Tester l'API directement avec curl
4. Vérifier les logs du backend

---

**Date** : 23 novembre 2025  
**Version** : 1.0  
**Auteur** : Assistant IA

