# 🔧 Correctif - Statut `confirmee` pour l'Enquêteur

## 🐛 Problème Identifié

Lorsque l'enquêteur confirmait son enquête, le statut restait à `en_attente` au lieu de passer à `confirmee`. Cela empêchait l'administrateur de valider l'enquête car la route `/api/enquetes/<id>/valider` vérifie que le statut est `confirmee`.

### Erreur Observée
```
PUT /api/enquetes/7/valider HTTP/1.1" 400
Error: Cette enquête doit être confirmée par l'enquêteur avant validation (statut actuel: en_attente)
```

---

## 🔍 Cause Racine

Dans `frontend/src/components/UpdateModal.jsx`, ligne 752, le statut était mis à `en_attente` au lieu de `confirmee` :

```javascript
// ❌ AVANT (incorrect)
await axios.put(
  `${API_URL}/api/donnees/${data.id}/statut`,
  { statut_validation: 'en_attente' },  // ← Problème ici
  ...
);
```

---

## ✅ Solution Appliquée

### Fichier Modifié
**`frontend/src/components/UpdateModal.jsx`**

### Changements

#### 1. Correction du statut (ligne 753)
```javascript
// ✅ APRÈS (correct)
await axios.put(
  `${API_URL}/api/donnees/${data.id}/statut`,
  { statut_validation: 'confirmee' },  // ← Corrigé
  ...
);
```

#### 2. Mise à jour du commentaire (ligne 748-749)
```javascript
// ✅ AVANT
// Après avoir enregistré les données enquêteur, mettre le statut à "en_attente"

// ✅ APRÈS
// Après avoir enregistré les données enquêteur, mettre le statut à "confirmee"
// Cela indique que l'enquêteur a terminé et confirmé son travail
```

#### 3. Amélioration du message de succès (ligne 765)
```javascript
// ✅ AVANT
setSuccess("Données enregistrées avec succès - En attente de validation");

// ✅ APRÈS
setSuccess("Données enregistrées avec succès - Enquête confirmée et prête pour validation par l'administrateur");
```

---

## 🎯 Flux Correct Maintenant

### Étape 1 : Enquêteur remplit l'enquête
- **Action** : L'enquêteur ouvre le modal, remplit les données, clique sur "Enregistrer"
- **Statut** : `en_attente` → `confirmee` ✅
- **Message** : "Données enregistrées avec succès - Enquête confirmée et prête pour validation par l'administrateur"

### Étape 2 : Admin valide l'enquête
- **Action** : L'admin voit l'enquête dans "Données" avec le bouton "✓ Valider"
- **Vérification backend** : Statut = `confirmee` ✅
- **Statut** : `confirmee` → `validee` ✅
- **Message** : "Enquête validée avec succès. Elle apparaîtra dans l'onglet Export des résultats."

### Étape 3 : Export groupé
- **Action** : L'admin clique sur "Créer un nouvel export" dans "Export des résultats"
- **Statut** : `validee` → `archivee` ✅
- **Résultat** : Fichier Word généré et téléchargé

---

## 🧪 Test de Vérification

Pour vérifier que le correctif fonctionne :

1. **Ouvrir l'interface enquêteur**
   ```
   http://localhost:5173
   ```

2. **Sélectionner une enquête en attente**
   - Cliquer sur une ligne dans le tableau

3. **Remplir les données requises**
   - Code résultat : P, H, N, Z, I ou Y
   - Éléments retrouvés : AT, AD, etc.
   - Adresse complète
   - Au moins un champ d'adresse rempli

4. **Cliquer sur "Enregistrer"**
   - ✅ Message : "Données enregistrées avec succès - Enquête confirmée et prête pour validation par l'administrateur"
   - ✅ Le modal se ferme

5. **Vérifier le statut en base de données**
   ```bash
   cd backend
   python -c "
   from app import create_app
   from extensions import db
   from models.models import Donnee
   
   app = create_app()
   with app.app_context():
       enquete = Donnee.query.get(7)  # Remplacer 7 par l'ID de votre enquête
       print(f'Statut de l\'enquête {enquete.id}: {enquete.statut_validation}')
   "
   ```
   - ✅ Résultat attendu : `Statut de l'enquête 7: confirmee`

6. **Aller dans l'onglet "Données" (Admin)**
   - ✅ L'enquête apparaît avec le bouton "✓ Valider" visible

