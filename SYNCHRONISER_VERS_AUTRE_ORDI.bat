@echo off
cls

echo ================================================================
echo     SYNCHRONISATION - Ordinateur SOURCE                        
echo ================================================================
echo.
echo Ce script va exporter TOUTES les donnees vers l'autre ordinateur :
echo   - Tous les clients (PARTNER, Sherlock, etc.)
echo   - Tous les tarifs
echo   - Toutes les regles tarifaires
echo   - Tous les mappings d'import
echo   - Tous les profils d'import
echo.
echo IMPORTANT : Executez ce script sur l'ordinateur SOURCE
echo            (celui qui a toutes les donnees)
echo.
pause
echo.

cd /d D:\EOS

echo [1/5] Export de tous les clients...
echo.
psql -U postgres -d eos_db -f EXPORT_TOUS_CLIENTS.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'export des clients
    pause
    exit /b 1
)

echo [OK] Clients exportes
echo.

echo [2/5] Export de tous les tarifs...
echo.
psql -U postgres -d eos_db -f EXPORT_TOUS_TARIFS.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'export des tarifs
    pause
    exit /b 1
)

echo [OK] Tarifs exportes
echo.

echo [3/5] Export de tous les profils d'import...
echo.
psql -U postgres -d eos_db -f EXPORT_PROFILS_IMPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'export des profils
    pause
    exit /b 1
)

echo [OK] Profils exportes
echo.

echo [4/5] Export de tous les mappings...
echo.
psql -U postgres -d eos_db -f EXPORT_MAPPINGS_IMPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'export des mappings
    pause
    exit /b 1
)

echo [OK] Mappings exportes
echo.

echo [5/5] Export des regles tarifaires...
echo.
psql -U postgres -d eos_db -f EXPORT_REGLES_TARIFAIRES.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'export des regles
    pause
    exit /b 1
)

echo [OK] Regles exportees
echo.

echo.
echo ================================================================
echo         EXPORT TERMINE AVEC SUCCES !           
echo ================================================================
echo.
echo Fichiers crees dans D:\EOS\ :
echo   1. TOUS_CLIENTS_EXPORT.sql
echo   2. TOUS_TARIFS_EXPORT.sql
echo   3. TOUS_PROFILS_IMPORT_EXPORT.sql
echo   4. TOUS_MAPPINGS_IMPORT_EXPORT.sql
echo   5. TOUTES_REGLES_TARIFAIRES_EXPORT.sql
echo.
echo PROCHAINE ETAPE :
echo ================
echo 1. Copiez ces 5 fichiers SQL sur l'autre ordinateur dans D:\EOS\
echo.
echo 2. Sur l'autre ordinateur, executez : IMPORTER_DEPUIS_AUTRE_ORDI.bat
echo.
echo 3. Pour acceder a distance, voir le fichier :
echo    GUIDE_ACCES_RESEAU.txt
echo.
pause

