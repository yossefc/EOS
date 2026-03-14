-- ================================================================
-- Script de correction automatique des permissions PostgreSQL
-- Donne tous les droits à l'utilisateur postgres sur toutes les tables
-- ================================================================

\echo '================================================================'
\echo '     Correction des permissions PostgreSQL'
\echo '================================================================'
\echo ''

-- 1. Donner tous les droits sur toutes les tables du schema public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

\echo '✓ Droits accordés sur toutes les tables'

-- 2. Donner tous les droits sur toutes les séquences (pour les INSERT avec ID auto)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

\echo '✓ Droits accordés sur toutes les séquences'

-- 3. Définir les permissions par défaut pour les futures tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;

\echo '✓ Permissions par défaut définies pour les futures tables'

-- 4. Vérification : lister les tables avec leurs propriétaires
\echo ''
\echo 'Tables et leurs propriétaires :'
\echo '-----------------------------'
SELECT 
    schemaname,
    tablename,
    tableowner,
    CASE 
        WHEN has_table_privilege('postgres', schemaname || '.' || tablename, 'SELECT') THEN 'OK'
        ELSE 'Pas de droits'
    END as acces_postgres
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo '================================================================'
\echo '           Permissions corrigées avec succès !'
\echo '================================================================'

