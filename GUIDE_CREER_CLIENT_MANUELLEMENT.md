# 📘 GUIDE : CRÉER UN CLIENT MANUELLEMENT

## 🎯 OBJECTIF

Ce guide explique comment créer un client manuellement dans la base de données **sans avoir à synchroniser** depuis un autre ordinateur.

---

## 🆚 COMPARAISON DES MÉTHODES

| Méthode | Avantages | Inconvénients | Usage |
|---------|-----------|---------------|-------|
| **Synchronisation complète** | Transfère tout (clients, tarifs, mappings) | Nécessite accès aux deux ordinateurs | Première installation |
| **Création manuelle** | Rapide, pas besoin de l'autre PC | Ne transfère pas les tarifs | Ajouter un client simple |

---

## ⚡ MÉTHODE RAPIDE : CRÉER SHERLOCK

Si vous voulez juste ajouter le client Sherlock :

```cmd
cd D:\EOS
.\CREER_CLIENT_SHERLOCK.bat
```

✅ **C'est tout !** Le client Sherlock est créé avec tous ses 70+ mappings.

---

## 🔧 CRÉER UN AUTRE CLIENT MANUELLEMENT

### Étape 1 : Créer le fichier SQL

Créez un fichier `CREER_CLIENT_MONNOM.sql` :

```sql
-- ===================================================================
-- CRÉATION DU CLIENT MON_CLIENT
-- ===================================================================

-- 1. Créer le client
INSERT INTO clients (code, nom, actif, date_creation)
VALUES ('MON_CLIENT', 'Nom du Client', true, NOW())
ON CONFLICT (code) DO UPDATE SET
  nom = EXCLUDED.nom,
  actif = EXCLUDED.actif;

-- 2. Créer le profil d'import
DO $$
DECLARE
    client_id_val INT;
BEGIN
    -- Récupérer l'ID du client
    SELECT id INTO client_id_val FROM clients WHERE code = 'MON_CLIENT';
    
    -- Créer le profil d'import
    INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
    VALUES (client_id_val, 'Mon Client Import', 'EXCEL', 'utf-8', true, NOW())
    ON CONFLICT DO NOTHING;
END $$;

-- 3. Créer les mappings
DO $$
DECLARE
    profile_id_val INT;
BEGIN
    -- Récupérer l'ID du profil
    SELECT ip.id INTO profile_id_val 
    FROM import_profiles ip
    JOIN clients c ON ip.client_id = c.id
    WHERE c.code = 'MON_CLIENT'
    LIMIT 1;
    
    -- Supprimer les anciens mappings
    DELETE FROM import_field_mappings WHERE import_profile_id = profile_id_val;
    
    -- Créer les mappings
    INSERT INTO import_field_mappings (import_profile_id, column_name, internal_field, is_required, strip_whitespace, date_creation)
    VALUES
        -- EXEMPLE : Adapter selon vos colonnes Excel
        (profile_id_val, 'Numéro', 'numeroDossier', true, true, NOW()),
        (profile_id_val, 'Nom', 'nom', true, true, NOW()),
        (profile_id_val, 'Prénom', 'prenom', false, true, NOW()),
        (profile_id_val, 'Adresse', 'adresse1', false, true, NOW()),
        (profile_id_val, 'Code Postal', 'codePostal', false, true, NOW()),
        (profile_id_val, 'Ville', 'ville', false, true, NOW());
    
    RAISE NOTICE 'Mappings créés';
END $$;

-- 4. Vérification
SELECT id, code, nom FROM clients WHERE code = 'MON_CLIENT';
SELECT COUNT(*) AS nb_mappings
FROM import_field_mappings ifm
JOIN import_profiles ip ON ifm.import_profile_id = ip.id
JOIN clients c ON ip.client_id = c.id
WHERE c.code = 'MON_CLIENT';
```

### Étape 2 : Créer le fichier BAT

Créez un fichier `CREER_CLIENT_MONNOM.bat` :

```batch
@echo off
cls
echo ================================================================
echo     CREATION DU CLIENT MON_CLIENT
echo ================================================================
echo.
pause

cd /d D:\EOS
psql -U postgres -d eos_db -f CREER_CLIENT_MONNOM.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de la creation
    pause
    exit /b 1
)

echo.
echo ✅ Client cree avec succes !
echo.
pause
```

### Étape 3 : Exécuter

```cmd
.\CREER_CLIENT_MONNOM.bat
```

---

## 📊 STRUCTURE DES MAPPINGS

### Colonnes Excel → Champs internes

Voici les champs internes disponibles pour les mappings :

#### **Champs principaux (table `donnees`)**

