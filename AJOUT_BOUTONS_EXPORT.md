# Ajout des Boutons d'Export dans les Onglets Données et Assignation

## 📋 Résumé des Modifications

J'ai ajouté des boutons d'export dans deux onglets de l'application pour permettre l'export facile des enquêtes visibles.

## 🎯 Fonctionnalités Ajoutées

### 1. Onglet **Données** (DataViewer.jsx)
- ✅ Bouton "Exporter (X)" ajouté en haut à gauche
- ✅ Affiche le nombre d'enquêtes visibles après filtrage
- ✅ Désactivé si aucune enquête n'est visible
- ✅ Animation de chargement pendant l'export

### 2. Onglet **Assignation** (AssignmentViewer.jsx)
- ✅ Bouton "Exporter (X)" ajouté dans la barre d'actions
- ✅ Affiche le nombre d'enquêtes visibles après recherche
- ✅ Désactivé si aucune enquête n'est visible
- ✅ Animation de chargement pendant l'export
- ✅ Messages de succès/erreur affichés temporairement

## 📁 Fichiers Modifiés

### Frontend

#### 1. `frontend/src/components/DataViewer.jsx`
**Modifications :**
- Ajout de la fonction `handleExportVisible()` pour gérer l'export
- Ajout du bouton d'export avec icône `Download`
- Gestion de l'état `exportingData` pour le feedback visuel

**Code ajouté :**
```javascript
// Fonction pour exporter les enquêtes visibles
const handleExportVisible = async () => {
  try {
    setExportingData(true);
    const enquetesToExport = filteredDonnees.map(donnee => ({ id: donnee.id }));
    
    if (enquetesToExport.length === 0) {
      alert("Aucune enquête à exporter");
      return;
    }
    
    const response = await axios.post(`${API_URL}/api/export-enquetes`, {
      enquetes: enquetesToExport
    }, {
      responseType: 'blob'
    });
    
    // Téléchargement du fichier
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `EOSExp_${new Date().toISOString().split('T')[0]}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error("Erreur lors de l'export:", error);
    alert(error.response?.data?.error || "Erreur lors de l'export des enquêtes");
  } finally {
    setExportingData(false);
  }
};
```

#### 2. `frontend/src/components/AssignmentViewer.jsx`
**Modifications :**
- Import de l'icône `Download` depuis `lucide-react`
- Ajout de l'état `exportingData`
- Ajout de la fonction `handleExportVisible()` avec gestion des messages
- Ajout du bouton d'export dans la barre d'actions

**Code ajouté :**
```javascript
// État pour l'export
const [exportingData, setExportingData] = useState(false);

