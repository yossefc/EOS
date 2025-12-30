# REFONTE EXPORT EOS - FORMAT "RÉPONSES" (Fixed-Width 2618 chars)

## 🎯 OBJECTIF

Remplacer l'export actuel (format "Demandes" 1854 chars) par le format **"Réponses EOS"** (2618 chars) conforme au cahier des charges du retour prestataire.

---

## 📊 ANALYSE DES ÉCARTS

### Format actuel (INCORRECT) - "Demandes"

**Fichier :** `backend/routes/export.py` fonction `generate_eos_export_line()`

**Problèmes identifiés :**

1. **Longueur incorrecte** : ~1854 caractères au lieu de 2618
2. **Champs du format "Demandes" inclus à tort** :
   - `elementDemandes` (10)
   - `elementObligatoires` (10)
   - `elementContestes` (10)
   - `codeMotif` (16)
   - `motifDeContestation` (64)
   - `codesociete` (2)
   - `urgence` (1)
   - `commentaire` (1000)
   - `datedenvoie` (10)

3. **Champs manquants du format "Réponses"** :
   - Corrections état civil prioritaires (qualite_corrigee, nom_corrige, etc.)
   - Facturation depuis table `enquete_facturation` (JOIN manquant)
   - **Revenus** (376 chars) :
     - commentaires_revenus (128)
     - montant_salaire (8)
     - periode_versement_salaire (3)
     - frequence_versement_salaire (2)
     - revenus 1-3 (nature, montant, période, fréquence)
   - **Mémos** (1128 chars) :
     - memo1-4 (64 chacun)
     - memo5 (1000)

4. **Source de données** :
   - Actuel : 2 tables (donnees, donnees_enqueteur)
   - Requis : 3 tables avec JOIN (donnees, donnees_enqueteur, **enquete_facturation**)

---

## 🏗️ NOUVELLE ARCHITECTURE (Spec-Driven)

### Fichier : `backend/routes/export_eos_reponses.py`

**Approche :**
- **Spec-driven** : liste `EOS_REPONSES_FIELD_SPECS` définit tous les champs
- **Helpers de formatage** : `format_alphanum()`, `format_numeric()`, `format_date()`, `format_amount()`
- **Validation stricte** : longueur 2618 chars exactement
- **Debug helper** : `debug_parse_line()` pour vérification manuelle

### Structure EOS_REPONSES_FIELD_SPECS

```python
# Format: (nom_champ, largeur, type, source_expr, commentaire)
EOS_REPONSES_FIELD_SPECS = [
    ('numeroDossier', 10, 'alpha', 'd.numeroDossier', 'N° dossier EOS'),
    ('referenceDossier', 15, 'alpha', 'd.referenceDossier', 'Référence'),
    # ... (73 champs au total)
]
```

**Avantages :**
- ✅ Facile à maintenir (ajouter/modifier champs)
- ✅ Auto-documentation (nom + largeur + source visible)
- ✅ Validation automatique longueur
- ✅ Traçabilité (source_expr explicite)

---

## 🔄 MAPPING DES CHAMPS

### A. Identifiants (135 chars) - Source: `donnees` (d)

| Champ | Largeur | Source | Commentaire |
|-------|---------|--------|-------------|
| numeroDossier | 10 | d.numeroDossier | Celui transmis par EOS |
| referenceDossier | 15 | d.referenceDossier | Référence EOS |
| numeroInterlocuteur | 12 | d.numeroInterlocuteur | N° interlocuteur EOS |
| guidInterlocuteur | 36 | d.guidInterlocuteur | GUID EOS |
| typeDemande | 3 | d.typeDemande | ENQ ou CON |
| numeroDemande | 11 | d.numeroDemande | N° demande EOS |
| numeroDemandeContestee | 11 | `d.numeroDemandeContestee if CON else ""` | Si contestation |
| numeroDemandeInitiale | 11 | `d.numeroDemandeInitiale if CON else ""` | Si contestation |
| forfaitDemande | 16 | d.forfaitDemande | Forfait EOS |
| dateRetourEspere | 10 | d.dateRetourEspere | Date retour espéré |

