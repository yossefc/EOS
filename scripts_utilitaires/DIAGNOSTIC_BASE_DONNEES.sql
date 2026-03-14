-- ===================================================================
-- DIAGNOSTIC COMPLET DE LA BASE DE DONNÉES EOS
-- ===================================================================
-- Ce script vérifie l'état complet de la base de données :
--   - Migrations Alembic appliquées
--   - Tables existantes
--   - Relations (foreign keys)
--   - Index
--   - Données de base (clients, profils d'import, etc.)
-- ===================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════════╗'
\echo '║          DIAGNOSTIC COMPLET BASE DE DONNÉES EOS               ║'
\echo '╚════════════════════════════════════════════════════════════════╝'
\echo ''

-- ===================================================================
-- 1. VERSION ALEMBIC
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '1. VERSION ALEMBIC'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version') 
        THEN '✅ Table alembic_version existe'
        ELSE '❌ Table alembic_version MANQUANTE'
    END as status;

SELECT 
    '📌 Migration actuelle: ' || version_num as info
FROM alembic_version;

\echo ''

-- ===================================================================
-- 2. TABLES PRINCIPALES
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '2. TABLES PRINCIPALES'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

WITH required_tables AS (
    SELECT unnest(ARRAY[
        'clients',
        'enqueteurs',
        'donnees',
        'donnees_enqueteur',
        'fichiers',
        'import_profiles',
        'import_field_mappings',
        'tarifs_eos',
        'tarifs_enqueteur',
        'tarifs_client',
        'enquete_facturation',
        'export_batches',
        'confirmation_options',
        'partner_case_requests',
        'partner_tarif_rules'
    ]) AS table_name
)
SELECT 
    rt.table_name,
    CASE 
        WHEN t.table_name IS NOT NULL THEN '✅ Existe'
        ELSE '❌ MANQUANTE'
    END as status,
    COALESCE(
        (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = rt.table_name),
        0
    ) as nb_colonnes
FROM required_tables rt
LEFT JOIN information_schema.tables t 
    ON rt.table_name = t.table_name 
    AND t.table_schema = 'public'
ORDER BY rt.table_name;

\echo ''

-- ===================================================================
-- 3. RELATIONS (FOREIGN KEYS)
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '3. RELATIONS (FOREIGN KEYS)'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    '📊 Total Foreign Keys: ' || COUNT(*) as info
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public';

\echo ''
\echo 'Détail des Foreign Keys par table:'
\echo ''

SELECT 
    tc.table_name as "Table",
    COUNT(*) as "Nb FK"
FROM information_schema.table_constraints tc
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
GROUP BY tc.table_name
ORDER BY tc.table_name;

\echo ''

-- ===================================================================
-- 4. INDEX
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '4. INDEX'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    '📊 Total Index: ' || COUNT(*) as info
FROM pg_indexes
WHERE schemaname = 'public';

\echo ''

-- ===================================================================
-- 5. CLIENTS
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '5. CLIENTS'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM clients) 
        THEN '✅ Table clients contient des données'
        ELSE '⚠️  Table clients VIDE'
    END as status;

\echo ''

SELECT 
    id,
    code,
    nom,
    actif,
    to_char(date_creation, 'YYYY-MM-DD') as date_creation
FROM clients
ORDER BY id;

\echo ''

-- ===================================================================
-- 6. PROFILS D'IMPORT
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '6. PROFILS D''IMPORT'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    c.code as client,
    ip.name as profil,
    ip.file_type,
    ip.actif,
    (SELECT COUNT(*) FROM import_field_mappings WHERE import_profile_id = ip.id) as nb_mappings
FROM import_profiles ip
JOIN clients c ON ip.client_id = c.id
ORDER BY c.code, ip.name;

\echo ''

-- ===================================================================
-- 7. TARIFS CLIENT
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '7. TARIFS CLIENT'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tarifs_client') 
        THEN '✅ Table tarifs_client existe'
        ELSE '❌ Table tarifs_client MANQUANTE'
    END as status;

\echo ''

SELECT 
    c.code as client,
    tc.code_lettre,
    tc.description,
    tc.montant,
    tc.actif
FROM tarifs_client tc
JOIN clients c ON tc.client_id = c.id
WHERE tc.actif = true
ORDER BY c.code, tc.code_lettre;

\echo ''

-- ===================================================================
-- 8. OPTIONS DE CONFIRMATION
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '8. OPTIONS DE CONFIRMATION'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'confirmation_options') 
        THEN '✅ Table confirmation_options existe'
        ELSE '❌ Table confirmation_options MANQUANTE'
    END as status;

\echo ''

SELECT 
    c.code as client,
    co.option_text,
    co.usage_count,
    to_char(co.created_at, 'YYYY-MM-DD') as date_creation
FROM confirmation_options co
JOIN clients c ON co.client_id = c.id
ORDER BY c.code, co.option_text;

\echo ''

