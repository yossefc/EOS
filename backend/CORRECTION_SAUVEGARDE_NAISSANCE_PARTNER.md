# Correction Sauvegarde Date/Lieu de Naissance PARTNER

**Date**: 18 décembre 2025

## 🔴 Problème identifié

Quand l'utilisateur saisit la **date de naissance** et le **lieu de naissance** dans l'onglet "Naissance" de la mise à jour PARTNER, ces données **n'étaient PAS sauvegardées** en base de données.

### Symptômes
- Les champs sont remplis dans l'UI
- Après sauvegarde et rechargement, les champs sont vides
- L'export Excel affiche des colonnes vides pour date/lieu de naissance

## 🔍 Diagnostic

### ✅ Frontend (OK)
Le frontend **envoie correctement** les données :
- `dateNaissance` : Format `YYYY-MM-DD` (ex: "1975-11-27")
- `lieuNaissance` : Texte (ex: "HAILLICOURT")

Code dans `frontend/src/components/UpdateModal.jsx` (lignes 861-889) :

```javascript
// Pour les clients non-EOS (PARTNER)
if (clientCode !== 'EOS') {
  // Construire la date de naissance
  let dateNaissanceComplete = null;
  if (formData.dateNaissanceRetrouvee_jour && 
      formData.dateNaissanceRetrouvee_mois && 
      formData.dateNaissanceRetrouvee_annee) {
    const jour = String(formData.dateNaissanceRetrouvee_jour).padStart(2, '0');
    const mois = String(formData.dateNaissanceRetrouvee_mois).padStart(2, '0');
    const annee = formData.dateNaissanceRetrouvee_annee;
    dateNaissanceComplete = `${annee}-${mois}-${jour}`;
  }
  
  dataToSend = {
    ...dataToSend,
    dateNaissance: dateNaissanceComplete,
    lieuNaissance: formData.lieuNaissanceRetrouvee || null
  };
}
```

### ❌ Backend (PROBLÈME)
La route `/api/donnees-enqueteur/<int:donnee_id>` **ne sauvegardait PAS** ces champs.

**Raison** : La route met à jour uniquement les champs de `DonneeEnqueteur`, mais `dateNaissance` et `lieuNaissance` sont stockés dans la table `Donnee`, pas dans `DonneeEnqueteur`.

## ✅ Solution appliquée

### Modification : `backend/app.py` (ligne 846)

**Avant** :
```python
# Mise à jour de la date de modification
donnee_enqueteur.updated_at = datetime.now()

# Si le code résultat est positif, préparer la facturation
```

**Après** :
```python
# Mise à jour de la date de modification
donnee_enqueteur.updated_at = datetime.now()

# Pour PARTNER (CLIENT_X), mettre à jour dateNaissance et lieuNaissance dans Donnee
if is_client_x:
    if 'dateNaissance' in data:
        if data.get('dateNaissance'):
            donnee_parent.dateNaissance = datetime.strptime(data.get('dateNaissance'), '%Y-%m-%d').date()
            logger.info(f"Date de naissance mise à jour pour enquête {donnee_id}: {donnee_parent.dateNaissance}")
        else:
            donnee_parent.dateNaissance = None
    
    if 'lieuNaissance' in data:
        donnee_parent.lieuNaissance = data.get('lieuNaissance')
        logger.info(f"Lieu de naissance mis à jour pour enquête {donnee_id}: {donnee_parent.lieuNaissance}")
    
    donnee_parent.updated_at = datetime.now()

# Si le code résultat est positif, préparer la facturation
```

### Logique de la correction

1. **Vérifier si c'est PARTNER** : `if is_client_x` (la variable existe déjà dans le code)
2. **Si `dateNaissance` est envoyée** :
   - Si non vide → Parser et sauvegarder dans `donnee_parent.dateNaissance`
   - Si vide → Mettre NULL
3. **Si `lieuNaissance` est envoyée** : Sauvegarder dans `donnee_parent.lieuNaissance`
4. **Mettre à jour `updated_at`** de la donnée parent
5. **Logs** pour faciliter le diagnostic

## 🧪 Tests de validation

### Test 1 : Saisie date/lieu de naissance

**Scénario** :
1. Ouvrir une enquête PARTNER
2. Cliquer sur "Mise à jour"
3. Aller dans l'onglet **"Naissance"**
4. Remplir :
   - Jour : **27**
   - Mois : **11**
   - Année : **1975**
   - Lieu : **HAILLICOURT**
5. Cliquer sur "Enregistrer"

**Résultat attendu** :
- ✅ Message "Données mises à jour avec succès"
- ✅ Logs backend :
  ```
  Date de naissance mise à jour pour enquête X: 1975-11-27
  Lieu de naissance mis à jour pour enquête X: HAILLICOURT
  ```

### Test 2 : Vérifier la persistance

**Scénario** :
1. Après avoir sauvegardé (Test 1)
2. **Recharger la page** (F5)
3. Ouvrir la même enquête
4. Cliquer sur "Mise à jour"
5. Aller dans l'onglet **"Naissance"**