### B. État civil (192 chars) - Source: **Priorité corrections `e.*_corrige`, sinon `d.*`**

| Champ | Largeur | Source | Priorité |
|-------|---------|--------|----------|
| qualite | 10 | `e.qualite_corrigee or d.qualite` | Correction prioritaire |
| nom | 30 | `e.nom_corrige or d.nom` | Correction prioritaire |
| prenom | 20 | `e.prenom_corrige or d.prenom` | Correction prioritaire |
| dateNaissance | 10 | d.dateNaissance | Toujours d |
| lieuNaissance | 50 | d.lieuNaissance | Toujours d |
| codePostalNaissance | 10 | `e.code_postal_naissance_corrige or d.codePostalNaissance` | Correction prioritaire |
| paysNaissance | 32 | `e.pays_naissance_corrige or d.paysNaissance` | Correction prioritaire |
| nomPatronymique | 30 | `e.nom_patronymique_corrige or d.nomPatronymique` | Correction prioritaire |

### C. Résultat (22 chars) - Source: `donnees_enqueteur` (e)

| Champ | Largeur | Source | Commentaire |
|-------|---------|--------|-------------|
| dateRetour | 10 | `e.date_retour or today()` | Date retour (défaut aujourd'hui) |
| codeResultat | 1 | e.code_resultat | P/N/H/Z/I/Y |
| elementsRetrouves | 10 | e.elements_retrouves | A/T/B/E/R/D |
| flagEtatCivilErrone | 1 | e.flag_etat_civil_errone | E ou vide |

### D. Facturation (59 chars) - Source: **Priorité `e`, sinon `f`**

| Champ | Largeur | Source | Priorité |
|-------|---------|--------|----------|
| numeroFacture | 9 | e.numero_facture | |
| dateFacture | 10 | e.date_facture | |
| montantFacture | 8 | `e.montant_facture or f.resultat_eos_montant` | **Priorité e, sinon f** |
| tarifApplique | 8 | `e.tarif_applique or f.tarif_eos_montant` | **Priorité e, sinon f** |
| cumulMontantsPrecedents | 8 | `e.cumul_montants_precedents or d.cumulMontantsPrecedents` | |
| repriseFacturation | 8 | e.reprise_facturation | |
| remiseEventuelle | 8 | e.remise_eventuelle | |

### E-H. Décès, Adresse, Téléphones, Employeur (593 chars)

Source : `donnees_enqueteur` (e)

### I. Banque (117 chars) - **IMPORTANT : numeroCompte et RIB TOUJOURS VIDES**

| Champ | Largeur | Source | Commentaire |
|-------|---------|--------|-------------|
| banqueDomiciliation | 32 | e.banque_domiciliation | |
| libelleGuichet | 30 | e.libelle_guichet | |
| titulaireCompte | 32 | e.titulaire_compte | |
| codeBanque | 5 | e.code_banque | |
| codeGuichet | 5 | e.code_guichet | |
| **numeroCompte** | 11 | `""` | **TOUJOURS VIDE (espaces)** |
| **ribCompte** | 2 | `""` | **TOUJOURS VIDE (espaces)** |

### J. Revenus (376 chars) - Source: `donnees_enqueteur` (e)

**NOUVEAUX CHAMPS (absents de l'ancien format) :**

| Champ | Largeur | Source |
|-------|---------|--------|
| commentairesRevenus | 128 | e.commentaires_revenus |
| montantSalaire | 8 | e.montant_salaire |
| periodeVersementSalaire | 3 | e.periode_versement_salaire |
| frequenceVersementSalaire | 2 | e.frequence_versement_salaire |
| **Revenus 1-3** | 45×3 | e.nature_revenu1, e.montant_revenu1, ... |

### K. Mémos (1128 chars) - Source: `donnees_enqueteur` (e)

**NOUVEAUX CHAMPS (absents de l'ancien format) :**

| Champ | Largeur | Source |
|-------|---------|--------|
| memo1 | 64 | e.memo1 |
| memo2 | 64 | e.memo2 |
| memo3 | 64 | e.memo3 |
| memo4 | 64 | e.memo4 |
| **memo5** | **1000** | e.memo5 |

---

## 🔧 HELPERS DE FORMATAGE

### format_alphanum(value, width)
- Padding à **droite** avec espaces
- Troncature si trop long
- None → espaces

### format_numeric(value, width)
- Padding à **gauche** avec zéros
- Digits only
- None → espaces (pas de zéros)

### format_date(date_value)
- Format `JJ/MM/AAAA` (10 chars)
- None → espaces

### format_amount(montant, width=8)
- Format `99999,99` (virgule, pas point)
- Padding à gauche avec zéros
- Décimales : 2
- None → `0000,00`

---

## 🧪 TESTS PYTEST

### Fichier : `backend/test_export_eos_reponses.py`

**13 tests automatiques :**

1. ✅ Longueur ligne exacte (2618 + CRLF)
2. ✅ Format CRLF en fin de ligne
3. ✅ Champs identifiants exacts (pas d'IDs internes)
4. ✅ TYPE_DEMANDE = ENQ
5. ✅ TYPE_DEMANDE = CON + champs contestation
6. ✅ Corrections état civil prioritaires
7. ✅ Facturation depuis DonneeEnqueteur
8. ✅ Facturation depuis EnqueteFacturation (fallback)
9. ✅ numeroCompte et RIB toujours vides
10. ✅ Champs manquants → None
11. ✅ Revenus présents
12. ✅ Mémos présents
13. ✅ Spec coverage complet

**Lancer les tests :**
```bash
cd backend
python -m pytest test_export_eos_reponses.py -v
```

---

## 🔍 DEBUG HELPER

### Fonction `debug_parse_line(line)`

Permet de visualiser tous les champs d'une ligne exportée :

```python
from routes.export_eos_reponses import debug_parse_line, generate_eos_reponses_line

# Générer une ligne
line = generate_eos_reponses_line(donnee, donnee_enqueteur, facturation)

# Parser et afficher
parsed = debug_parse_line(line)
```

**Affichage :**
```
================================================================================
DEBUG PARSE LIGNE (longueur: 2618)
================================================================================

numeroDossier                  [   0- 10] ( 10) : '0000123456' | N° dossier transmis par EOS
referenceDossier               [  10- 25] ( 15) : 'REF-2025-001   ' | Référence dossier EOS
numeroInterlocuteur            [  25- 37] ( 12) : 'INT-12345678' | N° interlocuteur EOS
...
memo5                          [1618-2618] (1000) : 'Personne très coopérative...' | Mémo 5 (long)

================================================================================
```

---

## 🚀 INTÉGRATION DANS LE SYSTÈME EXISTANT

### Étape 1 : Modifier `create_export_batch()`

**Fichier :** `backend/routes/export.py`

**Changements nécessaires :**

1. **Ajouter JOIN avec enquete_facturation** :
   ```python
   from models.enquete_facturation import EnqueteFacturation

   # Requête avec JOIN
   donnees_with_facturation = db.session.query(
       Donnee, DonneeEnqueteur, EnqueteFacturation
   ).join(
       DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
   ).outerjoin(  # LEFT JOIN car facturation peut être absente
       EnqueteFacturation, DonneeEnqueteur.id == EnqueteFacturation.donnee_enqueteur_id
   ).filter(
       Donnee.statut_validation == 'validee'
   ).all()
   ```

2. **Remplacer l'appel à generate_eos_export_line** :
   ```python
   from routes.export_eos_reponses import generate_eos_reponses_line

   for donnee, donnee_enqueteur, facturation in donnees_with_facturation:
       # Nouvelle fonction format "Réponses"
       line = generate_eos_reponses_line(donnee, donnee_enqueteur, facturation)

       if line is None:
           skipped_count += 1
           continue

       lines.append(line)
   ```

3. **Vérifier écriture fichier avec CRLF** :
   ```python
   # IMPORTANT: newline='' pour contrôler CRLF manuellement
   with open(filepath_full, 'w', encoding='cp1252', newline='', errors='replace') as f:
       f.writelines(lines)  # Les lignes contiennent déjà \r\n
   ```

### Étape 2 : Tester l'intégration

```bash
# 1. Lancer tests unitaires
cd backend
python -m pytest test_export_eos_reponses.py -v

# 2. Générer un export de test
curl -X POST http://localhost:5000/api/exports/create-batch \
  -H "Content-Type: application/json" \
  -d '{"utilisateur": "Admin"}'

# 3. Vérifier le fichier
file backend/exports/batches/XXXExp_*.txt
# Devrait afficher : "CRLF line terminators"

# 4. Vérifier longueur lignes
python -c "
with open('backend/exports/batches/XXXExp_20251229.txt', 'r', encoding='cp1252') as f:
    for i, line in enumerate(f, 1):
        length = len(line.rstrip('\r\n'))
        print(f'Ligne {i}: {length} chars')
        if length != 2618:
            print(f'  ⚠️  ERREUR: attendu 2618')
"
```

---

## ⚠️ POINTS CRITIQUES

### 1. NE PAS strip/rstrip les lignes avant écriture

❌ **INCORRECT :**
```python
line = generate_eos_reponses_line(d, e, f).strip()  # ❌ PERD LES ESPACES
with open(f, 'w') as out:
    out.write(line + '\n')  # ❌ CRLF perdu
```

✅ **CORRECT :**
```python
line = generate_eos_reponses_line(d, e, f)  # Contient déjà \r\n
with open(f, 'w', encoding='cp1252', newline='') as out:
    out.write(line)  # ✅ Ecriture exacte (CRLF préservé)
```

### 2. Paramètre newline='' obligatoire

**Pourquoi ?**
- Par défaut, Python convertit `\n` en `\r\n` sous Windows
- Avec `newline=''`, Python écrit **exactement** ce qu'on lui donne
- Nos lignes contiennent déjà `\r\n` → pas de double conversion

**Source :** [Python open() documentation](https://docs.python.org/3/library/functions.html#open)

### 3. JOIN avec enquete_facturation peut être NULL

Utiliser **LEFT JOIN (outerjoin)** car toutes les enquêtes n'ont pas forcément de facturation :

```python
.outerjoin(EnqueteFacturation, ...)  # Pas .join() !
```

---

## 📈 BÉNÉFICES DE LA REFONTE

| Aspect | Avant (Demandes) | Après (Réponses) |
|--------|------------------|------------------|
| **Longueur** | 1854 chars | 2618 chars ✅ |
| **Format** | Mixte demandes/réponses | Pur réponses ✅ |
| **État civil** | Jamais corrigé | Priorité corrections ✅ |
| **Facturation** | 2 tables | 3 tables (+ enquete_facturation) ✅ |
| **Revenus** | ❌ Absents | ✅ 376 chars |
| **Mémos** | ❌ Absents | ✅ 1128 chars |
| **Maintenabilité** | Hardcodé | Spec-driven ✅ |
| **Tests** | 10 tests partiels | 13 tests complets ✅ |
| **Debug** | Difficile | Helper debug_parse_line ✅ |

---

## 📝 CHECKLIST MIGRATION

- [ ] Créer modèle `EnqueteFacturation` si inexistant
- [ ] Modifier `create_export_batch()` pour JOIN 3 tables
- [ ] Remplacer `generate_eos_export_line()` par `generate_eos_reponses_line()`
- [ ] Vérifier `newline=''` dans l'écriture fichier
- [ ] Lancer tests pytest : `pytest test_export_eos_reponses.py -v`
- [ ] Générer export de test et vérifier longueur lignes (2618)
- [ ] Vérifier CRLF : `file XXXExp_*.txt`
- [ ] Tester avec données réelles (ENQ et CON)
- [ ] Valider avec client EOS

---

## 📞 SUPPORT

En cas de problème :
1. Vérifier logs backend (warnings sur champs manquants)
2. Utiliser `debug_parse_line()` pour inspecter ligne
3. Lancer tests : `pytest test_export_eos_reponses.py -v`
4. Vérifier JOIN avec enquete_facturation (peut être NULL)

---

**Date de création** : 2025-12-29
**Version** : 2.0.0 - Format "Réponses EOS" conforme
**Auteur** : Claude Code (Senior Backend Engineer)
