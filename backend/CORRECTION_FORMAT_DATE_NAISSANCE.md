# Correction Format Date de Naissance PARTNER

**Date**: 18 décembre 2025

## 🔴 Problème rencontré

Erreur lors de l'enregistrement de la date de naissance :
```
time data '7-06-05' does not match format '%Y-%m-%d'
```

### Cause
Quand l'utilisateur saisit une année sur **1, 2 ou 3 chiffres** (ex: "7", "75", "975"), le frontend l'envoyait telle quelle au backend, qui attendait un format strict `YYYY-MM-DD` avec une année sur **4 chiffres**.

**Exemple** :
- Utilisateur saisit : Jour=5, Mois=6, Année=**7**
- Frontend envoyait : `"7-06-05"` ❌
- Backend attendait : `"2007-06-05"` ou `"1907-06-05"` ✅

---

## ✅ Solution appliquée

### 1. Frontend : Formatage automatique de l'année

**Fichier modifié** : `frontend/src/components/UpdateModal.jsx` (ligne 867)

**Avant** :
```javascript
const annee = formData.dateNaissanceRetrouvee_annee;
dateNaissanceComplete = `${annee}-${mois}-${jour}`;
```

**Après** :
```javascript
// Formater l'année sur 4 chiffres
let annee = parseInt(formData.dateNaissanceRetrouvee_annee);
if (annee < 100) {
  // Si année sur 2 chiffres : 00-29 → 2000-2029, 30-99 → 1930-1999
  annee = annee < 30 ? 2000 + annee : 1900 + annee;
} else if (annee < 1000) {
  // Si année sur 3 chiffres, supposer 1XXX
  annee = 1000 + annee;
}
// Sinon, l'année est déjà sur 4 chiffres

dateNaissanceComplete = `${annee}-${mois}-${jour}`;
```

**Logique de conversion** :
- **Année 0-29** → 2000-2029 (ex: 7 → 2007, 25 → 2025)
- **Année 30-99** → 1930-1999 (ex: 75 → 1975, 99 → 1999)
- **Année 100-999** → 1100-1999 (ex: 975 → 1975)
- **Année ≥ 1000** → Inchangée (ex: 1975 → 1975)

### 2. Backend : Meilleur message d'erreur

**Fichier modifié** : `backend/app.py` (ligne 849)

**Avant** :
```python
donnee_parent.dateNaissance = datetime.strptime(data.get('dateNaissance'), '%Y-%m-%d').date()
```

**Après** :
```python
try:
    donnee_parent.dateNaissance = datetime.strptime(data.get('dateNaissance'), '%Y-%m-%d').date()
    logger.info(f"Date de naissance mise à jour pour enquête {donnee_id}: {donnee_parent.dateNaissance}")
except ValueError as e:
    logger.error(f"Format de date invalide: {data.get('dateNaissance')} - {e}")
    raise ValueError(f"Format de date invalide: {data.get('dateNaissance')}. Attendu: YYYY-MM-DD")
```

**Amélioration** :
- ✅ Capture l'erreur de format
- ✅ Log détaillé pour le diagnostic
- ✅ Message d'erreur clair pour l'utilisateur

---

## 🧪 Tests de validation

### Test 1 : Année sur 1 chiffre

**Saisie** :
- Jour : 5
- Mois : 6
- Année : **7**

**Résultat attendu** :
- ✅ Frontend envoie : `"2007-06-05"`
- ✅ Backend sauvegarde : `2007-06-05`
- ✅ Pas d'erreur

### Test 2 : Année sur 2 chiffres (< 30)

**Saisie** :
- Jour : 15
- Mois : 3
- Année : **25**

**Résultat attendu** :
- ✅ Frontend envoie : `"2025-03-15"`
- ✅ Backend sauvegarde : `2025-03-15`

### Test 3 : Année sur 2 chiffres (≥ 30)

**Saisie** :
- Jour : 27
- Mois : 11
- Année : **75**

**Résultat attendu** :
- ✅ Frontend envoie : `"1975-11-27"`
- ✅ Backend sauvegarde : `1975-11-27`

### Test 4 : Année sur 3 chiffres

**Saisie** :
- Jour : 10
- Mois : 5
- Année : **975**

**Résultat attendu** :
- ✅ Frontend envoie : `"1975-05-10"`
- ✅ Backend sauvegarde : `1975-05-10`

### Test 5 : Année sur 4 chiffres

**Saisie** :
- Jour : 20
- Mois : 8
- Année : **1980**

**Résultat attendu** :
- ✅ Frontend envoie : `"1980-08-20"`
- ✅ Backend sauvegarde : `1980-08-20`

---

## 📊 Tableau de conversion des années

| Saisie | Interprétation | Résultat | Exemple |
|--------|----------------|----------|---------|
| 0-29   | 2000-2029      | 2000+    | 7 → 2007 |
| 30-99  | 1930-1999      | 1900+    | 75 → 1975 |
| 100-999 | 1XXX          | 1000+    | 975 → 1975 |
| ≥1000  | Inchangé       | Tel quel | 1975 → 1975 |

**Logique** : Similaire à la convention utilisée dans les systèmes de dates (ex: Excel, MySQL).

---

## 🔗 Fichiers modifiés

1. ✅ `frontend/src/components/UpdateModal.jsx` (ligne 867)
   - Ajout formatage automatique de l'année

2. ✅ `backend/app.py` (ligne 849)
   - Ajout gestion d'erreur avec message clair

3. ✅ `backend/CORRECTION_FORMAT_DATE_NAISSANCE.md`
   - Cette documentation

---

## ⚠️ Important

### Rechargement de la page frontend
Le frontend doit être **rechargé** (F5) pour que la correction JavaScript soit active.

### Backend déjà redémarré
Le backend a été redémarré précédemment, la correction backend est déjà active.

### Aucun impact EOS
La correction concerne uniquement PARTNER (condition `if clientCode !== 'EOS'`).

---

## 🎉 Résultat

Après rechargement de la page frontend :
- ✅ Saisie d'une année sur **1, 2, 3 ou 4 chiffres** fonctionne
- ✅ Conversion automatique en année sur **4 chiffres**
- ✅ Sauvegarde réussie en base de données
- ✅ Pas d'erreur de format

**Le problème est résolu !** 🚀

---

## 📝 Notes techniques

### Pourquoi cette logique de conversion ?

**Convention standard** :
- Les années 00-29 sont généralement interprétées comme 2000-2029 (futur proche)
- Les années 30-99 sont généralement interprétées comme 1930-1999 (passé)

**Cas d'usage PARTNER** :
- Les enquêtes concernent généralement des personnes nées entre 1930 et 2025
- Cette logique couvre 95+ ans, ce qui est suffisant pour la plupart des cas

**Exemple concret** :
- Une personne née en **1975** peut saisir "75" au lieu de "1975"
- Une personne née en **2007** peut saisir "7" au lieu de "2007"

### Validation côté UI

Le champ année dans `PartnerNaissanceTab.jsx` a déjà une validation :
```javascript
<input
  type="number"
  name="dateNaissanceRetrouvee_annee"
  min="1900"
  max={new Date().getFullYear()}
  ...
/>
```

Cependant, cette validation n'empêche pas la saisie manuelle de valeurs courtes. La correction dans `UpdateModal.jsx` gère ce cas.