| Colonne Excel (exemple) | Champ interne | Obligatoire | Description |
|-------------------------|---------------|-------------|-------------|
| Numéro / NUM | `numeroDossier` | ✅ Oui | Numéro unique du dossier |
| Nom | `nom` | ✅ Oui | Nom de famille |
| Prénom | `prenom` | ❌ Non | Prénom |
| Date Naissance | `dateNaissance` | ❌ Non | Date de naissance |
| Lieu Naissance | `lieuNaissance` | ❌ Non | Lieu de naissance |
| Adresse | `adresse1` | ❌ Non | Adresse ligne 1 |
| Complément | `adresse2` | ❌ Non | Adresse ligne 2 |
| Code Postal | `codePostal` | ❌ Non | Code postal |
| Ville | `ville` | ❌ Non | Ville |
| Téléphone | `telephonePersonnel` | ❌ Non | Téléphone |
| Email | `email` | ❌ Non | Email |
| Tarif | `tarif_lettre` | ❌ Non | Code tarif (A, B, C...) |
| Motif | `motif` | ❌ Non | Motif de la recherche |
| Instructions | `instructions` | ❌ Non | Instructions spécifiques |

#### **Champs Sherlock (table `sherlock_donnees`)**

Si vous créez un client similaire à Sherlock avec beaucoup de champs :

| Colonne Excel | Champ interne | Description |
|---------------|---------------|-------------|
| DossierId | `dossier_id` | ID du dossier |
| EC-Civilité | `ec_civilite` | Civilité |
| EC-Prénom | `ec_prenom` | Prénom |
| EC-Nom Usage | `ec_nom_usage` | Nom d'usage |
| EC-Date Naissance | `ec_date_naissance` | Date naissance |
| AD-L1 | `ad_l1` | Adresse ligne 1 |
| AD-L6 CP | `ad_l6_cp` | Code postal |
| AD-Téléphone | `ad_telephone` | Téléphone |
| ... | ... | (Voir CREER_CLIENT_SHERLOCK.sql) |

---

## 🔍 TROUVER LES NOMS DE COLONNES

Pour savoir quels noms de colonnes utiliser dans votre fichier Excel :

1. Ouvrez votre fichier Excel
2. Notez les noms EXACTS des en-têtes (1ère ligne)
3. Utilisez ces noms dans le mapping `column_name`

**Exemple :**

Si votre Excel a ces colonnes :
```
| N° Dossier | Nom Client | Prénom Client | CP | Ville |
```

Vos mappings seront :
```sql
(profile_id_val, 'N° Dossier', 'numeroDossier', true, true, NOW()),
(profile_id_val, 'Nom Client', 'nom', true, true, NOW()),
(profile_id_val, 'Prénom Client', 'prenom', false, true, NOW()),
(profile_id_val, 'CP', 'codePostal', false, true, NOW()),
(profile_id_val, 'Ville', 'ville', false, true, NOW())
```

---

## ⚙️ PARAMÈTRES DES MAPPINGS

### `is_required` (Obligatoire)

- `true` : Le champ DOIT être présent dans le fichier Excel
- `false` : Le champ est optionnel

### `strip_whitespace` (Nettoyer espaces)

- `true` : Supprime les espaces au début et à la fin
- `false` : Garde les espaces

---

## 🧪 VÉRIFIER LA CRÉATION

Après avoir créé le client, vérifiez qu'il existe :

```sql
-- Se connecter à la base
psql -U postgres -d eos_db

-- Vérifier le client
SELECT id, code, nom, actif FROM clients;

-- Vérifier le profil d'import
SELECT ip.id, c.code AS client, ip.name, ip.file_type
FROM import_profiles ip
JOIN clients c ON ip.client_id = c.id
ORDER BY c.code;

-- Vérifier les mappings
SELECT 
    c.code AS client,
    COUNT(ifm.id) AS nb_mappings
FROM import_field_mappings ifm
JOIN import_profiles ip ON ifm.import_profile_id = ip.id
JOIN clients c ON ip.client_id = c.id
GROUP BY c.code
ORDER BY c.code;
```

---

## 📝 EXEMPLE COMPLET : CLIENT SIMPLE

Fichier `CREER_CLIENT_TEST.sql` :