-- ===================================================================
-- 9. COLONNES CRITIQUES DANS DONNEES
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '9. COLONNES PARTNER DANS TABLE DONNEES'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

WITH partner_columns AS (
    SELECT unnest(ARRAY[
        'tarif_lettre',
        'recherche',
        'instructions',
        'date_jour',
        'nom_complet',
        'motif'
    ]) AS column_name
)
SELECT 
    pc.column_name,
    CASE 
        WHEN c.column_name IS NOT NULL THEN '✅ Existe'
        ELSE '❌ MANQUANTE'
    END as status,
    COALESCE(c.data_type, 'N/A') as type
FROM partner_columns pc
LEFT JOIN information_schema.columns c 
    ON pc.column_name = c.column_name 
    AND c.table_name = 'donnees'
ORDER BY pc.column_name;

\echo ''

-- ===================================================================
-- 10. COLONNES DANS DONNEES_ENQUETEUR
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '10. COLONNES TEXTE DANS DONNEES_ENQUETEUR'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    column_name,
    data_type,
    CASE 
        WHEN character_maximum_length IS NOT NULL 
        THEN 'VARCHAR(' || character_maximum_length || ')'
        WHEN data_type = 'text'
        THEN 'TEXT'
        ELSE data_type
    END as type_complet
FROM information_schema.columns
WHERE table_name = 'donnees_enqueteur'
    AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone')
ORDER BY column_name;

\echo ''

-- ===================================================================
-- 11. STATISTIQUES GÉNÉRALES
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '11. STATISTIQUES GÉNÉRALES'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    'Clients' as table_name,
    COUNT(*) as nb_lignes
FROM clients
UNION ALL
SELECT 
    'Enquêteurs',
    COUNT(*)
FROM enqueteurs
UNION ALL
SELECT 
    'Dossiers (donnees)',
    COUNT(*)
FROM donnees
UNION ALL
SELECT 
    'Enquêtes complétées',
    COUNT(*)
FROM donnees_enqueteur
UNION ALL
SELECT 
    'Fichiers importés',
    COUNT(*)
FROM fichiers
UNION ALL
SELECT 
    'Profils d''import',
    COUNT(*)
FROM import_profiles
ORDER BY table_name;

\echo ''

-- ===================================================================
-- 12. RÉSUMÉ FINAL
-- ===================================================================
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo '12. RÉSUMÉ FINAL'
\echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
\echo ''

SELECT 
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tarifs_client') THEN '✅' ELSE '❌' END || ' Table tarifs_client' as verification,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tarifs_client') THEN 'OK' ELSE 'MANQUANT - Exécuter CONFIGURER_TARIFS_PARTNER.bat' END as action
UNION ALL
SELECT 
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'confirmation_options') THEN '✅' ELSE '❌' END || ' Table confirmation_options',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'confirmation_options') THEN 'OK' ELSE 'MANQUANT - Migration 006 non appliquée' END
UNION ALL
SELECT 
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'donnees' AND column_name = 'tarif_lettre') THEN '✅' ELSE '❌' END || ' Colonnes PARTNER dans donnees',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'donnees' AND column_name = 'tarif_lettre') THEN 'OK' ELSE 'MANQUANT - Migration 005 non appliquée' END
UNION ALL
SELECT 
    CASE WHEN (SELECT data_type FROM information_schema.columns WHERE table_name = 'donnees_enqueteur' AND column_name = 'elements_retrouves') = 'text' THEN '✅' ELSE '❌' END || ' Colonnes TEXT dans donnees_enqueteur',
    CASE WHEN (SELECT data_type FROM information_schema.columns WHERE table_name = 'donnees_enqueteur' AND column_name = 'elements_retrouves') = 'text' THEN 'OK' ELSE 'MANQUANT - Exécuter CORRIGER_COLONNES_TEXTE.bat' END
UNION ALL
SELECT 
    CASE WHEN EXISTS (SELECT 1 FROM clients WHERE code = 'PARTNER') THEN '✅' ELSE '❌' END || ' Client PARTNER configuré',
    CASE WHEN EXISTS (SELECT 1 FROM clients WHERE code = 'PARTNER') THEN 'OK' ELSE 'MANQUANT - Exécuter CONFIGURER_PARTNER.bat' END
UNION ALL
SELECT 
    CASE WHEN EXISTS (SELECT 1 FROM import_profiles ip JOIN clients c ON ip.client_id = c.id WHERE c.code = 'PARTNER') THEN '✅' ELSE '❌' END || ' Profil import PARTNER',
    CASE WHEN EXISTS (SELECT 1 FROM import_profiles ip JOIN clients c ON ip.client_id = c.id WHERE c.code = 'PARTNER') THEN 'OK' ELSE 'MANQUANT - Exécuter CONFIGURER_PARTNER.bat' END;

\echo ''
\echo '╔════════════════════════════════════════════════════════════════╗'
\echo '║              FIN DU DIAGNOSTIC                                 ║'
\echo '╚════════════════════════════════════════════════════════════════╝'
\echo ''

