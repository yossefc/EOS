-- ===================================================================
-- EXPORT DE TOUTES LES RÈGLES TARIFAIRES
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DE TOUTES LES RÈGLES TARIFAIRES                   ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export de toutes les règles tarifaires
\o TOUTES_REGLES_TARIFAIRES_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DE TOUTES LES RÈGLES TARIFAIRES';
\echo '-- Généré automatiquement';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer toutes les anciennes règles';
\echo 'TRUNCATE TABLE partner_tarif_rules CASCADE;';
\echo '';
\echo '-- Insérer toutes les règles tarifaires';
\echo '';

SELECT 'INSERT INTO partner_tarif_rules (client_id, tarif_lettre, request_key, description, actif) VALUES (' ||
       client_id || ', ' ||
       '''' || tarif_lettre || ''', ' ||
       '''' || request_key || ''', ' ||
       COALESCE('''' || REPLACE(description, '''', '''''') || '''', 'NULL') || ', ' ||
       actif || ');'
FROM partner_tarif_rules
ORDER BY client_id, tarif_lettre, request_key;

\echo '';
\echo '-- Afficher les règles importées par client';
\echo 'SELECT ';
\echo '    c.code AS client,';
\echo '    COUNT(*) AS nb_regles';
\echo 'FROM partner_tarif_rules ptr';
\echo 'JOIN clients c ON ptr.client_id = c.id';
\echo 'GROUP BY c.code';
\echo 'ORDER BY c.code;';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '✅ Export des règles terminé : TOUTES_REGLES_TARIFAIRES_EXPORT.sql'
\echo ''

