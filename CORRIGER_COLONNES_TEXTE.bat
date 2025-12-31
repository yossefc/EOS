@echo off
cls

echo ================================================================
echo     Correction DIRECTE des colonnes texte (SQL pur)         
echo ================================================================
echo.
echo Ce script convertit les colonnes VARCHAR en TEXT directement
echo dans PostgreSQL, SANS passer par Alembic.
echo.
echo Colonnes concernees :
echo   - elements_retrouves (VARCHAR ^-^> TEXT)
echo   - code_resultat (VARCHAR ^-^> TEXT)
echo   - flag_etat_civil_errone (VARCHAR ^-^> TEXT)
echo.
pause
echo.

cd /d D:\EOS

echo [1/2] Execution du script SQL...
echo.

psql -U postgres -d eos_db -f CORRIGER_COLONNES_TEXTE.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'execution du script SQL
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Marquage de la migration 007 comme appliquee...
echo.

psql -U postgres -d eos_db -c "UPDATE alembic_version SET version_num = '007_enlarge_donnees_enqueteur_columns';"

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de la mise a jour d'Alembic
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              Correction appliquee avec succes !           
echo ================================================================
echo.
echo Les colonnes ont ete converties en TEXT directement.
echo La migration 007 a ete marquee comme appliquee.
echo.
echo Vous pouvez maintenant redemarrer l'application.
echo.
pause

