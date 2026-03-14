# 📦 GUIDE : Transfert des données PARTNER entre deux ordinateurs

## 🎯 Objectif

Copier toutes les configurations PARTNER (tarifs, options, règles) d'un ordinateur à l'autre sans avoir à les reconfigurer manuellement.

---

## 📋 Données transférées

1. **Tarifs PARTNER** (`tarifs_client`)
   - Codes lettres (A, B, C, D, E, T, etc.)
   - Descriptions
   - Montants

2. **Options de confirmation** (`confirmation_options`)
   - Confirmé par email
   - Confirmé par téléphone
   - Confirmé sur place
   - Non confirmé

3. **Règles tarifaires** (`partner_tarif_rules`)
   - Règles de calcul automatique des tarifs

---

## 🚀 PROCÉDURE COMPLÈTE

### Sur CET ordinateur (SOURCE) :

#### Étape 1 : Exporter les données

```bash
cd D:\EOS
./EXPORTER_DONNEES_PARTNER.bat
```

**Résultat** : 3 fichiers SQL créés dans `D:\EOS\` :
- `PARTNER_TARIFS_EXPORT.sql`
- `PARTNER_CONFIRMATION_EXPORT.sql`
- `PARTNER_TARIF_RULES_EXPORT.sql`

#### Étape 2 : Copier les fichiers

Copiez ces 3 fichiers sur **clé USB** ou **réseau partagé**

---

### Sur l'AUTRE ordinateur (CIBLE) :

#### Étape 1 : Récupérer les fichiers

Copiez les 3 fichiers SQL dans `D:\eos\`

#### Étape 2 : Importer les données

```bash
cd /d/eos
./IMPORTER_DONNEES_PARTNER.bat
```

Le script va :
1. Vérifier que les 3 fichiers existent
2. Supprimer les anciennes données PARTNER
3. Importer les nouvelles données
4. Confirmer le succès

#### Étape 3 : Redémarrer l'application

```bash
./DEMARRER_EOS_SIMPLE.bat
```

---

## ✅ Vérification

Après l'import, vérifiez que tout est OK :

### Dans psql :

```sql
-- Connectez-vous
psql -U postgres -d eos_db

-- Vérifiez les tarifs
SELECT code_lettre, description, montant 
FROM tarifs_client tc 
JOIN clients c ON tc.client_id = c.id 
WHERE c.code = 'PARTNER';

-- Vérifiez les options
SELECT option_text 
FROM confirmation_options co 
JOIN clients c ON co.client_id = c.id 
WHERE c.code = 'PARTNER';

-- Quitter
\q
```

Vous devriez voir les mêmes données que sur l'ordinateur SOURCE.

---

## 🔧 Avantages de cette méthode

✅ **Rapide** : Quelques secondes vs reconfiguration manuelle  
✅ **Fiable** : Pas de risque d'oublier des données  
✅ **Reproductible** : Peut être refait à tout moment  
✅ **Sûr** : Supprime les anciennes données avant d'importer  

---

## ⚠️ Notes importantes

1. **Les fichiers SQL sont spécifiques au client PARTNER**
   - Ne touche pas aux données EOS
   - Ne touche pas aux dossiers/enquêtes

2. **L'import REMPLACE les données existantes**
   - Les anciens tarifs PARTNER seront supprimés
   - Les nouvelles données seront insérées

3. **Les dossiers ne sont PAS transférés**
   - Seules les configurations sont copiées
   - Les dossiers restent dans chaque base de données

---

## 📁 Fichiers créés

**Scripts d'export/import :**
- `EXPORTER_DONNEES_PARTNER.bat` : Export sur ordinateur SOURCE
- `EXPORTER_DONNEES_PARTNER.sql` : Script SQL d'export
- `IMPORTER_DONNEES_PARTNER.bat` : Import sur ordinateur CIBLE

**Fichiers de données (générés par l'export) :**
- `PARTNER_TARIFS_EXPORT.sql`
- `PARTNER_CONFIRMATION_EXPORT.sql`
- `PARTNER_TARIF_RULES_EXPORT.sql`

---

## 🆘 En cas de problème

### Erreur "Fichier introuvable"
→ Vérifiez que vous avez bien copié les 3 fichiers SQL

### Erreur de permissions
→ Exécutez d'abord `CORRIGER_PERMISSIONS.bat`

### Données non visibles après import
→ Redémarrez le backend (`DEMARRER_EOS_SIMPLE.bat`)

---

**Date de création** : 31 décembre 2025

