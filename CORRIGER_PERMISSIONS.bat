@echo off
cls

echo ================================================================
echo      Correction des permissions PostgreSQL
echo ================================================================
echo.
echo Ce script va :
echo   1. Donner tous les droits a l'utilisateur postgres
echo   2. Corriger les permissions sur toutes les tables
echo   3. Corriger les permissions sur toutes les sequences
echo   4. Definir les permissions par defaut
echo.
pause
echo.

cd /d D:\EOS

echo Execution du script SQL...
echo.

psql -U postgres -d eos_db -f CORRIGER_PERMISSIONS.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de la correction des permissions
    pause
    exit /b 1
)

echo.
echo ================================================================
echo           Permissions corrigees avec succes !
echo ================================================================
echo.
echo Actions a faire maintenant :
echo   1. Redemarrer le backend (fermez et relancez)
echo   2. Tester l'import PARTNER
echo.
pause

