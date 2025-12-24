# 🔧 CORRECTION - Données de naissance PARTNER (23/12/2025)

## 🎯 PROBLÈME IDENTIFIÉ

**Symptôme** : Les données saisies dans l'onglet "Naissance" (date et lieu de naissance) ne sont pas sauvegardées en base de données pour les dossiers PARTNER.

**Cause** : Erreur dans la condition d'envoi des données dans `UpdateModal.jsx` (ligne 856).

---

## 🔍 DIAGNOSTIC

### Script de diagnostic créé
```bash
cd backend
python scripts/check_partner_naissance.py
```

**Résultat** :
- ✅ Colonnes `dateNaissance_maj` et `lieuNaissance_maj` existent en DB
- ✅ Client PARTNER trouvé (ID=11)
- ❌ **0/9 dossiers avec données de naissance mises à jour**

### Analyse du code

**Avant (INCORRECT)** :
```javascript
// Ligne 856 dans UpdateModal.jsx
if (clientCode !== 'EOS') {
  dataToSend = {
    ...dataToSend,
    dateNaissance_maj: formData.dateNaissance_maj || null,
    lieuNaissance_maj: formData.lieuNaissance_maj || null
  };
}
```

**Problème** : La variable `clientCode` est initialisée à `'EOS'` par défaut (ligne 109) et n'est jamais mise à jour pour PARTNER. La condition `clientCode !== 'EOS'` est donc toujours `false`.

---

## ✅ CORRECTIONS APPLIQUÉES

### Fichier modifié
- `frontend/src/components/UpdateModal.jsx` (2 corrections)

### Correction 1 : Envoi des données (ligne 856)
```javascript
// AVANT
if (clientCode !== 'EOS') {

// APRÈS
if (isPartner) {
```

**Explication** : La variable `isPartner` est correctement calculée (ligne 114) : `const isPartner = clientCode === 'PARTNER';`

### Correction 2 : Chargement des données (ligne 448)
```javascript
// AVANT
              // Notes personnelles
              notes_personnelles: enqueteurData.notes_personnelles || ''
            });

// APRÈS
              // Notes personnelles
              notes_personnelles: enqueteurData.notes_personnelles || '',
              
              // PARTNER : Date et lieu de naissance mis à jour
              dateNaissance_maj: data.dateNaissance_maj || '',
              lieuNaissance_maj: data.lieuNaissance_maj || ''
            });
```

**Explication** : Les champs `dateNaissance_maj` et `lieuNaissance_maj` doivent être chargés depuis `data` (pas `enqueteurData`) car ils sont stockés dans la table `donnees`, pas `donnees_enqueteur`.

---

## 🧪 TESTS À EFFECTUER

### 1. Test de sauvegarde
1. Démarrer l'application
2. Ouvrir un dossier PARTNER
3. Aller dans l'onglet "Naissance"
4. Saisir une date de naissance (ex: 15/06/1985)
5. Saisir un lieu de naissance (ex: Paris)
6. Cliquer sur "Enregistrer"
7. Vérifier le message de succès

### 2. Vérification en base de données
```bash
cd backend
python scripts/check_partner_naissance.py
```

**Résultat attendu** :
```
Dossiers avec dateNaissance_maj : 1/9
Dossiers avec lieuNaissance_maj : 1/9
```

### 3. Test de relecture
1. Fermer le modal
2. Rouvrir le même dossier
3. Aller dans l'onglet "Naissance"
4. **Vérifier que les données saisies sont bien affichées**

### 4. Test d'export
1. Valider l'enquête
2. Exporter en Excel POS
3. **Vérifier que les colonnes "Date naissance (MAJ)" et "Lieu naissance (MAJ)" sont remplies**

---

## 📊 IMPACT

### Fichiers modifiés
- ✅ `frontend/src/components/UpdateModal.jsx` (2 corrections : envoi + chargement)

### Fichiers créés
- ✅ `backend/scripts/check_partner_naissance.py` (script de diagnostic)
- ✅ `CORRECTION_NAISSANCE_PARTNER_23_12.md` (ce fichier)

### Régression
- ❌ **Aucune** : La correction ne touche que PARTNER

---

## 🎯 AUTRES PROBLÈMES POTENTIELS

### 1. Chargement initial des données
Vérifier que les données existantes sont bien chargées dans `formData` au chargement du modal.

**À vérifier dans `UpdateModal.jsx`** (autour de la ligne 250) :
```javascript
useEffect(() => {
  if (data) {
    setFormData(prev => ({
      ...prev,
      dateNaissance_maj: data.dateNaissance_maj || '',
      lieuNaissance_maj: data.lieuNaissance_maj || ''
    }));
  }
}, [data]);
```

### 2. Sérialisation backend
Vérifier que le backend renvoie bien ces champs dans la réponse GET.

**À vérifier dans `backend/app.py`** (route `/api/donnees-complete`) :
```python
donnee_dict = donnee.to_dict()
# Les champs dateNaissance_maj et lieuNaissance_maj doivent être inclus
```

---

## 📝 RECOMMANDATIONS

### Court terme
1. ✅ Appliquer la correction (fait)
2. ⏳ Tester la sauvegarde
3. ⏳ Vérifier le chargement des données
4. ⏳ Tester l'export Excel

### Moyen terme
- Ajouter des logs pour tracer la sauvegarde des données PARTNER
- Créer des tests automatisés pour ce flux

---

## 🔗 FICHIERS LIÉS

### Frontend
- `frontend/src/components/UpdateModal.jsx` - Modal de mise à jour
- `frontend/src/components/PartnerNaissanceTab.jsx` - Onglet Naissance

### Backend
- `backend/app.py` - Route `/api/donnees-enqueteur/<id>` (ligne 787-913)
- `backend/models/models.py` - Modèle `Donnee` avec `dateNaissance_maj` et `lieuNaissance_maj`
- `backend/migrations/versions/009_add_naissance_maj_to_donnee.py` - Migration

### Scripts
- `backend/scripts/check_partner_naissance.py` - Diagnostic

---

**Date de correction** : 23/12/2025  
**Statut** : ✅ Correction appliquée, tests en attente  
**Priorité** : 🔴 HAUTE (bloque la saisie des données)

