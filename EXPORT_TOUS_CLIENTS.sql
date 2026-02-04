-- ===================================================================
-- EXPORT DE TOUS LES CLIENTS
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DE TOUS LES CLIENTS                               ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export de tous les clients
\o TOUS_CLIENTS_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DE TOUS LES CLIENTS';
\echo '-- Généré automatiquement';
\echo '-- ===================================================================';
\echo '';
\echo '-- Désactiver temporairement les triggers et contraintes';
\echo 'SET session_replication_role = replica;';
\echo '';

SELECT 'INSERT INTO clients (id, code, nom, actif, date_creation) VALUES (' ||
       id || ', ' ||
       '''' || code || ''', ' ||
       '''' || REPLACE(nom, '''', '''''') || ''', ' ||
       actif || ', ' ||
       COALESCE('''' || date_creation || '''', 'NOW()') || ')' ||
       ' ON CONFLICT (id) DO UPDATE SET ' ||
       'code = EXCLUDED.code, ' ||
       'nom = EXCLUDED.nom, ' ||
       'actif = EXCLUDED.actif;'
FROM clients
ORDER BY id;

\echo '';
\echo '-- Réactiver les triggers et contraintes';
\echo 'SET session_replication_role = DEFAULT;';
\echo '';
\echo '-- Mettre à jour la séquence';
\echo 'SELECT setval(''clients_id_seq'', (SELECT MAX(id) FROM clients));';
\echo '';
\echo '-- Afficher les clients importés';
\echo 'SELECT id, code, nom, actif FROM clients ORDER BY id;';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '✅ Export des clients terminé : TOUS_CLIENTS_EXPORT.sql'
\echo ''

