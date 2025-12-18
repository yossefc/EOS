# Correction Import Date de Naissance et NJF - PARTNER

**Date**: 18 décembre 2025

## 🎯 Problème identifié

L'import des fichiers PARTNER ne traitait pas correctement :
1. **Date de naissance** : Les colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` n'étaient pas combinées
2. **NJF** (Nom de Jeune Fille) : La colonne `NJF` n'était pas mappée

## 🔍 Cause

Dans le fichier `backend/import_engine.py`, la fonction `_preprocess_client_x_record()` ne s'appliquait qu'au client `CLIENT_X`, pas à `PARTNER`.

## ✅ Corrections apportées

### 1. Combinaison de la date de naissance (`backend/import_engine.py`)

**Avant** (ligne 355) :
```python
if not client or client.code != 'CLIENT_X':
    return record
```

**Après** :
```python
if not client or client.code not in ['CLIENT_X', 'PARTNER']:
    return record
```

**Impact** : Maintenant, les colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` sont combinées en format `DD/MM/YYYY` lors de l'import PARTNER.

### 2. Ajout du mapping NJF

**Script créé** : `backend/scripts/add_njf_mapping_partner.py`

Ce script ajoute le mapping :
- **Colonne Excel** : `NJF`
- **Champ interne** : `nomPatronymique`

**Résultat** : La colonne NJF du fichier Excel est maintenant importée dans le champ `nomPatronymique`.

## 📋 Structure du fichier d'import PARTNER

Format attendu (colonnes clés) :
```
NUM | NOM | PRENOM | NJF | JOUR | MOIS | ANNEE NAISSANCE | LIEUNAISSANCE | ...
1   | KORFINI | RICHARD |  | 12 | 6 | 1964 | HAILLICOURT | ...
```

## 🧪 Tests requis

Pour vérifier que tout fonctionne :

### Étape 1 : Ré-importer un fichier PARTNER
1. Aller dans l'interface d'import
2. Sélectionner le client PARTNER
3. Importer un fichier Excel avec les colonnes JOUR/MOIS/ANNEE et NJF
4. Vérifier dans les logs : `Date de naissance combinée: XX/XX/XXXX`

### Étape 2 : Vérifier l'affichage dans Update Modal
1. Ouvrir une enquête PARTNER
2. Cliquer sur "Mise à jour"
3. **Vérifier** : La date de naissance s'affiche correctement

### Étape 3 : Vérifier l'export Excel
1. Valider une enquête PARTNER avec date de naissance et NJF
2. Exporter en Excel positif
3. **Vérifier** :
   - Colonne `NJF` : contient la valeur
   - Colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` : contiennent 12, 6, 1964

### Étape 4 : Vérifier l'export Word
1. Exporter en Word positif
2. **Vérifier** :
   - Section "DONNÉES IMPORTÉES" contient la date de naissance : `Ne le 12/06/1964`
   - Le document reste sur 1 page

## 📝 Notes importantes

- **Les enquêtes existantes** importées avant cette correction ne seront pas affectées
- **Il faut ré-importer** les fichiers pour que la date de naissance soit correctement traitée
- Le backend doit être redémarré pour appliquer les changements

## 🔗 Fichiers modifiés

1. `backend/import_engine.py` (ligne 355)
2. `backend/scripts/add_njf_mapping_partner.py` (nouveau)

## ✨ Résultat attendu

Après ré-import d'un fichier PARTNER :
- ✅ Date de naissance combinée et stockée : `12/06/1964`
- ✅ NJF importé dans `nomPatronymique`
- ✅ Affichage correct dans Update Modal
- ✅ Export Excel avec NJF et date de naissance complète
- ✅ Export Word avec date de naissance formatée

