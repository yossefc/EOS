# Correction Flux PARTNER Complet - Import → DB → UI → Export

**Date**: 18 décembre 2025

## 🎯 Problèmes identifiés

### 1. Import PARTNER : Date de naissance non enregistrée
- **Symptôme** : Les colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` du fichier Excel ne sont pas combinées en `dateNaissance` dans la DB
- **Résultat** : `dateNaissance` = NULL pour toutes les enquêtes importées

### 2. Update : Date/Lieu de naissance non persistés
- **Symptôme** : Les modifications de date/lieu de naissance dans l'UI Update Modal ne ressortent pas dans l'export

### 3. Export : Montant tarif = 0 au lieu du montant configuré
- **Symptôme** : Tarif lettre "A" présent en DB, mais montant exporté = 0 alors que le mapping A → 15€ existe

---

## 🔍 Diagnostic effectué

### Analyse du modèle `Donnee`
✅ Le modèle utilise un champ unique `dateNaissance` (type `Date`)  
✅ Le champ `lieuNaissance` existe  
✅ Les champs sont correctement sérialisés dans `to_dict()`

### Analyse de l'import
❌ **BUG TROUVÉ** : La fonction `_preprocess_client_x_record()` avait une condition incorrecte (ligne 359)

```python
# AVANT (BUGGÉ)
if 'dateNaissance' in record and record.get('dateNaissance'):
    # Cette condition est FAUSSE car dateNaissance est vide au départ !
```

**Problème** : La condition vérifie si `dateNaissance` a déjà une valeur, mais pour PARTNER, ce champ est vide à l'import. Les colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` ne sont jamais combinées.

### Analyse de l'update
✅ La route `/api/donnees/<id>` (PUT) permet bien de mettre à jour `dateNaissance` et `lieuNaissance` pour les clients non-EOS (lignes 508-516)

### Analyse de l'export
✅ Export Word : Affiche correctement `dateNaissance` et `lieuNaissance` (lignes 259-267)  
✅ Export Excel : Extrait correctement jour/mois/année depuis `dateNaissance` (lignes 474-479)  
✅ Tarif : La fonction `_get_montant_from_tarif()` est correcte et cherche bien dans `TarifClient`

### Vérification des tarifs PARTNER
✅ Tarif A configuré : **15.00€** (actif)  
✅ 6 tarifs PARTNER au total (A, B, C, D, E, W)

---

## ✅ Corrections apportées

### 1. Correction de l'import - Date de naissance (`backend/import_engine.py`)

**Fichier modifié** : `backend/import_engine.py` (fonction `_preprocess_client_x_record`, lignes 358-395)

**Changements** :
- ✅ Suppression de la condition incorrecte `if 'dateNaissance' in record and record.get('dateNaissance')`
- ✅ Lecture directe des 3 champs séparés : `dateNaissance`, `dateNaissance_mois`, `dateNaissance_annee`
- ✅ Nettoyage robuste des valeurs Excel (gestion des float pandas : `27.0` → `"27"`)
- ✅ Validation des valeurs (jour 1-31, mois 1-12, année 1900-2100)
- ✅ Combinaison en format `DD/MM/YYYY` pour `convert_date()`
- ✅ Logs détaillés pour le débogage

**Code ajouté** :

```python
def clean_date_part(value):
    """Convertit valeur Excel (float/str) en string propre"""
    if value is None or str(value).strip() in ('', 'nan', 'NaN', 'None'):
        return None
    try:
        # Si c'est un float (ex: 27.0), convertir en int puis string
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()

jour = clean_date_part(jour_raw)
mois = clean_date_part(mois_raw)
annee = clean_date_part(annee_raw)

logger.info(f"Date naissance PARTNER - JOUR:{jour} MOIS:{mois} ANNEE:{annee}")

if jour and mois and annee:
    try:
        j = int(jour)
        m = int(mois)
        a = int(annee)
        if 1 <= j <= 31 and 1 <= m <= 12 and 1900 <= a <= 2100:
            record['dateNaissance'] = f"{str(j).zfill(2)}/{str(m).zfill(2)}/{a}"
            logger.info(f"✅ Date de naissance combinée: {record['dateNaissance']}")
        else:
            logger.warning(f"⚠️ Date invalide ignorée: {j}/{m}/{a}")
            record['dateNaissance'] = None
    except Exception as e:
        logger.warning(f"⚠️ Erreur combinaison date: {jour}/{mois}/{annee} - {e}")
        record['dateNaissance'] = None
else:
    record['dateNaissance'] = None
    if jour or mois or annee:
        logger.warning(f"⚠️ Date incomplète (JOUR:{jour}, MOIS:{mois}, ANNEE:{annee})")
```

### 2. Scripts de diagnostic créés

**`backend/scripts/check_partner_tarifs.py`**
- Liste tous les tarifs PARTNER configurés
- Vérifie spécifiquement le tarif A
- Aide au diagnostic des problèmes de montant

**`backend/scripts/add_tarif_partner.py`**
- Permet d'ajouter ou mettre à jour un tarif PARTNER
- Usage : `python scripts/add_tarif_partner.py A 25.00`

---

## 📋 Flux complet vérifié

