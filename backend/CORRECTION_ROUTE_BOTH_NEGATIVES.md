# Correction Route /both pour Enquêtes Négatives

**Date**: 18 décembre 2025

## 🔴 Problème rencontré

L'utilisateur a reçu une erreur **404** lors de l'export des enquêtes négatives :
```
OPTIONS /api/partner/exports/enquetes/negatives/both HTTP/1.1" 404
```

**Cause** : La route `/api/partner/exports/enquetes/negatives/both` n'existait pas.

---

## ✅ Solution appliquée

### Création de la route `/both` pour enquêtes négatives

**Fichier modifié** : `backend/routes/partner_export.py`

**Nouvelle route créée** :
```python
@partner_export_bp.route('/api/partner/exports/enquetes/negatives/both', methods=['POST'])
def export_enquetes_negatives_both():
    """
    Génère Word ET Excel pour les enquêtes négatives en une seule fois
    Archive seulement après avoir généré les 2 fichiers
    """
```

**Fonctionnement** :
1. Récupère les enquêtes négatives (`code_resultat IN ('N', 'I')`)
2. Génère le fichier **Word** (.docx)
3. Génère le fichier **Excel** (.xls)
4. Combine les 2 fichiers dans un **ZIP**
5. Archive les enquêtes **APRÈS** génération des 2 fichiers
6. Retourne le ZIP à télécharger

**Robustesse** :
- ✅ Fonctionne même si **0 enquêtes** (génère fichiers vides avec headers)
- ✅ Ne crée pas de batch si 0 enquêtes (évite de polluer les archives)
- ✅ Logs informatifs pour le diagnostic

---

## 📊 Excel Enquêtes Positives : Date/Lieu de naissance

### Vérification effectuée

**État actuel** : ✅ **DÉJÀ FONCTIONNEL**

Le code d'export Excel positif (`partner_export_service.py`, lignes 473-482) inclut **DÉJÀ** :

```python
# Date naissance (JOUR, MOIS, ANNEE NAISSANCE)
if donnee.dateNaissance:
    row_data.append(donnee.dateNaissance.day)    # Colonne JOUR
    row_data.append(donnee.dateNaissance.month)  # Colonne MOIS
    row_data.append(donnee.dateNaissance.year)   # Colonne ANNEE NAISSANCE
else:
    row_data.extend(['', '', ''])

row_data.append(donnee.lieuNaissance or '')  # Colonne LIEUNAISSANCE
```

**Colonnes exportées** :
- `JOUR` : Jour de naissance (1-31)
- `MOIS` : Mois de naissance (1-12)
- `ANNEE NAISSANCE` : Année de naissance (ex: 1975)
- `LIEUNAISSANCE` : Lieu de naissance (ex: HAILLICOURT)

**Source des données** :
- **Import** : `Donnee.dateNaissance` et `Donnee.lieuNaissance` remplis lors de l'import
- **Mise à jour** : `Donnee.dateNaissance` et `Donnee.lieuNaissance` mis à jour via la route `PUT /api/donnees/<id>`

**Conclusion** : Les colonnes sont déjà présentes dans l'Excel. Si elles apparaissent vides, c'est que :
1. La date de naissance n'a pas été importée correctement (problème import)
2. La date de naissance n'a pas été saisie dans l'onglet "Naissance" de la mise à jour
3. La date de naissance n'a pas été sauvegardée correctement

---

## 🧪 Tests de validation

### Test 1 : Export Enquêtes Négatives /both

**Scénario** :
1. Avoir au moins 1 enquête négative validée dans PARTNER
2. Cliquer sur le bouton d'export qui appelle `/api/partner/exports/enquetes/negatives/both`

**Résultat attendu** :
- ✅ Fichier ZIP téléchargé contenant :
  - `cr_DD_MM_YYYY_HH_MM_SS.docx` (Word)
  - `cr_DD_MM_YYYY_HH_MM_SS.xls` (Excel)
- ✅ Pas d'erreur 404

