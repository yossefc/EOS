# Refonte du Flux de Validation des Enquêtes

**Date :** 1er décembre 2025  
**Objectif :** Intégrer la validation des enquêtes directement dans l'onglet Données

---

## 📋 Résumé des Changements

### Ancien Système
- Onglet "Validation Enquêtes" séparé (AdminDashboard)
- Statut `confirmee` pour les enquêtes validées
- Validation en deux étapes (validation puis export)

### Nouveau Système
- **Validation intégrée dans l'onglet "Données"**
- Boutons "Valider" et "Refuser" directement sur chaque ligne
- Statut `archive` pour les enquêtes validées
- Les enquêtes validées disparaissent du tableau Données
- Elles apparaissent immédiatement dans "Export des résultats"

---

## 🔧 Modifications Backend

### 1. Nouvelles Routes API (`backend/routes/validation_v2.py`)

#### `PUT /api/enquetes/<id>/valider`
- Valide une enquête et la marque comme archivée
- Vérifie qu'il y a une réponse d'enquêteur (code_resultat)
- Change le statut à `archive`
- Crée une entrée dans `EnqueteArchive`
- Ajoute un événement à l'historique

#### `PUT /api/enquetes/<id>/refuser`
- Refuse une enquête
- Remet le statut à `en_attente`
- Supprime l'archive si elle existe
- Ajoute un événement à l'historique avec le motif

### 2. Route Modifiée (`backend/app.py`)

