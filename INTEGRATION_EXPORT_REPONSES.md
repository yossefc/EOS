# GUIDE D'INTÉGRATION - Export "Réponses EOS"

## 🎯 Objectif

Remplacer l'export actuel par le format "Réponses EOS" (2618 chars) dans `backend/routes/export.py`.

---

## 📋 MODIFICATIONS À APPLIQUER

### 1. Import de la nouvelle fonction

**Fichier :** `backend/routes/export.py`

**Ajouter en haut du fichier :**
```python
# Import du nouveau format "Réponses EOS"
from routes.export_eos_reponses import generate_eos_reponses_line, debug_parse_line
```

---

### 2. Modifier create_export_batch() - Requête SQL

**AVANT (2 tables) :**
```python
# Récupérer les enquêtes validées (avec limite)
donnees = Donnee.query.filter_by(statut_validation='validee')\
                      .order_by(Donnee.created_at.asc())\
                      .limit(MAX_EXPORT_EOS_LIMIT).all()
```

**APRÈS (3 tables avec JOIN) :**
```python
# Import du modèle EnqueteFacturation
from models.enquete_facturation import EnqueteFacturation

# Récupérer les enquêtes validées avec JOIN facturation (3 tables)
donnees_with_facturation = db.session.query(
    Donnee, DonneeEnqueteur, EnqueteFacturation
).join(
    DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
).outerjoin(  # LEFT JOIN car facturation peut être absente
    EnqueteFacturation, DonneeEnqueteur.id == EnqueteFacturation.donnee_enqueteur_id
).filter(
    Donnee.statut_validation == 'validee'
).order_by(
    Donnee.created_at.asc()
).limit(MAX_EXPORT_EOS_LIMIT).all()
```

---

### 3. Modifier create_export_batch() - Génération lignes

**AVANT (boucle simple) :**
```python
# Générer le contenu du fichier au format EOS
lines = []
skipped_count = 0
for donnee in donnees:
    # Récupérer les données enquêteur
    donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
    if not donnee_enqueteur:
        logger.warning(f"Pas de données enquêteur pour l'enquête {donnee.id}, ignorée")
        skipped_count += 1
        continue

    # Récupérer l'enquêteur
    enqueteur = None
    if donnee.enqueteurId:
        enqueteur = db.session.get(Enqueteur, donnee.enqueteurId)

    # Générer la ligne au format EOS
    line = generate_eos_export_line(donnee, donnee_enqueteur, enqueteur)

    # Ignorer les lignes avec champs obligatoires manquants
    if line is None:
        skipped_count += 1
        continue

    lines.append(line)
```

**APRÈS (utilise query JOIN + nouvelle fonction) :**
```python
# Générer le contenu du fichier au format "Réponses EOS"
lines = []
skipped_count = 0

for donnee, donnee_enqueteur, facturation in donnees_with_facturation:
    # Note: donnee_enqueteur est toujours présent (JOIN)
    # facturation peut être None (OUTER JOIN)

    # Générer la ligne au format "Réponses EOS" (2618 chars)
    line = generate_eos_reponses_line(donnee, donnee_enqueteur, facturation)

    # Ignorer les lignes avec champs obligatoires manquants
    if line is None:
        skipped_count += 1
        continue

    # Vérification longueur (sécurité supplémentaire)
    line_data = line.rstrip('\r\n')
    if len(line_data) != 2618:
        logger.error(f"ERREUR LONGUEUR: enquête ID={donnee.id}, attendu 2618, obtenu {len(line_data)}")
        skipped_count += 1
        continue

    lines.append(line)
```

---

### 4. Vérifier écriture fichier (CRITIQUE)

**AVANT (potentiellement incorrect) :**
```python
with open(filepath_full, 'w', encoding='cp1252', newline='', errors='replace') as f:
    f.writelines(lines)
```

**APRÈS (identique mais vérifié) :**
```python
# IMPORTANT: newline='' pour contrôler CRLF manuellement
# Les lignes contiennent déjà \r\n, pas de conversion automatique
with open(filepath_full, 'w', encoding='cp1252', newline='', errors='replace') as f:
    f.writelines(lines)  # Ecriture exacte (CRLF préservé)
```

✅ **C'est déjà correct !** Le paramètre `newline=''` est présent.

---

## 🔧 PATCH COMPLET À APPLIQUER

**Fichier :** `backend/routes/export.py`

### Modifications ligne par ligne :

1. **Ligne ~10 (imports) - Ajouter :**
```python
from routes.export_eos_reponses import generate_eos_reponses_line, debug_parse_line
```

