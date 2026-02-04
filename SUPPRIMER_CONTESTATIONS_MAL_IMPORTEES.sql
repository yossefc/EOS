-- Supprimer les contestations avec prenom = 'URGENT'
-- Ces contestations ont été importées avec le mapping incorrect

\echo '=== Contestations à supprimer (prenom = URGENT) ==='
SELECT 
    id,
    "numeroDossier",
    nom,
    prenom,
    "typeDemande",
    statut_validation
FROM donnees
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
AND "typeDemande" = 'CON'
AND prenom = 'URGENT';

\echo ''
\echo '=== ATTENTION : Voulez-vous vraiment supprimer ces contestations ? ==='
\echo 'Si OUI, decommenter la ligne DELETE ci-dessous et relancer le script'
\echo ''

-- DÉCOMMENTER cette ligne pour supprimer :
-- DELETE FROM donnees
-- WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
-- AND "typeDemande" = 'CON'
-- AND prenom = 'URGENT';

\echo 'Pour supprimer, editez le fichier SQL et decommenter la ligne DELETE'

