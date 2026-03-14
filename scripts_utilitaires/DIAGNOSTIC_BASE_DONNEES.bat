@echo off
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║       DIAGNOSTIC COMPLET DE LA BASE DE DONNEES EOS            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Ce script va generer un rapport complet de l'etat de la base :
echo.
echo   - Version des migrations Alembic
echo   - Tables existantes
echo   - Relations (Foreign Keys)
echo   - Index
echo   - Clients configures
echo   - Profils d'import
echo   - Tarifs
echo   - Colonnes critiques
echo   - Statistiques generales
echo.
pause
echo.

cd /d D:\EOS

echo Execution du diagnostic...
echo.

psql -U postgres -d eos_db -f DIAGNOSTIC_BASE_DONNEES.sql > RAPPORT_DIAGNOSTIC.txt 2>&1

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors du diagnostic
    echo Verifiez que PostgreSQL est demarre et que la base eos_db existe
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              DIAGNOSTIC TERMINE AVEC SUCCES                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Le rapport complet a ete enregistre dans :
echo    RAPPORT_DIAGNOSTIC.txt
echo.
echo Vous pouvez :
echo   1. Consulter le rapport : notepad RAPPORT_DIAGNOSTIC.txt
echo   2. L'envoyer par email pour support
echo   3. Le comparer avec l'autre ordinateur
echo.
pause

REM Ouvrir automatiquement le rapport
notepad RAPPORT_DIAGNOSTIC.txt

