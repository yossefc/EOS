-- ===================================================================
-- EXPORT DES DONNÉES PARTNER (Ordinateur SOURCE)
-- ===================================================================
-- Ce script exporte tous les tarifs et configurations PARTNER
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  EXPORT DES DONNÉES PARTNER                               ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

\echo '[INFO] Export en cours...'
\echo ''

-- Désactiver l'affichage des commandes
\set QUIET on

-- Export des tarifs PARTNER
\o PARTNER_TARIFS_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DES TARIFS PARTNER';
\echo '-- Généré automatiquement le :' `date`;
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer les anciens tarifs PARTNER';
\echo 'DELETE FROM tarifs_client WHERE client_id = (SELECT id FROM clients WHERE code = ''PARTNER'');';
\echo '';
\echo '-- Insérer les nouveaux tarifs';

SELECT 'INSERT INTO tarifs_client (client_id, code_lettre, description, montant, date_debut, date_fin, actif) VALUES (' ||
       '(SELECT id FROM clients WHERE code = ''PARTNER''), ' ||
       '''' || code_lettre || ''', ' ||
       '''' || REPLACE(description, '''', '''''') || ''', ' ||
       montant || ', ' ||
       '''' || date_debut || ''', ' ||
       COALESCE('''' || date_fin || '''', 'NULL') || ', ' ||
       actif || ');'
FROM tarifs_client tc
JOIN clients c ON tc.client_id = c.id
WHERE c.code = 'PARTNER'
ORDER BY tc.code_lettre;

\echo '';
\echo '-- Fin de l''import des tarifs';
\o

-- Export des options de confirmation PARTNER
\o PARTNER_CONFIRMATION_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DES OPTIONS DE CONFIRMATION PARTNER';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer les anciennes options PARTNER';
\echo 'DELETE FROM confirmation_options WHERE client_id = (SELECT id FROM clients WHERE code = ''PARTNER'');';
\echo '';
\echo '-- Insérer les nouvelles options';

SELECT 'INSERT INTO confirmation_options (client_id, option_text, usage_count, created_at) VALUES (' ||
       '(SELECT id FROM clients WHERE code = ''PARTNER''), ' ||
       '''' || REPLACE(option_text, '''', '''''') || ''', ' ||
       usage_count || ', ' ||
       'NOW());'
FROM confirmation_options co
JOIN clients c ON co.client_id = c.id
WHERE c.code = 'PARTNER'
ORDER BY co.id;

\echo '';
\echo '-- Fin de l''import des options de confirmation';
\o

-- Export des règles tarifaires PARTNER
\o PARTNER_TARIF_RULES_EXPORT.sql
\echo '-- ===================================================================';
\echo '-- IMPORT DES RÈGLES TARIFAIRES PARTNER';
\echo '-- ===================================================================';
\echo '';
\echo '-- Supprimer les anciennes règles PARTNER';
\echo 'DELETE FROM partner_tarif_rules WHERE client_id = (SELECT id FROM clients WHERE code = ''PARTNER'');';
\echo '';
\echo '-- Insérer les nouvelles règles';

SELECT 'INSERT INTO partner_tarif_rules (client_id, tarif_lettre, request_key, description, actif) VALUES (' ||
       '(SELECT id FROM clients WHERE code = ''PARTNER''), ' ||
       '''' || tarif_lettre || ''', ' ||
       '''' || request_key || ''', ' ||
       COALESCE('''' || REPLACE(description, '''', '''''') || '''', 'NULL') || ', ' ||
       actif || ');'
FROM partner_tarif_rules ptr
JOIN clients c ON ptr.client_id = c.id
WHERE c.code = 'PARTNER'
ORDER BY ptr.tarif_lettre, ptr.request_key;

\echo '';
\echo '-- Fin de l''import des règles tarifaires';
\o

-- Réactiver l'affichage
\set QUIET off

\echo ''
\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  ✅ EXPORT TERMINÉ AVEC SUCCÈS !                          ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''
\echo 'Fichiers créés :'
\echo '  1. PARTNER_TARIFS_EXPORT.sql'
\echo '  2. PARTNER_CONFIRMATION_EXPORT.sql'
\echo '  3. PARTNER_TARIF_RULES_EXPORT.sql'
\echo ''
\echo 'Copiez ces 3 fichiers sur l''autre ordinateur dans D:\eos\'
\echo 'Puis exécutez : IMPORTER_DONNEES_PARTNER.bat'
\echo ''

