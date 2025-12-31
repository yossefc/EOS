-- ================================================================
-- Script de vérification de la base de données EOS
-- Vérifie que toutes les tables nécessaires existent
-- ================================================================

\echo '================================================================'
\echo '     Vérification des tables de la base de données EOS'
\echo '================================================================'
\echo ''

-- 1. Lister toutes les tables existantes
\echo '1. TABLES EXISTANTES :'
\echo '-------------------'
SELECT 
    table_name,
    CASE 
        WHEN table_name IN ('clients', 'import_profiles', 'import_field_mappings', 'fichiers', 'donnees', 'donnees_enqueteur', 'enquete_facturation', 'tarifs_enqueteur', 'partner_request_keywords', 'partner_case_requests', 'partner_tarif_rules', 'confirmation_options', 'enquete_archive_files', 'export_batches', 'alembic_version') 
        THEN 'OK'
        ELSE 'Inconnue'
    END as statut
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

\echo ''
\echo '2. VERIFICATION DES TABLES ESSENTIELLES :'
\echo '---------------------------------------'

-- Vérification des tables principales
DO $$
DECLARE
    tables_necessaires TEXT[] := ARRAY[
        'clients',
        'import_profiles',
        'import_field_mappings',
        'fichiers',
        'donnees',
        'donnees_enqueteur',
        'enquete_facturation',
        'tarifs_enqueteur',
        'partner_request_keywords',
        'partner_case_requests',
        'partner_tarif_rules',
        'confirmation_options',
        'enquete_archive_files',
        'export_batches',
        'alembic_version'
    ];
    table_name TEXT;
    table_exists BOOLEAN;
    missing_count INT := 0;
BEGIN
    FOREACH table_name IN ARRAY tables_necessaires
    LOOP
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = table_name
        ) INTO table_exists;
        
        IF table_exists THEN
            RAISE NOTICE '✓ % : OK', table_name;
        ELSE
            RAISE NOTICE '✗ % : MANQUANTE !', table_name;
            missing_count := missing_count + 1;
        END IF;
    END LOOP;
    
    RAISE NOTICE '';
    IF missing_count = 0 THEN
        RAISE NOTICE '================================================';
        RAISE NOTICE '✓ TOUTES LES TABLES SONT PRESENTES !';
        RAISE NOTICE '================================================';
    ELSE
        RAISE NOTICE '================================================';
        RAISE NOTICE '✗ % TABLE(S) MANQUANTE(S) !', missing_count;
        RAISE NOTICE '================================================';
    END IF;
END $$;

\echo ''
\echo '3. VERIFICATION DES CLIENTS :'
\echo '---------------------------'
SELECT 
    id,
    code,
    nom,
    actif,
    CASE 
        WHEN actif THEN 'Actif'
        ELSE 'Inactif'
    END as statut
FROM clients
ORDER BY id;

\echo ''
\echo '4. VERIFICATION DES PROFILS D''IMPORT :'
\echo '-------------------------------------'
SELECT 
    ip.id,
    c.code as client_code,
    ip.name as profile_name,
    ip.file_type,
    COUNT(ifm.id) as nb_mappings
FROM import_profiles ip
JOIN clients c ON c.id = ip.client_id
LEFT JOIN import_field_mappings ifm ON ifm.import_profile_id = ip.id
GROUP BY ip.id, c.code, ip.name, ip.file_type
ORDER BY c.code, ip.id;

\echo ''
\echo '5. VERIFICATION DES COLONNES PARTNER DANS TABLE DONNEES :'
\echo '-------------------------------------------------------'
SELECT 
    column_name,
    data_type,
    CASE WHEN is_nullable = 'YES' THEN 'NULL' ELSE 'NOT NULL' END as nullable
FROM information_schema.columns
WHERE table_name = 'donnees'
  AND column_name IN ('tarif_lettre', 'recherche', 'instructions', 'date_jour', 'nom_complet', 'motif')
ORDER BY column_name;

\echo ''
\echo '6. VERSION DES MIGRATIONS ALEMBIC :'
\echo '---------------------------------'
SELECT version_num as derniere_migration FROM alembic_version;

\echo ''
\echo '================================================================'
\echo '           Vérification terminée'
\echo '================================================================'