**Résultat attendu** :
- ✅ Jour : **27**
- ✅ Mois : **11**
- ✅ Année : **1975**
- ✅ Lieu : **HAILLICOURT**

**Les champs sont pré-remplis avec les valeurs sauvegardées.**

### Test 3 : Vérifier en base de données

**Scénario** :
Exécuter cette requête SQL :

```sql
SELECT 
    id, 
    "numeroDossier", 
    nom, 
    prenom, 
    "dateNaissance", 
    "lieuNaissance"
FROM donnees 
WHERE client_id = 11  -- PARTNER
  AND "dateNaissance" IS NOT NULL
ORDER BY id DESC 
LIMIT 5;
```

**Résultat attendu** :
```
id  | numeroDossier | nom     | prenom  | dateNaissance | lieuNaissance
----|---------------|---------|---------|---------------|---------------
351 | 1             | KORFINI | RICHARD | 1975-11-27    | HAILLICOURT
```

### Test 4 : Vérifier l'export Excel

**Scénario** :
1. Valider l'enquête du Test 1
2. Exporter en **Excel (Enquêtes Positives)**
3. Ouvrir le fichier Excel

**Résultat attendu** :
- ✅ Colonne `JOUR` : **27**
- ✅ Colonne `MOIS` : **11**
- ✅ Colonne `ANNEE NAISSANCE` : **1975**
- ✅ Colonne `LIEUNAISSANCE` : **HAILLICOURT**

### Test 5 : Vérifier l'export Word

**Scénario** :
1. Exporter en **Word (Enquêtes Positives)**
2. Ouvrir le fichier Word

**Résultat attendu** :
- ✅ Section "DONNÉES IMPORTÉES" contient :
  ```
  Naissance: 27/11/1975 à HAILLICOURT
  ```

## 📊 Flux de données corrigé

### Avant la correction ❌
```
Frontend (UI)
   ↓ (envoie dateNaissance + lieuNaissance)
Backend /api/donnees-enqueteur/<id>
   ↓ (IGNORE les champs dateNaissance et lieuNaissance)
Base de données
   ↓ (dateNaissance et lieuNaissance restent NULL)
❌ PERDU
```

### Après la correction ✅
```
Frontend (UI)
   ↓ (envoie dateNaissance + lieuNaissance)
Backend /api/donnees-enqueteur/<id>
   ↓ (SI is_client_x → met à jour donnee_parent.dateNaissance et lieuNaissance)
Base de données
   ↓ (dateNaissance et lieuNaissance sauvegardés dans table 'donnees')
✅ PERSISTÉ
   ↓
Export Excel/Word
   ↓ (colonnes JOUR/MOIS/ANNEE/LIEUNAISSANCE remplies)
✅ AFFICHÉ
```

## 🔗 Fichiers modifiés

1. ✅ `backend/app.py` (fonction `update_donnee_enqueteur`, ligne 846)
   - Ajout de 14 lignes pour sauvegarder date/lieu de naissance

2. ✅ `backend/CORRECTION_SAUVEGARDE_NAISSANCE_PARTNER.md`
   - Cette documentation

## ⚠️ Important

### Backend à redémarrer
Le backend **doit être redémarré** pour que la correction soit active.

### Aucun impact EOS
La correction est **conditionnée** par `if is_client_x`, donc uniquement pour PARTNER (pas EOS).

### Logs ajoutés
Les logs permettent de vérifier que la sauvegarde fonctionne :
```
INFO - Date de naissance mise à jour pour enquête 351: 1975-11-27
INFO - Lieu de naissance mis à jour pour enquête 351: HAILLICOURT
```

## 🎉 Résultat attendu

Après redémarrage du backend :
- ✅ Saisie date/lieu dans l'onglet "Naissance" → **Sauvegardé**
- ✅ Rechargement de la page → **Champs pré-remplis**
- ✅ Vérification DB → **Données présentes**
- ✅ Export Excel → **Colonnes remplies**
- ✅ Export Word → **Date affichée**

**Le problème est maintenant résolu !** 🚀

---

## 📝 Notes techniques

### Pourquoi `donnee_parent` et pas `donnee_enqueteur` ?

**Structure de la base de données** :
- Table `donnees` : Contient les données **importées** (dont `dateNaissance` et `lieuNaissance`)
- Table `donnees_enqueteur` : Contient les données **ajoutées par l'enquêteur**

**Pour PARTNER**, quand l'enquêteur saisit la date/lieu de naissance, cela **complète/corrige** les données importées, donc on met à jour la table `donnees` (via `donnee_parent`).

### Pourquoi la condition `if is_client_x` ?

La variable `is_client_x` est déjà définie ligne 800 :
```python
is_client_x = client and client.code != 'EOS'
```

Elle est `True` pour PARTNER (et tout client non-EOS), et `False` pour EOS.

Cela garantit qu'**EOS n'est pas affecté** par cette modification.

