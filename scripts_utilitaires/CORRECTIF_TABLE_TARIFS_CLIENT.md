# 🔧 CORRECTIF : Table tarifs_client manquante

## ❌ Problème

Lors de l'utilisation des exports PARTNER, l'erreur suivante se produit :

```
psycopg2.errors.UndefinedTable: ERREUR: la relation « tarifs_client » n'existe pas
```

**Cause** : La table `tarifs_client` n'a jamais été créée par une migration Alembic, bien que le modèle Python existe dans `backend/models/tarifs.py`.

---

## ✅ Solution

Créer une nouvelle migration (008) pour créer la table `tarifs_client` et insérer les tarifs PARTNER par défaut.

---

## 📋 Instructions (AUTRE ORDINATEUR)

### Étape 1️⃣ : Récupérer la nouvelle migration

```bash
cd /d/eos
git pull origin master
```

### Étape 2️⃣ : Appliquer la migration et configurer les tarifs

**Exécutez le script automatique :**

```bash
./CONFIGURER_TARIFS_PARTNER.bat
```

Ce script va :
1. Appliquer la migration 008 pour créer la table `tarifs_client`
2. Insérer les tarifs PARTNER par défaut (A, B, C, D, E, T)
3. Afficher les tarifs insérés

### Étape 3️⃣ : Ajuster les tarifs (IMPORTANT)

Les montants insérés sont des **EXEMPLES** :
- Tarif A : 50.00 €
- Tarif B : 75.00 €  
- Tarif C : 100.00 €
- Tarif D : 120.00 €
- Tarif E : 90.00 €
- Tarif T : 60.00 €

**Modifiez le fichier `INSERER_TARIFS_PARTNER.sql`** pour mettre vos tarifs réels, puis réexécutez :

```bash
psql -U postgres -d eos_db -f INSERER_TARIFS_PARTNER.sql
```

### Étape 4️⃣ : Redémarrer l'application

```bash
./DEMARRER_EOS_SIMPLE.bat
```

---

## 🔍 Vérification manuelle (optionnelle)

Pour vérifier que la table existe et contient les tarifs :

```sql
-- Voir la structure de la table
\d tarifs_client

-- Voir les tarifs PARTNER
SELECT tc.code_lettre, tc.description, tc.montant, tc.actif
FROM tarifs_client tc
JOIN clients c ON tc.client_id = c.id
WHERE c.code = 'PARTNER';
```

---

## 📁 Fichiers créés

- `backend/migrations/versions/008_create_tarifs_client.py` : Migration Alembic
- `INSERER_TARIFS_PARTNER.sql` : Script SQL pour insérer les tarifs
- `CONFIGURER_TARIFS_PARTNER.bat` : Script automatique d'installation
- `CORRECTIF_TABLE_TARIFS_CLIENT.md` : Cette documentation

---

## ⚠️ Note importante

Cette table est utilisée par :
- **Exports PARTNER** : Pour calculer les montants des enquêtes
- **Service de tarification** : `PartnerTarifResolver`

Sans cette table, les exports PARTNER ne peuvent pas fonctionner.

---

**Date de création** : 31 décembre 2025  
**Migration concernée** : `008_create_tarifs_client`