2. **Ligne ~1420 (import modèle) - Ajouter :**
```python
from models.enquete_facturation import EnqueteFacturation
```

3. **Lignes ~1442-1445 - Remplacer query :**
```python
# ANCIEN CODE (à supprimer):
# donnees = Donnee.query.filter_by(statut_validation='validee')\
#                       .order_by(Donnee.created_at.asc())\
#                       .limit(MAX_EXPORT_EOS_LIMIT).all()

# NOUVEAU CODE:
donnees_with_facturation = db.session.query(
    Donnee, DonneeEnqueteur, EnqueteFacturation
).join(
    DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
).outerjoin(
    EnqueteFacturation, DonneeEnqueteur.id == EnqueteFacturation.donnee_enqueteur_id
).filter(
    Donnee.statut_validation == 'validee'
).order_by(
    Donnee.created_at.asc()
).limit(MAX_EXPORT_EOS_LIMIT).all()
```

4. **Lignes ~1447-1450 - Adapter vérification vide :**
```python
if not donnees_with_facturation:
    return jsonify({
        'success': False,
        'error': 'Aucune enquête validée à exporter'
    }), 404
```

5. **Lignes ~1453 - Adapter log :**
```python
logger.info(f"Création d'un export EOS 'Réponses' de {len(donnees_with_facturation)} enquêtes sur {total_count} validée(s) par {utilisateur}")
```

6. **Lignes ~1465-1489 - Remplacer boucle complète :**
```python
# ANCIEN CODE (à supprimer complètement):
# for donnee in donnees:
#     donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
#     ...

# NOUVEAU CODE:
# Générer le contenu du fichier au format "Réponses EOS"
lines = []
skipped_count = 0

for donnee, donnee_enqueteur, facturation in donnees_with_facturation:
    # Générer la ligne au format "Réponses EOS" (2618 chars)
    line = generate_eos_reponses_line(donnee, donnee_enqueteur, facturation)

    # Ignorer les lignes avec champs obligatoires manquants
    if line is None:
        skipped_count += 1
        continue

    # Vérification longueur (sécurité supplémentaire)
    line_data = line.rstrip('\r\n')
    if len(line_data) != 2618:
        logger.error(f"ERREUR LONGUEUR: enquête ID={donnee.id}, attendu 2618, obtenu {len(line_data)}")
        skipped_count += 1
        continue

    lines.append(line)
```

7. **Lignes ~1504-1512 - Adapter extraction enquete_ids :**
```python
# ANCIEN CODE:
# enquete_ids = [d.id for d in donnees if DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()]

# NOUVEAU CODE:
enquete_ids = [d.id for d, e, f in donnees_with_facturation if e]
```

8. **Lignes ~1524-1532 - Adapter marquage archivées :**
```python
# ANCIEN CODE:
# for donnee in donnees:
#     if DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first():
#         donnee.statut_validation = 'archivee'
#         ...

# NOUVEAU CODE:
for donnee, donnee_enqueteur, facturation in donnees_with_facturation:
    if donnee_enqueteur:  # Enquêteur présent (toujours le cas avec JOIN)
        donnee.statut_validation = 'archivee'
        donnee.add_to_history(
            'archivage',
            f'Enquête exportée au format EOS Réponses (2618 chars) dans {filename} par {utilisateur}',
            utilisateur
        )
```

---

## 🧪 TESTS POST-MIGRATION

### Test 1 : Vérifier longueur des lignes

```python
# Script test_longueur.py
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else 'backend/exports/batches/XXXExp_20251229.txt'

with open(filepath, 'r', encoding='cp1252') as f:
    for i, line in enumerate(f, 1):
        length_with_crlf = len(line)
        length_without_crlf = len(line.rstrip('\r\n'))

        if length_without_crlf != 2618:
            print(f'❌ Ligne {i}: {length_without_crlf} chars (attendu 2618)')
        elif not line.endswith('\r\n'):
            print(f'❌ Ligne {i}: pas de CRLF')
        else:
            print(f'✅ Ligne {i}: OK (2618 chars + CRLF)')
```

**Exécution :**
```bash
python test_longueur.py backend/exports/batches/XXXExp_20251229.txt
```

### Test 2 : Vérifier CRLF

```bash
file backend/exports/batches/XXXExp_*.txt
# Devrait afficher : "... with CRLF line terminators"

# Sous Linux/Mac, utiliser:
od -c backend/exports/batches/XXXExp_*.txt | head -50
# Chercher \r \n à la fin des lignes
```

### Test 3 : Debug parsing d'une ligne

