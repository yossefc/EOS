-- Vérifier les mappings du profil PARTNER
\echo '=== Profils PARTNER ==='
SELECT id, name, file_type
FROM import_profiles
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER');

\echo ''
\echo '=== Mappings PRENOM ==='
SELECT column_name, is_required
FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'prenom'
ORDER BY column_name;

\echo ''
\echo '=== Mappings URGENCE ==='
SELECT column_name, is_required
FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
AND internal_field = 'urgence'
ORDER BY column_name;

\echo ''
\echo '=== Tous les mappings PARTNER (premiers 30) ==='
SELECT internal_field, column_name, is_required
FROM import_field_mappings
WHERE import_profile_id IN (
    SELECT id FROM import_profiles
    WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
)
ORDER BY internal_field, column_name
LIMIT 30;