#### `GET /api/donnees-complete`
- **Filtre les enquêtes archivées** (elles n'apparaissent plus dans Données)
- Ajoute les champs :
  - `has_response` : indique si l'enquête a une réponse
  - `can_validate` : indique si les boutons de validation doivent être affichés

### 3. Routes Export Modifiées (`backend/routes/export.py`)

#### `GET /api/enquetes/validees`
- Filtre maintenant sur `statut_validation == 'archive'` au lieu de `'confirmee'`
- Inclut les informations d'archive (date de validation, déjà exporté)

#### `POST /api/export/enquete/<id>`
- Vérifie que le statut est `'archive'` au lieu de `'confirmee'`

---

## 🎨 Modifications Frontend

### 1. DataViewer.jsx

#### Nouveaux imports
```javascript
import { CheckCircle, XCircle } from 'lucide-react';
```

#### Nouveaux états
```javascript
const [validating, setValidating] = useState(false);
const [successMessage, setSuccessMessage] = useState(null);
```

#### Nouvelles fonctions
- `handleValiderEnquete(enqueteId)` : Valide une enquête
- `handleRefuserEnquete(enqueteId)` : Refuse une enquête

#### Nouveaux boutons dans la colonne Actions
```javascript
{donnee.can_validate && (
  <>
    <button onClick={() => handleValiderEnquete(donnee.id)}>
      <CheckCircle className="w-4 h-4" />
    </button>
    <button onClick={() => handleRefuserEnquete(donnee.id)}>
      <XCircle className="w-4 h-4" />
    </button>
  </>
)}
```

### 2. tabs.jsx

#### Suppression de l'onglet Validation
- Commenté l'import de `AdminDashboard`
- Retiré l'onglet "Validation Enquêtes" de la liste

---

## 📊 Flux de Validation

### Scénario 1 : Validation d'une Enquête

1. **L'enquêteur** remplit une enquête (code_resultat, éléments retrouvés, etc.)
2. **L'administrateur** voit les boutons "Valider" et "Refuser" dans l'onglet Données
3. **Clic sur "Valider"** :
   - Confirmation demandée
   - API `PUT /api/enquetes/{id}/valider` appelée
   - Statut passe à `archive`
   - Entrée créée dans `EnqueteArchive`
   - L'enquête **disparaît** du tableau Données
   - Message de succès affiché
4. **L'enquête apparaît** dans l'onglet "Export des résultats"

### Scénario 2 : Refus d'une Enquête

1. **Clic sur "Refuser"** :
   - Demande du motif (optionnel)
   - API `PUT /api/enquetes/{id}/refuser` appelée
   - Statut revient à `en_attente`
   - Archive supprimée si elle existait
   - Les boutons disparaissent
   - La ligne reste visible dans le tableau
2. **L'enquête reste** dans l'onglet Données avec statut `en_attente`

---

## 🗄️ Schéma de Base de Données

### Table `donnees`
- `statut_validation` : `'en_attente'` | `'archive'` | `'refusee'`
  - `'en_attente'` : Enquête en cours ou refusée
  - `'archive'` : Enquête validée, prête pour l'export
  - `'refusee'` : (ancien statut, peut être nettoyé)

### Table `enquete_archives`
- Créée automatiquement lors de la validation
- Contient :
  - `enquete_id` : ID de l'enquête
  - `date_export` : Date de validation/archivage
  - `utilisateur` : Qui a validé
  - `nom_fichier` : Rempli lors de l'export réel

---

## 🧪 Tests Recommandés

### Test 1 : Validation Basique
1. Créer une enquête avec une réponse d'enquêteur
2. Vérifier que les boutons "Valider" et "Refuser" apparaissent
3. Cliquer sur "Valider"
4. Vérifier que l'enquête disparaît de l'onglet Données
5. Vérifier qu'elle apparaît dans "Export des résultats"

### Test 2 : Refus d'Enquête
1. Créer une enquête avec une réponse
2. Cliquer sur "Refuser"
3. Entrer un motif
4. Vérifier que les boutons disparaissent
5. Vérifier que la ligne reste visible
6. Vérifier le statut dans l'historique

### Test 3 : Enquête Sans Réponse
1. Créer une enquête sans réponse d'enquêteur
2. Vérifier que les boutons de validation n'apparaissent PAS

### Test 4 : Export
1. Valider plusieurs enquêtes
2. Aller dans "Export des résultats"
3. Vérifier que toutes les enquêtes validées sont listées
4. Exporter un document Word
5. Vérifier que le statut "déjà exporté" est mis à jour

---

## 🔄 Migration des Données Existantes

Si des enquêtes ont le statut `'confirmee'` dans la base actuelle :

```sql
-- Mettre à jour les enquêtes confirmées vers le nouveau statut
UPDATE donnees 
SET statut_validation = 'archive' 
WHERE statut_validation = 'confirmee';

-- Créer des entrées d'archive pour les enquêtes déjà confirmées
INSERT INTO enquete_archives (enquete_id, date_export, utilisateur)
SELECT id, updated_at, 'Migration Automatique'
FROM donnees
WHERE statut_validation = 'archive'
AND id NOT IN (SELECT enquete_id FROM enquete_archives);
```

---

## 📝 Notes Importantes

1. **Ancien composant AdminDashboard** : Peut être supprimé après validation complète du nouveau système

2. **Routes legacy** : Les anciennes routes de validation (`/api/enquetes/a-valider`, `/api/enquete/valider/<id>`) sont conservées pour compatibilité mais ne sont plus utilisées

3. **Statut `refusee`** : Ce statut n'est plus utilisé. Les enquêtes refusées reviennent à `en_attente`

4. **Performance** : Le filtrage sur `statut_validation != 'archive'` dans `/api/donnees-complete` améliore les performances en réduisant le nombre de lignes affichées

---

## ✅ Checklist de Déploiement

- [x] Créer les nouvelles routes API
- [x] Modifier la route de listing des données
- [x] Mettre à jour DataViewer.jsx
- [x] Supprimer l'onglet Validation
- [x] Adapter les routes d'export
- [ ] Tester en environnement de développement
- [ ] Migrer les données existantes (si nécessaire)
- [ ] Déployer en production
- [ ] Supprimer AdminDashboard.jsx (après validation)
- [ ] Supprimer les routes legacy (après validation)
- [ ] Mettre à jour la documentation utilisateur

---

## 🎯 Avantages du Nouveau Système

1. **Simplicité** : Tout se passe dans un seul onglet
2. **Rapidité** : Validation en un clic depuis le tableau
3. **Visibilité** : Statut clair de chaque enquête
4. **Traçabilité** : Historique complet des validations/refus
5. **UX améliorée** : Moins de navigation entre les onglets

---

**Refonte terminée avec succès ! 🎉**



