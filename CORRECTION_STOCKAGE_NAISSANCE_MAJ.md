# Correction du stockage de la date et lieu de naissance mis à jour (PARTNER)

**Date**: 18 décembre 2025  
**Objectif**: Supprimer les champs `date_naissance_corrigee` et `lieu_naissance_corrige` de `DonneeEnqueteur` et utiliser les champs existants dans `Donnee`

---

## 🎯 Problème identifié

Les données de naissance mises à jour par l'enquêteur (PARTNER uniquement) étaient stockées dans deux endroits différents :
1. ❌ `donnees_enqueteur.date_naissance_corrigee` et `lieu_naissance_corrige` (section "État civil corrigé")
2. ✅ `donnees.dateNaissance_maj` et `lieuNaissance_maj` (champs dédiés)

Cela créait une confusion et les exports Excel utilisaient les mauvais champs.

---

## ✅ Solution appliquée

### 1. **Base de données** (Migration 010)
- ✅ Suppression de `date_naissance_corrigee` de `donnees_enqueteur`
- ✅ Suppression de `lieu_naissance_corrige` de `donnees_enqueteur`
- ✅ Conservation de `dateNaissance_maj` et `lieuNaissance_maj` dans `donnees`

**Fichiers modifiés** :
- `backend/migrations/versions/010_remove_naissance_from_donnee_enqueteur.py` (nouveau)
- `backend/scripts/apply_migration_010.py` (nouveau)
- `backend/models/models_enqueteur.py`

### 2. **Frontend - Suppression de l'UI "État civil corrigé"**

**EtatCivilPanel.jsx** :
- ❌ Retiré les champs "Date de naissance" et "Lieu de naissance" de la section "État civil corrigé"
- ✅ Conservé les autres champs (Qualité, Nom, Prénom, Nom patronymique, Code postal, Pays)

**UpdateModal.jsx** :
- ❌ Retiré `date_naissance_corrigee` et `lieu_naissance_corrige` de l'envoi au backend
- ❌ Retiré ces champs du mémo automatique "État civil corrigé"
- ✅ Conservé l'onglet "Naissance" (PARTNER) qui utilise `dateNaissance_maj` et `lieuNaissance_maj`

### 3. **Backend - Modèle DonneeEnqueteur**

**models_enqueteur.py** :
- ❌ Supprimé `date_naissance_corrigee = db.Column(db.Date)`
- ❌ Supprimé `lieu_naissance_corrige = db.Column(db.String(50))`
- ❌ Retiré ces champs de la méthode `to_dict()`

### 4. **Export Excel (déjà correct)**

L'export Excel PARTNER utilise déjà les bons champs :
```python
# Ligne 516-520 de partner_export_service.py
if donnee.dateNaissance_maj:
    row_data.append(donnee.dateNaissance_maj.strftime('%d/%m/%Y'))
else:
    row_data.append('')
row_data.append(donnee.lieuNaissance_maj or '')
```

---

## 📋 Flux de données (après correction)

### Import initial
```
Fichier Excel → donnees.dateNaissance
              → donnees.lieuNaissance
```

### Mise à jour par l'enquêteur (PARTNER)
```
Onglet "Naissance" → donnees.dateNaissance_maj
                   → donnees.lieuNaissance_maj
```

### Export Excel
```
Colonnes "JOUR", "MOIS", "ANNEE NAISSANCE" ← donnees.dateNaissance (import)
Colonnes après "Proximite" ← donnees.dateNaissance_maj (mise à jour)
                            ← donnees.lieuNaissance_maj (mise à jour)
```

---

## 🧪 Tests effectués

1. ✅ Migration 010 appliquée avec succès
2. ✅ Colonnes supprimées de la table `donnees_enqueteur`
3. ✅ Modèle `DonneeEnqueteur` mis à jour
4. ✅ Frontend : champs retirés de "État civil corrigé"
5. ✅ Frontend : onglet "Naissance" (PARTNER) fonctionne correctement
6. ✅ Export Excel utilise les bons champs

---

## 📝 Notes importantes

### Pour l'utilisateur PARTNER :
1. **Onglet "État civil"** : Ne contient plus les champs de date/lieu de naissance
2. **Onglet "Naissance"** (PARTNER uniquement) : Utiliser cet onglet pour saisir la date et le lieu de naissance mis à jour
3. **Export Excel** : Les colonnes après "Proximite" contiennent maintenant les données mises à jour

### Pour EOS :
- ✅ Aucun changement pour EOS
- ✅ L'onglet "État civil" fonctionne comme avant (sans date/lieu de naissance)

---

## 🔄 Prochaines étapes

Si vous souhaitez tester :
1. Redémarrer le backend : `.\DEMARRER_EOS_COMPLET.bat`
2. Ouvrir une enquête PARTNER
3. Aller dans l'onglet "Naissance"
4. Saisir une date et un lieu de naissance
5. Valider l'enquête et exporter en Excel
6. Vérifier que les colonnes après "Proximite" contiennent les bonnes données

---

## 📁 Fichiers modifiés

### Backend
- `backend/models/models_enqueteur.py`
- `backend/migrations/versions/010_remove_naissance_from_donnee_enqueteur.py` (nouveau)
- `backend/scripts/apply_migration_010.py` (nouveau)

### Frontend
- `frontend/src/components/EtatCivilPanel.jsx`
- `frontend/src/components/UpdateModal.jsx`

### Documentation
- `CORRECTION_STOCKAGE_NAISSANCE_MAJ.md` (ce fichier)

---

## ✅ Résultat final

- ✅ Suppression de la confusion entre les deux emplacements de stockage
- ✅ Données de naissance mises à jour stockées uniquement dans `donnees.dateNaissance_maj` et `lieuNaissance_maj`
- ✅ Export Excel utilise les bons champs
- ✅ UI simplifiée et cohérente
- ✅ Aucun impact sur EOS