```python
# Script test_parse.py
from routes.export_eos_reponses import debug_parse_line

with open('backend/exports/batches/XXXExp_20251229.txt', 'r', encoding='cp1252') as f:
    first_line = f.readline()

# Afficher tous les champs
parsed = debug_parse_line(first_line)

# Vérifier quelques champs clés
print(f"\nVérifications:")
print(f"- N° dossier: '{parsed['numeroDossier'].strip()}'")
print(f"- Type demande: '{parsed['typeDemande'].strip()}'")
print(f"- Code résultat: '{parsed['codeResultat'].strip()}'")
print(f"- Montant facture: '{parsed['montantFacture'].strip()}'")
```

### Test 4 : Tests pytest complets

```bash
cd backend
python -m pytest test_export_eos_reponses.py -v
```

**Résultat attendu :**
```
test_export_eos_reponses.py::TestFormatHelpers::test_format_alphanum_normal PASSED
test_export_eos_reponses.py::TestFormatHelpers::test_format_alphanum_trop_long PASSED
...
test_export_eos_reponses.py::TestExempleReel::test_exemple_complet_con PASSED

======================= 13 passed in 0.5s =======================
```

---

## ⚠️ POINTS D'ATTENTION

### 1. Modèle EnqueteFacturation doit exister

**Vérifier :**
```python
# backend/models/enquete_facturation.py
from extensions import db

class EnqueteFacturation(db.Model):
    __tablename__ = 'enquete_facturation'

    id = db.Column(db.Integer, primary_key=True)
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id'))
    donnee_enqueteur_id = db.Column(db.Integer, db.ForeignKey('donnees_enqueteur.id'))

    tarif_eos_code = db.Column(db.String(16))
    tarif_eos_montant = db.Column(db.Numeric(8, 2))
    resultat_eos_montant = db.Column(db.Numeric(8, 2))

    tarif_enqueteur_code = db.Column(db.String(16))
    tarif_enqueteur_montant = db.Column(db.Numeric(8, 2))
    resultat_enqueteur_montant = db.Column(db.Numeric(8, 2))

    # ... autres champs
```

**Si inexistant :** créer le modèle et migration Alembic.

### 2. Champs corrections état civil dans DonneeEnqueteur

**Vérifier que ces colonnes existent :**
- qualite_corrigee
- nom_corrige
- prenom_corrige
- code_postal_naissance_corrige
- pays_naissance_corrige
- nom_patronymique_corrige

**Si manquantes :** ajouter migration Alembic.

### 3. Colonnes revenus et mémos dans DonneeEnqueteur

**Vérifier existence :**
- commentaires_revenus
- montant_salaire, periode_versement_salaire, frequence_versement_salaire
- nature_revenu1-3, montant_revenu1-3, periode_versement_revenu1-3, frequence_versement_revenu1-3
- memo1, memo2, memo3, memo4, memo5

**Si manquantes :** ajouter migration Alembic.

---

## 🚀 DÉPLOIEMENT

### Étape 1 : Backup DB
```bash
pg_dump eos_db > backup_avant_migration_export.sql
```

### Étape 2 : Appliquer migrations si nécessaire
```bash
cd backend
flask db upgrade
```

### Étape 3 : Redémarrer backend
```bash
.\REDEMARRER_BACKEND.bat
```

### Étape 4 : Tester export
```bash
curl -X POST http://localhost:5000/api/exports/create-batch \
  -H "Content-Type: application/json" \
  -d '{"utilisateur": "Admin Test"}'
```

### Étape 5 : Valider fichier généré
```bash
# Vérifier longueur
python test_longueur.py backend/exports/batches/XXXExp_*.txt

# Vérifier CRLF
file backend/exports/batches/XXXExp_*.txt

# Parser première ligne
python test_parse.py
```

---

## 📞 TROUBLESHOOTING

### Erreur : "cannot import name 'EnqueteFacturation'"

**Solution :** Créer le modèle EnqueteFacturation ou ajuster l'import.

### Erreur : "column e.qualite_corrigee does not exist"

**Solution :** Ajouter migration Alembic pour colonnes corrections état civil.

### Erreur : "ERREUR LONGUEUR: attendu 2618, obtenu XXXX"

**Solution :** Vérifier EOS_REPONSES_FIELD_SPECS (somme des largeurs doit faire 2618).

### Lignes générées avec LF au lieu de CRLF

**Solution :** Vérifier paramètre `newline=''` dans `open()`.

---

**Date** : 2025-12-29
**Version** : 1.0
**Statut** : Prêt pour intégration
