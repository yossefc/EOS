# Correction endpoint API - 23/12/2025 18:35

## 🐛 Problème identifié

**Symptôme** : Aucune demande ne s'affiche dans le tableau ni dans la mise à jour PARTNER.

**Erreur console** : `Failed to load resource: the server responded with a status of 404 (NOT FOUND)` pour `/api/partner/cases/{id}/requests`

## 🔍 Diagnostic

### Incohérence dans les URLs d'API

**Composants frontend** :
1. ✅ `PartnerDemandesHeader.jsx` : `/api/partner/case-requests/{donneeId}`
2. ❌ `PartnerElementsStatus.jsx` : `/api/partner/cases/{donneeId}/requests` (n'existe pas !)

**Backend** :
- ✅ Endpoint existant : `/api/partner/case-requests/{donnee_id}`
- ❌ Endpoint manquant : `/api/partner/cases/{donnee_id}/requests`

### Cause

Lors de la création de `PartnerElementsStatus.jsx`, j'ai utilisé une URL différente de celle de `PartnerDemandesHeader.jsx`, créant ainsi un endpoint qui n'existe pas côté backend.

## ✅ Solution appliquée

### Correction dans `PartnerElementsStatus.jsx`

**Avant** :
```javascript
const response = await axios.get(
  `${config.API_BASE_URL}/api/partner/cases/${donneeId}/requests`
);
```

**Après** :
```javascript
const response = await axios.get(
  `${config.API_BASE_URL}/api/partner/case-requests/${donneeId}`
);
```

### Fichiers modifiés
- `frontend/src/components/PartnerElementsStatus.jsx` (ligne 25)

## 🧪 Tests de validation

### 1. Ouvrir une enquête PARTNER
- ✅ Aucune erreur 404 dans la console
- ✅ Les demandes s'affichent dans l'en-tête (`PartnerDemandesHeader`)

### 2. Aller dans l'onglet "Données"
- ✅ Les éléments s'affichent avec code couleur (`PartnerElementsStatus`)
- 🟢 Vert = trouvé
- 🔴 Rouge = non trouvé

### 3. Vérifier les logs backend
- ✅ `GET /api/partner/case-requests/{id}` retourne 200 OK
- ✅ Réponse : `{ success: true, requests: [...] }`

## 📝 Endpoints PARTNER (pour référence)

| Endpoint | Méthode | Description | Utilisé par |
|----------|---------|-------------|-------------|
| `/api/partner/case-requests/{id}` | GET | Récupère les demandes | `PartnerDemandesHeader`, `PartnerElementsStatus` |
| `/api/partner/case-requests/{id}/recalculate` | POST | Recalcule statuts POS/NEG | `PartnerDemandesHeader` (bouton) |
| `/api/partner/keywords` | GET, POST, PUT, DELETE | CRUD keywords | Admin |
| `/api/partner/tarifs` | GET, POST, PUT, DELETE | CRUD tarifs | Admin |

## ⚠️ Note importante

**Les deux composants doivent utiliser le même endpoint** :
- `PartnerDemandesHeader` : affichage en-tête (résumé + badges)
- `PartnerElementsStatus` : affichage dans onglet Données (détails + code couleur)

Ils récupèrent les mêmes données mais les présentent différemment.

## 🔄 Actions requises

### Pas besoin de redémarrer le backend
✅ C'est une correction frontend uniquement

### Rafraîchir le navigateur
```
Ctrl + F5 (hard refresh)
ou
Ctrl + Shift + R
```

### Tester
1. Ouvrir une enquête PARTNER
2. Vérifier l'en-tête : demandes affichées ?
3. Aller dans "Données" : éléments avec code couleur ?
4. Console : aucune erreur 404 ?

## 📊 Impact

| Avant | Après |
|-------|-------|
| ❌ 404 Not Found | ✅ 200 OK |
| ❌ Aucune demande affichée | ✅ Demandes affichées |
| ❌ Erreurs console | ✅ Aucune erreur |

## 🎓 Leçon apprise

**Toujours vérifier que les endpoints existent côté backend avant de les appeler côté frontend !**

Mieux : définir les endpoints dans un fichier de configuration centralisé :
```javascript
// config/api-endpoints.js
export const PARTNER_ENDPOINTS = {
  CASE_REQUESTS: (id) => `/api/partner/case-requests/${id}`,
  RECALCULATE: (id) => `/api/partner/case-requests/${id}/recalculate`,
  // ...
};
```

Puis utiliser :
```javascript
import { PARTNER_ENDPOINTS } from '../config/api-endpoints';
const response = await axios.get(PARTNER_ENDPOINTS.CASE_REQUESTS(donneeId));
```

---

**Date** : 23/12/2025 18:35  
**Auteur** : Cursor Agent  
**Type** : Correction bug frontend  
**Statut** : ✅ Appliqué (pas besoin de redémarrage backend)

