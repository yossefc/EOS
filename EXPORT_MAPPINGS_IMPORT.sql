-- ===================================================================
-- EXPORT DE TOUS LES MAPPINGS D'IMPORT
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DE TOUS LES MAPPINGS D''IMPORT                    ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export de tous les mappings
\o TOUS_MAPPINGS_IMPORT_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DE TOUS LES MAPPINGS D''IMPORT';
\echo '-- Généré automatiquement';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer tous les anciens mappings';
\echo 'TRUNCATE TABLE import_field_mappings CASCADE;';
\echo '';
\echo '-- Insérer tous les mappings';
\echo '';

SELECT 'INSERT INTO import_field_mappings (import_profile_id, internal_field, column_name, strip_whitespace, is_required, date_creation) VALUES (' ||
       import_profile_id || ', ' ||
       '''' || internal_field || ''', ' ||
       '''' || REPLACE(column_name, '''', '''''') || ''', ' ||
       strip_whitespace || ', ' ||
       is_required || ', ' ||
       COALESCE('''' || date_creation || '''', 'NOW()') || ');'
FROM import_field_mappings
ORDER BY import_profile_id, internal_field;

\echo '';
\echo '-- Afficher le nombre de mappings par profil';
\echo 'SELECT ';
\echo '    c.code AS client,';
\echo '    ip.name AS profil,';
\echo '    COUNT(ifm.id) AS nb_mappings';
\echo 'FROM import_profiles ip';
\echo 'JOIN clients c ON ip.client_id = c.id';
\echo 'LEFT JOIN import_field_mappings ifm ON ifm.import_profile_id = ip.id';
\echo 'GROUP BY c.code, ip.name';
\echo 'ORDER BY c.code;';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '✅ Export des mappings terminé : TOUS_MAPPINGS_IMPORT_EXPORT.sql'
\echo ''