```sql
-- Client simple avec 5 colonnes
INSERT INTO clients (code, nom, actif, date_creation)
VALUES ('TEST', 'Client Test', true, NOW())
ON CONFLICT (code) DO UPDATE SET nom = EXCLUDED.nom;

DO $$
DECLARE
    client_id_val INT;
    profile_id_val INT;
BEGIN
    SELECT id INTO client_id_val FROM clients WHERE code = 'TEST';
    
    INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
    VALUES (client_id_val, 'Test Import', 'EXCEL', 'utf-8', true, NOW())
    RETURNING id INTO profile_id_val;
    
    INSERT INTO import_field_mappings (import_profile_id, column_name, internal_field, is_required, strip_whitespace, date_creation)
    VALUES
        (profile_id_val, 'Numero', 'numeroDossier', true, true, NOW()),
        (profile_id_val, 'Nom', 'nom', true, true, NOW()),
        (profile_id_val, 'Prenom', 'prenom', false, true, NOW()),
        (profile_id_val, 'Ville', 'ville', false, true, NOW()),
        (profile_id_val, 'Telephone', 'telephonePersonnel', false, true, NOW());
END $$;

SELECT 'Client TEST créé avec succès' AS resultat;
```

Exécuter :
```cmd
psql -U postgres -d eos_db -f CREER_CLIENT_TEST.sql
```

---

## 🆚 QUAND UTILISER QUELLE MÉTHODE ?

### ✅ Utilisez la CRÉATION MANUELLE si :

- Vous voulez juste ajouter 1 client simple
- Vous n'avez pas accès à l'autre ordinateur
- Le client n'a pas de tarifs spécifiques
- C'est un nouveau client qui n'existe nulle part

### ✅ Utilisez la SYNCHRONISATION COMPLÈTE si :

- Vous installez sur un nouvel ordinateur
- Vous voulez TOUS les clients d'un coup
- Vous voulez aussi les tarifs et règles tarifaires
- C'est la première installation

---

## 💡 CONSEILS

### 1. Testez d'abord avec un client simple

Créez un client TEST avec 3-4 colonnes pour vous familiariser.

### 2. Utilisez des noms de colonnes clairs

Évitez les caractères spéciaux dans les noms de colonnes Excel.

### 3. Marquez les bons champs comme obligatoires

Au minimum : `numeroDossier` et `nom` doivent être obligatoires.

### 4. Documentez vos mappings

Ajoutez des commentaires dans votre fichier SQL pour vous rappeler à quoi sert chaque mapping.

---

## 🔄 METTRE À JOUR UN CLIENT EXISTANT

Pour modifier les mappings d'un client :

```sql
DO $$
DECLARE
    profile_id_val INT;
BEGIN
    -- Récupérer l'ID du profil
    SELECT ip.id INTO profile_id_val 
    FROM import_profiles ip
    JOIN clients c ON ip.client_id = c.id
    WHERE c.code = 'MON_CLIENT'
    LIMIT 1;
    
    -- Supprimer les anciens mappings
    DELETE FROM import_field_mappings WHERE import_profile_id = profile_id_val;
    
    -- Recréer les nouveaux mappings
    INSERT INTO import_field_mappings (...)
    VALUES (...);
END $$;
```

---

## 🗑️ SUPPRIMER UN CLIENT

```sql
-- Supprimer le client et toutes ses données
DELETE FROM clients WHERE code = 'MON_CLIENT';

-- Les profils et mappings sont supprimés automatiquement (CASCADE)
```

---

## 📚 FICHIERS CRÉÉS POUR VOUS

| Fichier | Description |
|---------|-------------|
| `CREER_CLIENT_SHERLOCK.sql` | Script SQL pour créer Sherlock |
| `CREER_CLIENT_SHERLOCK.bat` | Script BAT pour exécuter facilement |
| `GUIDE_CREER_CLIENT_MANUELLEMENT.md` | Ce guide |

---

## 🆘 EN CAS DE PROBLÈME

### ❌ "ERROR: relation clients does not exist"

La base de données n'est pas initialisée. Exécutez :
```cmd
.\APPLIQUER_MIGRATIONS_SIMPLE.bat
```

### ❌ "ERROR: duplicate key value"

Le client existe déjà. C'est normal avec `ON CONFLICT`, le client sera mis à jour.

### ❌ Le client n'apparaît pas dans l'interface

1. Vérifiez qu'il est bien créé : `SELECT * FROM clients;`
2. Redémarrez l'application : `DEMARRER_EOS_SIMPLE.bat`
3. Videz le cache du navigateur (Ctrl+F5)

---

## ✅ RÉCAPITULATIF

**Pour créer Sherlock rapidement :**
```cmd
.\CREER_CLIENT_SHERLOCK.bat
```

**Pour créer un autre client :**
1. Créez un fichier SQL (inspirez-vous de `CREER_CLIENT_SHERLOCK.sql`)
2. Adaptez les mappings selon vos colonnes Excel
3. Exécutez avec `psql`

**Pour tout synchroniser :**
Utilisez `SYNCHRONISER_VERS_AUTRE_ORDI.bat` (voir `LISEZMOI_SYNCHRONISATION.txt`)

---

Bonne création de clients ! 🚀
