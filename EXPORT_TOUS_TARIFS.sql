-- ===================================================================
-- EXPORT DE TOUS LES TARIFS
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DE TOUS LES TARIFS                                ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export de tous les tarifs
\o TOUS_TARIFS_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DE TOUS LES TARIFS';
\echo '-- Généré automatiquement';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer tous les anciens tarifs';
\echo 'TRUNCATE TABLE tarifs_client CASCADE;';
\echo '';
\echo '-- Insérer tous les tarifs';
\echo '';

SELECT 'INSERT INTO tarifs_client (client_id, code_lettre, description, montant, date_debut, date_fin, actif) VALUES (' ||
       client_id || ', ' ||
       '''' || code_lettre || ''', ' ||
       '''' || REPLACE(description, '''', '''''') || ''', ' ||
       montant || ', ' ||
       '''' || date_debut || ''', ' ||
       COALESCE('''' || date_fin || '''', 'NULL') || ', ' ||
       actif || ');'
FROM tarifs_client
ORDER BY client_id, code_lettre;

\echo '';
\echo '-- Afficher les tarifs importés par client';
\echo 'SELECT c.code AS client, tc.code_lettre, tc.description, tc.montant';
\echo 'FROM tarifs_client tc';
\echo 'JOIN clients c ON tc.client_id = c.id';
\echo 'ORDER BY c.code, tc.code_lettre;';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '✅ Export des tarifs terminé : TOUS_TARIFS_EXPORT.sql'
\echo ''

