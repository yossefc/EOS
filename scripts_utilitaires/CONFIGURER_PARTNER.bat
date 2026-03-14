@echo off
cls

echo ================================================================
echo      Configuration automatique du client PARTNER
echo ================================================================
echo.
echo Ce script va :
echo   1. Creer le client PARTNER dans la base de donnees
echo   2. Creer le profil d'import Excel pour PARTNER
echo   3. Configurer tous les mappings de colonnes
echo.
echo Assurez-vous que PostgreSQL est demarre !
echo.
pause
echo.

cd /d D:\EOS

echo [1/2] Execution du script SQL...
echo.

REM Executer le script SQL
psql -U postgres -d eos_db -f CONFIGURER_PARTNER.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de la configuration
    echo.
    echo Verifiez que :
    echo   1. PostgreSQL est demarre
    echo   2. Le mot de passe est correct
    echo   3. La base de donnees eos_db existe
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo           Configuration PARTNER terminee !
echo ================================================================
echo.
echo Actions a faire maintenant :
echo   1. Redemarrer le backend (fermez et relancez)
echo   2. Recharger la page dans le navigateur (F5)
echo   3. Tester l'import PARTNER dans l'onglet Import
echo.
pause

