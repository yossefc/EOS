-- Vérifier l'état des contestations PARTNER
\echo '=== Contestations avec typeDemande = CON ==='
SELECT 
    id,
    "numeroDossier",
    LEFT(nom, 20) AS nom,
    LEFT(prenom, 15) AS prenom,
    urgence,
    "typeDemande",
    est_contestation,
    statut_validation,
    exported
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND "typeDemande" = 'CON'
ORDER BY id DESC
LIMIT 10;

\echo ''
\echo '=== Statistiques ==='
SELECT 
    "typeDemande",
    est_contestation,
    COUNT(*) AS nombre
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
GROUP BY "typeDemande", est_contestation
ORDER BY "typeDemande", est_contestation;

