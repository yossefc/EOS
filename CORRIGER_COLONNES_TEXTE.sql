-- ===================================================================
-- Script de correction des colonnes texte dans donnees_enqueteur
-- ===================================================================
-- Ce script convertit directement les colonnes VARCHAR(10) en TEXT
-- sans passer par Alembic (qui cause des problèmes de conversion)
-- ===================================================================

\echo '╔═══════════════════════════════════════════════════════════╗'
\echo '║  Conversion des colonnes texte en TEXT                  ║'
\echo '╚═══════════════════════════════════════════════════════════╝'
\echo ''

-- Vérifier les types actuels
\echo '[INFO] Types actuels des colonnes :'
SELECT 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'donnees_enqueteur'
  AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone');

\echo ''
\echo '[1/3] Conversion de elements_retrouves vers TEXT...'
ALTER TABLE donnees_enqueteur 
    ALTER COLUMN elements_retrouves TYPE TEXT 
    USING elements_retrouves::TEXT;
\echo '✓ elements_retrouves converti en TEXT'

\echo '[2/3] Conversion de code_resultat vers TEXT...'
ALTER TABLE donnees_enqueteur 
    ALTER COLUMN code_resultat TYPE TEXT 
    USING code_resultat::TEXT;
\echo '✓ code_resultat converti en TEXT'

\echo '[3/3] Conversion de flag_etat_civil_errone vers TEXT...'
ALTER TABLE donnees_enqueteur 
    ALTER COLUMN flag_etat_civil_errone TYPE TEXT 
    USING flag_etat_civil_errone::TEXT;
\echo '✓ flag_etat_civil_errone converti en TEXT'

\echo ''
\echo '[INFO] Types après conversion :'
SELECT 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'donnees_enqueteur'
  AND column_name IN ('elements_retrouves', 'code_resultat', 'flag_etat_civil_errone');

\echo ''
\echo '╔═══════════════════════════════════════════════════════════╗'
\echo '║  ✅ Conversion terminée avec succès !                    ║'
\echo '╚═══════════════════════════════════════════════════════════╝'
\echo ''
\echo 'Maintenant, marquez la migration 007 comme appliquée :'
\echo 'UPDATE alembic_version SET version_num = '\''007_enlarge_donnees_enqueteur_columns'\'';'
\echo ''

