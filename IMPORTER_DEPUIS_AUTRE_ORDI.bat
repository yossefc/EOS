@echo off
cls

echo ================================================================
echo     SYNCHRONISATION - Ordinateur CIBLE                        
echo ================================================================
echo.
echo Ce script va importer TOUTES les donnees depuis l'autre ordinateur.
echo.
echo IMPORTANT : Executez ce script sur l'ordinateur CIBLE
echo            (celui qui doit recevoir les donnees)
echo.
echo PREREQUIS :
echo   Les 5 fichiers SQL doivent etre dans ce dossier :
echo   - TOUS_CLIENTS_EXPORT.sql
echo   - TOUS_TARIFS_EXPORT.sql
echo   - TOUS_PROFILS_IMPORT_EXPORT.sql
echo   - TOUS_MAPPINGS_IMPORT_EXPORT.sql
echo   - TOUTES_REGLES_TARIFAIRES_EXPORT.sql
echo.
pause
echo.

cd /d D:\EOS

REM Verifier que les fichiers existent
if not exist "TOUS_CLIENTS_EXPORT.sql" (
    echo [ERREUR] Fichier TOUS_CLIENTS_EXPORT.sql introuvable !
    echo.
    echo Copiez d'abord les fichiers SQL depuis l'autre ordinateur.
    echo.
    pause
    exit /b 1
)

if not exist "TOUS_TARIFS_EXPORT.sql" (
    echo [ERREUR] Fichier TOUS_TARIFS_EXPORT.sql introuvable !
    pause
    exit /b 1
)

if not exist "TOUS_PROFILS_IMPORT_EXPORT.sql" (
    echo [ERREUR] Fichier TOUS_PROFILS_IMPORT_EXPORT.sql introuvable !
    pause
    exit /b 1
)

if not exist "TOUS_MAPPINGS_IMPORT_EXPORT.sql" (
    echo [ERREUR] Fichier TOUS_MAPPINGS_IMPORT_EXPORT.sql introuvable !
    pause
    exit /b 1
)

if not exist "TOUTES_REGLES_TARIFAIRES_EXPORT.sql" (
    echo [ERREUR] Fichier TOUTES_REGLES_TARIFAIRES_EXPORT.sql introuvable !
    pause
    exit /b 1
)

echo [OK] Tous les fichiers SQL sont presents
echo.

echo [1/5] Import de tous les clients (incluant Sherlock)...
echo.
psql -U postgres -d eos_db -f TOUS_CLIENTS_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des clients
    pause
    exit /b 1
)

echo [OK] Clients importes
echo.

echo [2/5] Import de tous les profils d'import...
echo.
psql -U postgres -d eos_db -f TOUS_PROFILS_IMPORT_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des profils
    pause
    exit /b 1
)

echo [OK] Profils importes
echo.

echo [3/5] Import de tous les mappings...
echo.
psql -U postgres -d eos_db -f TOUS_MAPPINGS_IMPORT_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des mappings
    pause
    exit /b 1
)

echo [OK] Mappings importes
echo.

echo [4/5] Import de tous les tarifs...
echo.
psql -U postgres -d eos_db -f TOUS_TARIFS_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des tarifs
    pause
    exit /b 1
)

echo [OK] Tarifs importes
echo.

echo [5/5] Import de toutes les regles tarifaires...
echo.
psql -U postgres -d eos_db -f TOUTES_REGLES_TARIFAIRES_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des regles
    pause
    exit /b 1
)

echo [OK] Regles importees
echo.

echo.
echo ================================================================
echo         IMPORT TERMINE AVEC SUCCES !           
echo ================================================================
echo.
echo Toutes les donnees ont ete importees :
echo   - Tous les clients (PARTNER, Sherlock, etc.)
echo   - Tous les tarifs
echo   - Tous les profils d'import
echo   - Tous les mappings
echo   - Toutes les regles tarifaires
echo.
echo PROCHAINE ETAPE :
echo ================
echo 1. Redemarrez l'application : DEMARRER_EOS_SIMPLE.bat
echo.
echo 2. Pour permettre l'acces a distance, voir :
echo    GUIDE_ACCES_RESEAU.txt
echo.
pause

