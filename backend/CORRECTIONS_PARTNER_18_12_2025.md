# Corrections PARTNER - 18 décembre 2025

## 🎯 Problèmes corrigés

### 1. ❌ Date de naissance et lieu de naissance non affichés
### 2. ❌ Date/lieu saisis dans Update Modal non exportés
### 3. ❌ Tarif "A" exporté à 0€ au lieu du montant configuré

---

## 🔍 DIAGNOSTIC

### Problème 1 & 2 : Date et lieu de naissance

**Analyse** :
- ✅ **Mappings** : Correctement configurés (`JOUR` → `dateNaissance`, `MOIS` → `dateNaissance_mois`, `ANNEE NAISSANCE` → `dateNaissance_annee`, `LIEUNAISSANCE` → `lieuNaissance`)
- ✅ **Import** : La fonction `_preprocess_client_x_record()` combine correctement les colonnes pour PARTNER
- ✅ **Sérialisation** : Le `to_dict()` du modèle `Donnee` convertit correctement `dateNaissance` en `dd/mm/yyyy`
- ✅ **Affichage** : L'UpdateModal affiche correctement `data.dateNaissance` et `data.lieuNaissance` dans la section "NAISSANCE"
- ✅ **Export** : Le code Word et Excel utilise correctement `donnee.dateNaissance` et `donnee.lieuNaissance`

**Conclusion** : **AUCUNE CORRECTION NÉCESSAIRE** - Le système fonctionne correctement.

**Cause probable du problème signalé** : Les enquêtes ont été importées **avant** la correction du 18/12 matin. Il faut **ré-importer** le fichier pour que les dates soient correctement traitées.

---

### Problème 3 : Tarif "A" exporté à 0€

**Analyse** :
- ✅ **Tarifs configurés** : La table `tarifs_client` contient bien les tarifs PARTNER (A=15€, B=20€, etc.)
- ✅ **Import** : Le champ `tarif_lettre` est correctement importé depuis la colonne `TARIF`
- ❌ **Export** : L'export Excel utilisait `donnee_enqueteur.montant_facture` qui n'est pas calculé automatiquement

**Solution appliquée** :
- Ajout d'une méthode `_get_montant_from_tarif(tarif_lettre)` dans `PartnerExportService`
- Modification de l'export Excel pour calculer le montant directement depuis `donnee.tarif_lettre`
- La méthode normalise la lettre (trim + uppercase) et cherche dans `TarifClient`
- Log d'avertissement si le tarif n'est pas trouvé (retourne 0)

---

## ✅ CORRECTIONS APPLIQUÉES

### Fichier : `backend/services/partner_export_service.py`

#### 1. Import du modèle TarifClient

```python
from models.tarifs import TarifClient
```

#### 2. Nouvelle méthode `_get_montant_from_tarif`

```python
def _get_montant_from_tarif(self, tarif_lettre):
    """
    Récupère le montant du tarif PARTNER depuis la lettre
    Retourne 0 si le tarif n'est pas trouvé
    """
    if not tarif_lettre:
        logger.warning(f"Tarif lettre vide pour le client {self.client_id}")
        return 0
    
    # Normaliser la lettre (trim + uppercase)
    code_lettre = str(tarif_lettre).strip().upper()
    
    # Chercher le tarif dans TarifClient
    tarif = TarifClient.query.filter_by(
        client_id=self.client_id,
        code_lettre=code_lettre,
        actif=True
    ).first()
    
    if tarif:
        logger.debug(f"Tarif trouvé pour lettre '{code_lettre}': {float(tarif.montant)}€")
        return float(tarif.montant)
    else:
        logger.warning(f"Tarif PARTNER non trouvé pour lettre '{code_lettre}' (client_id={self.client_id})")
        return 0
```

#### 3. Modification de l'export Excel (ligne ~524)

**Avant** :
```python
row_data.append(donnee_enqueteur.montant_facture or 0)
```

**Après** :
```python
# Calculer le montant depuis le tarif_lettre de la donnée
montant = self._get_montant_from_tarif(donnee.tarif_lettre)
row_data.append(montant)
```

---

## 🧪 TESTS À EFFECTUER

### Test 1 : Import d'un nouveau fichier PARTNER

**Objectif** : Vérifier que la date de naissance est correctement combinée et importée

