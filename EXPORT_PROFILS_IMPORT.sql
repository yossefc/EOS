-- ===================================================================
-- EXPORT DE TOUS LES PROFILS D'IMPORT
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DE TOUS LES PROFILS D''IMPORT                     ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export de tous les profils d'import
\o TOUS_PROFILS_IMPORT_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DE TOUS LES PROFILS D''IMPORT';
\echo '-- Généré automatiquement';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer tous les anciens profils';
\echo 'TRUNCATE TABLE import_profiles CASCADE;';
\echo '';
\echo '-- Insérer tous les profils d''import';
\echo '';

SELECT 'INSERT INTO import_profiles (id, client_id, name, file_type, encoding, actif, date_creation) VALUES (' ||
       id || ', ' ||
       client_id || ', ' ||
       '''' || REPLACE(name, '''', '''''') || ''', ' ||
       '''' || file_type || ''', ' ||
       '''' || encoding || ''', ' ||
       actif || ', ' ||
       COALESCE('''' || date_creation || '''', 'NOW()') || ');'
FROM import_profiles
ORDER BY id;

\echo '';
\echo '-- Mettre à jour la séquence';
\echo 'SELECT setval(''import_profiles_id_seq'', (SELECT MAX(id) FROM import_profiles));';
\echo '';
\echo '-- Afficher les profils importés';
\echo 'SELECT ip.id, c.code AS client, ip.name, ip.file_type';
\echo 'FROM import_profiles ip';
\echo 'JOIN clients c ON ip.client_id = c.id';
\echo 'ORDER BY c.code, ip.id;';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '✅ Export des profils terminé : TOUS_PROFILS_IMPORT_EXPORT.sql'
\echo ''