7. **Cliquer sur "✓ Valider"**
   - ✅ Confirmation : "Êtes-vous sûr de vouloir valider cette enquête ?"
   - ✅ Message de succès : "Enquête validée avec succès !"
   - ✅ L'enquête disparaît de "Données"
   - ✅ L'enquête apparaît dans "Export des résultats"

---

## 📊 Récapitulatif des Statuts

| Étape | Action | Statut Avant | Statut Après | Onglet Visible |
|-------|--------|--------------|--------------|----------------|
| 1. Import | Import fichier CSV | - | `en_attente` | Données |
| 2. Enquêteur | Remplit et confirme | `en_attente` | `confirmee` ✅ | Données (avec bouton Valider) |
| 3. Admin | Valide l'enquête | `confirmee` | `validee` | Export des résultats |
| 4. Admin | Crée export groupé | `validee` | `archivee` | Archives |

---

## ⚠️ Points d'Attention

### 1. Enquêtes Existantes
Les enquêtes qui ont été remplies **avant** ce correctif ont toujours le statut `en_attente`. Pour les corriger :

#### Option A : Re-confirmer manuellement
1. Ouvrir chaque enquête dans l'interface enquêteur
2. Cliquer sur "Enregistrer" (même sans modifier les données)
3. Le statut passera automatiquement à `confirmee`

#### Option B : Mise à jour en masse via SQL
```bash
cd backend
python -c "
from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur

app = create_app()
with app.app_context():
    # Trouver toutes les enquêtes avec données enquêteur mais statut en_attente
    enquetes = db.session.query(Donnee).join(
        DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
    ).filter(
        Donnee.statut_validation == 'en_attente',
        DonneeEnqueteur.code_resultat.isnot(None)
    ).all()
    
    print(f'Trouvé {len(enquetes)} enquête(s) à corriger')
    
    for enquete in enquetes:
        enquete.statut_validation = 'confirmee'
        print(f'  - Enquête {enquete.id}: en_attente → confirmee')
    
    db.session.commit()
    print('✅ Mise à jour terminée')
"
```

### 2. Validation du Statut
La route `/api/donnees/<id>/statut` accepte uniquement ces valeurs :
- `en_attente`
- `confirmee`
- `refusee`

Elle **ne permet pas** de mettre directement à `validee` ou `archivee` (ces statuts sont gérés par d'autres routes).

---

## 🚀 Déploiement

### 1. Redémarrer le Frontend
```bash
# Si le frontend tourne en dev
# Les modifications sont automatiquement rechargées (Hot Module Replacement)
# Sinon, redémarrer :
cd frontend
npm run dev
```

### 2. Pas besoin de redémarrer le Backend
Le backend n'a pas été modifié, donc pas besoin de redémarrage.

### 3. Vider le Cache du Navigateur (optionnel)
Si les changements ne sont pas visibles :
- Appuyer sur `Ctrl + Shift + R` (Windows/Linux)
- Ou `Cmd + Shift + R` (Mac)

---

## 📝 Notes Techniques

### Route Backend Concernée
**`backend/routes/validation.py`** - Ligne 128-167

```python
@validation_bp.route('/api/donnees/<int:donnee_id>/statut', methods=['PUT'])
def update_statut_validation(donnee_id):
    """Met à jour le statut de validation d'une enquête"""
    # Accepte: 'en_attente', 'confirmee', 'refusee'
    # Cette route est appelée par l'enquêteur après confirmation
```

### Validation Stricte dans `validation_v2.py`
**`backend/routes/validation_v2.py`** - Ligne 42-46

```python
# Vérifier que l'enquête est confirmée par l'enquêteur
if donnee.statut_validation != 'confirmee':
    return jsonify({
        'success': False,
        'error': f'Cette enquête doit être confirmée par l\'enquêteur avant validation (statut actuel: {donnee.statut_validation})'
    }), 400
```

Cette vérification **garantit** que seules les enquêtes confirmées par l'enquêteur peuvent être validées par l'admin.

---

## ✅ Résultat Final

Après ce correctif :

✅ **Enquêteur confirme** → Statut passe à `confirmee`  
✅ **Admin peut valider** → Statut passe à `validee`  
✅ **Export groupé** → Statut passe à `archivee`  
✅ **Flux complet fonctionnel** de bout en bout  

---

**Date du correctif** : 2025-12-01  
**Fichier modifié** : `frontend/src/components/UpdateModal.jsx`  
**Lignes modifiées** : 748-749, 753, 765
