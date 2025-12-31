@echo off
cls

echo ================================================================
echo      Verification de la base de donnees EOS
echo ================================================================
echo.
echo Ce script va verifier :
echo   1. Toutes les tables necessaires sont presentes
echo   2. Les clients (EOS, PARTNER) sont configures
echo   3. Les profils d'import sont crees
echo   4. Les colonnes PARTNER existent dans la table donnees
echo   5. La version des migrations
echo.
pause
echo.

cd /d D:\EOS

echo Execution du script de verification...
echo.

psql -U postgres -d eos_db -f VERIFIER_BASE_DONNEES.sql

echo.
echo ================================================================
echo           Verification terminee
echo ================================================================
echo.
echo Si des tables sont manquantes, executez :
echo   - APPLIQUER_MIGRATIONS_SIMPLE.bat (pour les migrations)
echo   - CONFIGURER_PARTNER.bat (pour le client PARTNER)
echo.
pause

