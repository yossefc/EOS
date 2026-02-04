-- ======================================================================
-- Correction du mapping URGENCE pour PARTNER
-- Problème : urgence est mappé à PRENOM au lieu d'une colonne URGENCE
-- ======================================================================

\echo '=== AVANT Correction ==='
SELECT id, internal_field, column_name, is_required
FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field IN ('prenom', 'urgence')
ORDER BY internal_field, column_name;

\echo ''
\echo '=== Suppression du mapping incorrect : urgence -> PRENOM ==='

-- Supprimer le mapping INCORRECT : urgence -> PRENOM
DELETE FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'urgence'
AND column_name = 'PRENOM';

\echo 'Mapping incorrect supprimé ✅'
\echo ''
\echo '=== APRÈS Correction ==='

SELECT id, internal_field, column_name, is_required
FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field IN ('prenom', 'urgence')
ORDER BY internal_field, column_name;

\echo ''
\echo '=== Résultat ==='
\echo 'Le champ urgence ne sera plus rempli automatiquement.'
\echo 'Si votre fichier Excel a une colonne URGENCE, vous pourrez ajouter le mapping manuellement.'
\echo ''
\echo 'Pour ajouter un mapping URGENCE (si la colonne existe dans votre fichier) :'
\echo '  INSERT INTO import_field_mappings (import_profile_id, internal_field, column_name, is_required, created_at)'
\echo '  VALUES ((SELECT id FROM import_profiles WHERE client_id = (SELECT id FROM clients WHERE code = '\''PARTNER'\'') AND name = '\''CONTESTATIONS'\''), '\''urgence'\'', '\''URGENCE'\'', false, NOW());'
\echo ''