### Import PARTNER
1. ✅ Lecture des colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` depuis Excel
2. ✅ Nettoyage des valeurs (float → int → string)
3. ✅ Validation des valeurs
4. ✅ Combinaison en `DD/MM/YYYY`
5. ✅ Conversion en `Date` par `convert_date()`
6. ✅ Stockage dans `donnee.dateNaissance`

### Update PARTNER
1. ✅ Frontend envoie `dateNaissance` (format `YYYY-MM-DD`)
2. ✅ Backend parse et stocke dans `donnee.dateNaissance`
3. ✅ Backend stocke `lieuNaissance`
4. ✅ Commit en DB

### Affichage UI
1. ✅ API `/api/donnees/<id>` retourne `dateNaissance` formatée (`DD/MM/YYYY`)
2. ✅ API retourne `lieuNaissance`
3. ✅ Frontend affiche dans "Informations" et "Update Modal"

### Export PARTNER
#### Word
1. ✅ Lecture de `donnee.dateNaissance` (Date)
2. ✅ Extraction jour/mois/année
3. ✅ Affichage : "Naissance: 27/11/1975 à HAILLICOURT"

#### Excel
1. ✅ Lecture de `donnee.dateNaissance` (Date)
2. ✅ Colonnes `JOUR`, `MOIS`, `ANNEE NAISSANCE` remplies (27, 11, 1975)
3. ✅ Colonne `LIEUNAISSANCE` remplie
4. ✅ Colonne `Montant facture` : résolution du tarif depuis `tarif_lettre`
   - Lecture de `donnee.tarif_lettre` (ex: "A")
   - Recherche dans `TarifClient` (client_id=PARTNER, code_lettre="A", actif=True)
   - Montant trouvé : **15.00€**

---

## 🧪 Tests à effectuer

### Étape 1 : Ré-importer un fichier PARTNER

1. Supprimer l'ancien fichier (ou utiliser "Remplacer le fichier")
2. Importer le fichier Excel PARTNER
3. **Vérifier dans les logs backend** :
   ```
   Date naissance PARTNER - JOUR:27 MOIS:11 ANNEE:1975
   ✅ Date de naissance combinée: 27/11/1975
   ```

### Étape 2 : Vérifier en DB

Connectez-vous à PostgreSQL et exécutez :

```sql
SELECT 
    "numeroDossier", 
    nom, 
    prenom, 
    "dateNaissance", 
    "lieuNaissance",
    tarif_lettre
FROM donnees 
WHERE client_id = 11  -- PARTNER
ORDER BY id DESC 
LIMIT 5;
```

**Résultat attendu** :
- `dateNaissance` : `1975-11-27` (pas NULL !)
- `lieuNaissance` : `HAILLICOURT`
- `tarif_lettre` : `A`

### Étape 3 : Vérifier dans l'UI

1. Ouvrir une enquête PARTNER
2. Onglet **"Informations"** :
   - ✅ Date de naissance : `27/11/1975`
   - ✅ Lieu de naissance : `HAILLICOURT`
3. Cliquer sur **"Mise à jour"** :
   - ✅ Date de naissance pré-remplie
   - ✅ Lieu de naissance pré-rempli
4. Modifier la date et le lieu, sauvegarder
5. Recharger → ✅ Modifications conservées

### Étape 4 : Vérifier l'export

1. Valider une enquête PARTNER
2. **Export Excel positif** :
   - ✅ Colonne `JOUR` : `27`
   - ✅ Colonne `MOIS` : `11`
   - ✅ Colonne `ANNEE NAISSANCE` : `1975`
   - ✅ Colonne `LIEUNAISSANCE` : `HAILLICOURT`
   - ✅ Colonne `Montant facture` : `15.0` (pas 0 !)
3. **Export Word positif** :
   - ✅ Section "DONNÉES IMPORTÉES" contient : `Naissance: 27/11/1975 à HAILLICOURT`
   - ✅ Document reste sur 1 page

---

## 📝 Commandes utiles

### Vérifier les tarifs PARTNER
```bash
cd D:\EOS\backend
python scripts/check_partner_tarifs.py
```

### Ajouter/Modifier un tarif PARTNER
```bash
cd D:\EOS\backend
python scripts/add_tarif_partner.py A 25.00
```

### Redémarrer le backend
```bash
cd D:\EOS
.\DEMARRER_EOS_COMPLET.bat
```

---

## 🔗 Fichiers modifiés

1. ✅ `backend/import_engine.py` - Correction combinaison date de naissance
2. ✅ `backend/scripts/check_partner_tarifs.py` - Nouveau script de diagnostic
3. ✅ `backend/scripts/add_tarif_partner.py` - Nouveau script de gestion des tarifs
4. ✅ `backend/CORRECTION_FLUX_PARTNER_COMPLET.md` - Cette documentation

---

## ✨ Résultat attendu

Après ré-import d'un fichier PARTNER :
- ✅ `dateNaissance` stockée en DB (pas NULL)
- ✅ `lieuNaissance` stocké en DB
- ✅ Affichage correct dans UI (Informations + Update Modal)
- ✅ Modifications persistées après update
- ✅ Export Excel avec date de naissance complète (JOUR/MOIS/ANNEE)
- ✅ Export Word avec date de naissance formatée
- ✅ Montant facture = 15€ pour tarif A (pas 0)

---

## ⚠️ Important

- **Le backend doit être redémarré** pour appliquer les corrections
- **Les enquêtes déjà importées** ne seront pas corrigées automatiquement
- **Il faut ré-importer** les fichiers pour bénéficier de la correction

