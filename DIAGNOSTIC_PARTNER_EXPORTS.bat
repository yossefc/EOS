@echo off
cls

echo ================================================================
echo      DIAGNOSTIC DES EXPORTS PARTNER
echo ================================================================
echo.
echo Ce script va analyser les enquetes Partner validees
echo et identifier pourquoi elles vont toutes dans "Enquetes Positives"
echo.
pause
echo.

cd /d D:\EOS

echo Execution du diagnostic SQL...
echo.

SET PGPASSWORD=elsih26
psql -U postgres -d eos_db -f DIAGNOSTIC_EXPORTS_PARTNER.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'execution du diagnostic
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo           Diagnostic termine !
echo ================================================================
echo.
echo Analysez les resultats ci-dessus pour identifier le probleme :
echo.
echo - Si "SANS CODE" apparait : les enquetes n'ont pas de code resultat
echo - Si "Contestations non marquees" liste des enquetes : le flag est incorrect
echo.
pause

