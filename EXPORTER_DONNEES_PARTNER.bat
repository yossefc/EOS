@echo off
cls

echo ================================================================
echo     EXPORT DES DONNEES PARTNER (Ordinateur SOURCE)         
echo ================================================================
echo.
echo Ce script va exporter toutes les donnees PARTNER :
echo   - Tarifs PARTNER (table tarifs_client)
echo   - Options de confirmation
echo   - Regles tarifaires
echo.
echo Ces donnees seront exportees dans des fichiers .sql
echo que vous pourrez copier sur l'autre ordinateur.
echo.
pause
echo.

cd /d D:\EOS

echo Execution de l'export...
echo.

psql -U postgres -d eos_db -f EXPORTER_DONNEES_PARTNER.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'export
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              EXPORT TERMINE AVEC SUCCES !           
echo ================================================================
echo.
echo Fichiers crees :
echo   1. PARTNER_TARIFS_EXPORT.sql
echo   2. PARTNER_CONFIRMATION_EXPORT.sql
echo   3. PARTNER_TARIF_RULES_EXPORT.sql
echo.
echo PROCHAINES ETAPES :
echo.
echo 1. Copiez ces 3 fichiers SQL sur l'autre ordinateur
echo    Destination : D:\eos\
echo.
echo 2. Sur l'autre ordinateur, executez :
echo    IMPORTER_DONNEES_PARTNER.bat
echo.
pause

