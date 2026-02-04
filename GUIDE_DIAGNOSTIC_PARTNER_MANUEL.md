# 🔍 Guide de Diagnostic Partner - Méthode Manuelle

## Étape 1 : Se connecter à PostgreSQL

Ouvrez PowerShell et exécutez :

```powershell
psql -U postgres -d eos_db
```

Entrez votre mot de passe PostgreSQL quand demandé.

---

## Étape 2 : Vérifier le client PARTNER

Copiez-collez cette requête dans psql :

```sql
SELECT id, code, nom, actif FROM clients WHERE code = 'PARTNER';
```

**Résultat attendu** : Une ligne avec le client PARTNER

---

## Étape 3 : STATISTIQUES DES EXPORTS

```sql
SELECT 
    CASE 
        WHEN d.est_contestation THEN 'Contestation'
        ELSE 'Enquête'
    END AS type_enquete,
    CASE 
        WHEN de.code_resultat IN ('P', 'H') THEN 'Positive'
        WHEN de.code_resultat IN ('N', 'I') THEN 'Négative'
        WHEN de.code_resultat IS NULL THEN '⚠️ SANS CODE ⚠️'
        ELSE 'Autre (' || de.code_resultat || ')'
    END AS resultat,
    COUNT(*) AS nombre
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
GROUP BY type_enquete, resultat
ORDER BY type_enquete, resultat;
```

### Interprétation :

| type_enquete | resultat | nombre | Signification |
|--------------|----------|--------|---------------|
| Enquête | Positive | X | ✅ Sera exporté dans "Enquêtes Positives" |
| Enquête | Négative | Y | ✅ Sera exporté dans "Enquêtes Négatives" |
| Contestation | Positive | Z | ✅ Sera exporté dans "Contestations Positives" |
| Contestation | Négative | W | ✅ Sera exporté dans "Contestations Négatives" |
| Enquête | ⚠️ SANS CODE ⚠️ | N | ❌ **PROBLÈME** : N'ira nulle part ! |

---

## Étape 4 : IDENTIFIER LES PROBLÈMES

### 4.1 - Enquêtes SANS code résultat

```sql
SELECT d.id, d.numeroDossier, LEFT(d.nom, 30) AS nom, 
       d.statut_validation, de.code_resultat, d.est_contestation
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND de.code_resultat IS NULL
LIMIT 20;
```

**Si cette requête retourne des lignes** : C'est le problème ! Ces enquêtes n'ont pas de code résultat.

---

### 4.2 - Contestations NON marquées

```sql
SELECT d.id, d.numeroDossier, LEFT(d.nom, 30) AS nom, 
       d.typeDemande, d.est_contestation, d.enquete_originale_id
FROM donnees d
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND (d.typeDemande = 'CON' OR d.enquete_originale_id IS NOT NULL)
  AND d.est_contestation = FALSE
LIMIT 20;
```

**Si cette requête retourne des lignes** : Ces contestations ne sont pas marquées correctement.

---

## Étape 5 : CORRIGER LES PROBLÈMES

### Correction 1 : Ajouter les codes résultats manquants

⚠️ **ATTENTION** : Cette requête va mettre **'P'** (Positif) par défaut. Ajustez manuellement ensuite si nécessaire.

```sql
-- Vérifier d'abord combien seront affectés
SELECT COUNT(*) 
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND de.id IS NULL;

-- Si OK, créer les entrées manquantes
INSERT INTO donnees_enqueteur (donnee_id, code_resultat)
SELECT d.id, 'P'
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND de.id IS NULL;
```

---

### Correction 2 : Marquer les contestations

```sql
-- Vérifier d'abord
SELECT COUNT(*)
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND statut_validation = 'validee'
  AND exported = FALSE
  AND (typeDemande = 'CON' OR enquete_originale_id IS NOT NULL)
  AND est_contestation = FALSE;

-- Si OK, corriger
UPDATE donnees
SET est_contestation = TRUE
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND statut_validation = 'validee'
  AND exported = FALSE
  AND (typeDemande = 'CON' OR enquete_originale_id IS NOT NULL)
  AND est_contestation = FALSE;
```

---

## Étape 6 : VÉRIFIER À NOUVEAU

Réexécutez la requête de l'Étape 3 pour voir les nouvelles statistiques.

Ensuite, dans l'interface web :
1. Allez dans **Export**
2. Section **Export PARTNER**
3. Les statistiques devraient maintenant être correctes !

---

## Alternative Rapide : Une Seule Requête

Voici toutes les stats importantes en une fois :

```sql
\echo '=== STATISTIQUES EXPORTS PARTNER ==='
SELECT 
    CASE 
        WHEN d.est_contestation THEN 'Contestation'
        ELSE 'Enquête'
    END AS type,
    CASE 
        WHEN de.code_resultat IN ('P', 'H') THEN 'Positive'
        WHEN de.code_resultat IN ('N', 'I') THEN 'Négative'
        WHEN de.code_resultat IS NULL THEN 'SANS_CODE'
        ELSE de.code_resultat
    END AS resultat,
    COUNT(*) AS nb
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
GROUP BY type, resultat
ORDER BY type, resultat;

\echo ''
\echo '=== CODES RESULTATS DISTINCTS ==='
SELECT DISTINCT de.code_resultat, COUNT(*) 
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
GROUP BY de.code_resultat;
```

---

**Dernière mise à jour** : 22 janvier 2026