### Test 2 : Export Enquêtes Négatives /both (0 enquêtes)

**Scénario** :
1. Aucune enquête négative validée dans PARTNER
2. Cliquer sur le bouton d'export

**Résultat attendu** :
- ✅ Fichier ZIP téléchargé contenant :
  - Word avec 0 pages
  - Excel avec headers uniquement
- ✅ Pas d'erreur 404
- ✅ Log : "Export combiné enquêtes négatives PARTNER: fichiers vides (0 enquêtes)"

### Test 3 : Vérifier date/lieu de naissance dans Excel Positif

**Scénario** :
1. Créer une enquête PARTNER
2. Ouvrir "Mise à jour" → Onglet "Naissance"
3. Remplir :
   - Date de naissance : **27/11/1975**
   - Lieu de naissance : **HAILLICOURT**
4. Sauvegarder
5. Valider l'enquête
6. Exporter en Excel (Enquêtes Positives)

**Résultat attendu** :
- ✅ Colonne `JOUR` : **27**
- ✅ Colonne `MOIS` : **11**
- ✅ Colonne `ANNEE NAISSANCE` : **1975**
- ✅ Colonne `LIEUNAISSANCE` : **HAILLICOURT**

**Si les colonnes sont vides** :
1. Vérifier que la date a bien été **sauvegardée** :
   - Ouvrir l'enquête → "Mise à jour" → Vérifier que la date apparaît
2. Vérifier en DB :
   ```sql
   SELECT id, "numeroDossier", nom, "dateNaissance", "lieuNaissance" 
   FROM donnees 
   WHERE client_id = 11  -- PARTNER
   ORDER BY id DESC LIMIT 5;
   ```
3. Si `dateNaissance` est NULL en DB :
   - Le problème est dans la **sauvegarde** (route PUT) ou dans l'**import**

---

## 🔗 Fichiers modifiés

1. ✅ `backend/routes/partner_export.py`
   - Ajout route `/api/partner/exports/enquetes/negatives/both`

2. ✅ `backend/CORRECTION_ROUTE_BOTH_NEGATIVES.md`
   - Cette documentation

---

## ⚠️ Important

### Backend à redémarrer
Le backend doit être redémarré pour que la nouvelle route soit accessible.

### Aucun impact EOS
La correction concerne uniquement PARTNER.

### Frontend à vérifier
Vérifier que le frontend appelle bien la route `/both` pour les enquêtes négatives.

---

## 🎉 Résultat attendu

Après redémarrage du backend :
- ✅ Route `/api/partner/exports/enquetes/negatives/both` accessible (plus d'erreur 404)
- ✅ Export fonctionne (ZIP avec Word + Excel)
- ✅ Excel Enquêtes Positives inclut date/lieu de naissance (déjà fonctionnel)

---

## 📝 Notes sur la date de naissance

**Le code d'export est correct.** Si les colonnes date/lieu de naissance apparaissent vides dans l'Excel, cela signifie que :

1. **La date n'a pas été importée correctement** :
   - Vérifier que l'import PARTNER combine bien les colonnes JOUR/MOIS/ANNEE
   - Voir `backend/import_engine.py` (fonction `_preprocess_client_x_record`)

2. **La date n'a pas été saisie dans l'UI** :
   - Onglet "Mise à jour" → Onglet "Naissance"
   - Vérifier que les champs sont visibles et fonctionnels

3. **La date n'a pas été sauvegardée** :
   - Vérifier la route `PUT /api/donnees/<id>` (lignes 508-516 de `backend/app.py`)
   - Vérifier que `dateNaissance` et `lieuNaissance` sont bien updatés

**Pour diagnostiquer** :
1. Ouvrir une enquête PARTNER
2. "Mise à jour" → Onglet "Naissance"
3. Remplir la date et le lieu
4. Sauvegarder
5. Recharger la page
6. Vérifier que la date/lieu sont toujours présents
7. Si oui → le problème est résolu
8. Si non → le problème est dans la sauvegarde (backend)

