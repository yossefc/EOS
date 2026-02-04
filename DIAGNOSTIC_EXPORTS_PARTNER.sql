-- ================================================================
-- Script de diagnostic des exports Partner
-- ================================================================

\echo '================================================================================'
\echo 'DIAGNOSTIC DES EXPORTS PARTNER'
\echo '================================================================================'
\echo ''

-- 1. Vérifier que le client PARTNER existe
\echo '1. Vérification du client PARTNER:'
SELECT id, code, nom, actif 
FROM clients 
WHERE code = 'PARTNER';

\echo ''
\echo '================================================================================'
\echo '2. STATISTIQUES DES ENQUETES VALIDEES NON EXPORTEES'
\echo '================================================================================'
\echo ''

-- Statistiques par type et résultat
SELECT 
    CASE 
        WHEN d.est_contestation THEN 'Contestation'
        ELSE 'Enquête'
    END AS type_enquete,
    CASE 
        WHEN de.code_resultat IN ('P', 'H') THEN 'Positive'
        WHEN de.code_resultat IN ('N', 'I') THEN 'Négative'
        WHEN de.code_resultat IS NULL THEN 'SANS CODE'
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

\echo ''
\echo '================================================================================'
\echo '3. ENQUETES SANS CODE RESULTAT (PROBLEME)'
\echo '================================================================================'
\echo ''

SELECT d.id, d.numeroDossier, d.nom, d.statut_validation, 
       de.code_resultat, d.est_contestation
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND de.code_resultat IS NULL
ORDER BY d.id
LIMIT 10;

\echo ''
\echo '================================================================================'
\echo '4. CONTESTATIONS NON MARQUEES (PROBLEME)'
\echo '================================================================================'
\echo ''

SELECT d.id, d.numeroDossier, d.nom, d.typeDemande, 
       d.est_contestation, d.enquete_originale_id
FROM donnees d
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND (d.typeDemande = 'CON' OR d.enquete_originale_id IS NOT NULL)
  AND d.est_contestation = FALSE
LIMIT 10;

\echo ''
\echo '================================================================================'
\echo '5. LISTE DETAILLEE DES 20 PREMIERES ENQUETES'
\echo '================================================================================'
\echo ''

SELECT 
    d.id,
    d.numeroDossier,
    LEFT(d.nom, 20) AS nom,
    d.statut_validation,
    de.code_resultat,
    CASE WHEN d.est_contestation THEN 'OUI' ELSE 'NON' END AS contestation,
    CASE WHEN d.exported THEN 'OUI' ELSE 'NON' END AS exporte
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
ORDER BY d.est_contestation, de.code_resultat, d.id
LIMIT 20;

\echo ''
\echo '================================================================================'
\echo 'FIN DU DIAGNOSTIC'
\echo '================================================================================'