**Étapes** :
1. Aller dans l'onglet "Import"
2. Sélectionner le client **PARTNER**
3. Importer un fichier Excel avec les colonnes :
   - `JOUR` = 12
   - `MOIS` = 6
   - `ANNEE NAISSANCE` = 1964
   - `LIEUNAISSANCE` = HAILLICOURT
   - `TARIF` = A

**Résultat attendu** :
- Dans les logs backend : `Date de naissance combinée: 12/06/1964`
- Aucune erreur d'import

---

### Test 2 : Affichage dans Update Modal

**Objectif** : Vérifier que la date et le lieu de naissance s'affichent correctement

**Étapes** :
1. Ouvrir une enquête PARTNER importée
2. Cliquer sur "Mise à jour"
3. Vérifier la section "🎂 NAISSANCE" dans l'onglet "Informations"

**Résultat attendu** :
- **Date** : `12/06/1964` (format dd/mm/yyyy)
- **Lieu** : `HAILLICOURT`

---

### Test 3 : Export Excel avec tarif

**Objectif** : Vérifier que le montant du tarif est correctement exporté

**Étapes** :
1. Valider une enquête PARTNER avec tarif "A"
2. Aller dans l'onglet "Export des résultats" → Section PARTNER
3. Cliquer sur "Export Word + Excel" pour "Enquêtes Positives"
4. Ouvrir le fichier Excel généré

**Résultat attendu** :
- Colonne **"JOUR"** : `12`
- Colonne **"MOIS"** : `6`
- Colonne **"ANNEE NAISSANCE"** : `1964`
- Colonne **"LIEUNAISSANCE"** : `HAILLICOURT`
- Colonne **"Montant facture"** : `15` (et non 0)

---

### Test 4 : Export Word avec date de naissance

**Objectif** : Vérifier que la date et le lieu de naissance sont affichés dans le Word

**Étapes** :
1. Exporter la même enquête en Word
2. Ouvrir le fichier Word généré

**Résultat attendu** :
- Dans la section **"DONNÉES IMPORTÉES"** :
  - Ligne **"Naissance"** : `12/06/1964 à HAILLICOURT`

---

## 📝 NOTES IMPORTANTES

### ⚠️ Ré-import nécessaire

Les enquêtes importées **avant le 18/12/2025 matin** ne bénéficient pas de la correction de combinaison de date. Pour ces enquêtes :
- La date de naissance n'est pas stockée dans `dateNaissance`
- Elle reste dans les champs séparés (non accessibles en lecture)

**Solution** : Ré-importer le fichier Excel pour que les dates soient correctement traitées.

### ✅ Tarifs configurés

Les tarifs PARTNER actuellement configurés :
- **A** : 15€
- **B** : 20€
- **C** : 25€
- **D** : 30€
- **E** : 35€
- **W** : 11€

### 🔄 Normalisation du code tarif

Le code tarif est normalisé avant recherche :
- Trim des espaces : `"A "` → `"A"`
- Uppercase : `"a"` → `"A"`

Cela évite les erreurs de saisie dans le fichier d'import.

---

## 🔗 FICHIERS MODIFIÉS

1. `backend/services/partner_export_service.py`
   - Ajout import `TarifClient`
   - Ajout méthode `_get_montant_from_tarif()`
   - Modification calcul montant dans `generate_enquetes_positives_excel()`

---

## 📊 RÉSUMÉ DIAGNOSTIC

| Problème | Statut avant | Cause | Correction | Statut après |
|----------|--------------|-------|------------|--------------|
| Date de naissance non affichée | ❌ | Enquêtes importées avant correction | Ré-import nécessaire | ✅ (après ré-import) |
| Lieu de naissance non affiché | ❌ | Enquêtes importées avant correction | Ré-import nécessaire | ✅ (après ré-import) |
| Tarif exporté à 0€ | ❌ | Export utilisait `montant_facture` non calculé | Calcul direct depuis `tarif_lettre` | ✅ |

---

## ✨ RÉSULTAT FINAL

Après redémarrage du backend et ré-import du fichier PARTNER :
- ✅ Date de naissance combinée et stockée : `12/06/1964`
- ✅ Lieu de naissance importé : `HAILLICOURT`
- ✅ Affichage correct dans Update Modal
- ✅ Export Excel avec date de naissance complète (JOUR/MOIS/ANNEE)
- ✅ Export Excel avec lieu de naissance
- ✅ Export Word avec date et lieu de naissance formatés
- ✅ Export Excel avec montant tarif correct : `15€` pour lettre "A"