// Fonction pour exporter les enquêtes visibles
const handleExportVisible = useCallback(async () => {
  try {
    setExportingData(true);
    const enquetesToExport = filteredEnquetes.map(enquete => ({ id: enquete.id }));
    
    if (enquetesToExport.length === 0) {
      setError("Aucune enquête à exporter");
      setTimeout(() => setError(null), 3000);
      return;
    }
    
    const response = await api.post('/api/export-enquetes', {
      enquetes: enquetesToExport
    }, {
      responseType: 'blob'
    });
    
    // Téléchargement du fichier
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `EOSExp_${new Date().toISOString().split('T')[0]}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    setSuccessMessage(`${enquetesToExport.length} enquête(s) exportée(s) avec succès`);
    setTimeout(() => setSuccessMessage(''), 3000);
    
  } catch (error) {
    console.error("Erreur lors de l'export:", error);
    setError(error.response?.data?.error || "Erreur lors de l'export des enquêtes");
    setTimeout(() => setError(null), 3000);
  } finally {
    setExportingData(false);
  }
}, [filteredEnquetes]);
```

### Backend

#### 3. `backend/routes/export.py`
**Modifications :**
- Remplacement complet du code d'export Word par un export texte au format EOS
- Suppression des dépendances `python-docx` et `docx.*`
- Ajout de la fonction `generate_eos_text_file()` pour générer le contenu texte
- Ajout de la fonction `format_export_line()` pour formater chaque ligne au format à longueur fixe

**Format du fichier généré :**
- Fichier texte (`.txt`) avec encodage UTF-8
- Format à longueur fixe selon spécifications EOS France
- Une ligne par enquête
- Champs remplis avec des espaces pour respecter les longueurs fixes

**Champs exportés (par ligne) :**
1. Informations de base : N° dossier, référence, type demande
2. État civil : nom, prénom, date/lieu de naissance
3. Adresse d'origine : adresse, code postal, ville, téléphone
4. Résultats enquête : code résultat, éléments retrouvés
5. Adresse trouvée : adresse complète (3 lignes), code postal, ville, pays
6. Contact : téléphones personnel et professionnel
7. Employeur : nom, téléphone, adresse, ville
8. Banque : nom, guichet, titulaire, codes
9. Décès : date, n° acte, localité
10. Notes personnelles

## 🎨 Interface Utilisateur

### Bouton d'Export
- **Couleur** : Vert (`bg-green-500` / `bg-green-600`)
- **Icône** : Download (lucide-react)
- **Position** : 
  - DataViewer : En haut à gauche, avant les boutons "Filtres" et "Actualiser"
  - AssignmentViewer : Dans la barre d'actions, avant "Actualiser" et "Assignation en masse"
- **États** :
  - Normal : Vert avec icône Download
  - Chargement : Animation de rotation avec icône RefreshCw
  - Désactivé : Opacité réduite, curseur not-allowed

### Messages
- **Succès** (AssignmentViewer) : Bannière verte avec icône Check
- **Erreur** : Bannière rouge avec icône AlertCircle (DataViewer : alert, AssignmentViewer : bannière)
- **Durée** : 3 secondes (auto-disparition)

## 🔄 Flux d'Export

1. **Utilisateur clique sur "Exporter (X)"**
2. **Frontend** :
   - Récupère les IDs des enquêtes visibles (après filtrage/recherche)
   - Envoie une requête POST à `/api/export-enquetes`
   - Reçoit un fichier blob en réponse
3. **Backend** :
   - Récupère les données complètes des enquêtes depuis la base
   - Génère le fichier texte au format EOS (longueur fixe)
   - Retourne le fichier avec `Content-Type: text/plain`
4. **Frontend** :
   - Crée un lien de téléchargement temporaire
   - Déclenche le téléchargement automatique
   - Nettoie le lien et l'URL blob
   - Affiche un message de succès

## 📝 Format du Fichier Exporté

**Nom du fichier** : `EOSExp_YYYYMMDD_HHMMSS.txt`

**Exemple** : `EOSExp_20241123_143022.txt`

**Structure** :
```
[N°Dossier(20)][Référence(20)][Type(3)][Nom(30)][Prénom(30)][DateNaiss(8)]...
```

Chaque champ a une longueur fixe :
- Les valeurs sont tronquées si trop longues
- Les valeurs sont complétées avec des espaces si trop courtes
- Les dates sont au format DDMMYYYY
- Les champs vides sont remplis d'espaces

## ✅ Tests Recommandés

### Test 1 : Export depuis l'onglet Données
1. Ouvrir l'onglet "Données"
2. Appliquer des filtres (optionnel)
3. Cliquer sur "Exporter (X)"
4. Vérifier que le fichier `.txt` se télécharge
5. Ouvrir le fichier et vérifier le contenu

### Test 2 : Export depuis l'onglet Assignation
1. Ouvrir l'onglet "Assignation"
2. Utiliser la barre de recherche (optionnel)
3. Cliquer sur "Exporter (X)"
4. Vérifier le message de succès
5. Vérifier que le fichier `.txt` se télécharge
6. Ouvrir le fichier et vérifier le contenu

### Test 3 : Cas limites
- ✅ Exporter sans enquêtes visibles → Message d'erreur
- ✅ Exporter 1 seule enquête → Fichier avec 1 ligne
- ✅ Exporter toutes les enquêtes → Fichier complet
- ✅ Exporter avec des champs vides → Espaces dans le fichier

## 🚀 Déploiement

### Prérequis
- Aucune nouvelle dépendance Python requise
- Aucune nouvelle dépendance npm requise

### Étapes
1. Les modifications frontend sont déjà en place
2. Les modifications backend sont déjà en place
3. Redémarrer le serveur backend si nécessaire
4. Rafraîchir le frontend

### Commandes
```bash
# Backend (si nécessaire)
cd D:/EOS/backend
python app.py

# Frontend (si nécessaire)
cd D:/EOS/frontend
npm run dev
```

## 📞 Support

En cas de problème :
1. Vérifier les logs du backend (`app.log`)
2. Vérifier la console du navigateur (F12)
3. Vérifier que la route `/api/export-enquetes` est bien enregistrée
4. Vérifier les permissions de téléchargement du navigateur

---

**Date de modification** : 23 novembre 2024
**Version** : 1.0

