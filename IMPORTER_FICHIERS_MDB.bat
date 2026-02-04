@echo off
REM ============================================================================
REM Script d'import de fichiers MDB vers PostgreSQL
REM ============================================================================

echo.
echo ============================================================================
echo IMPORT DE FICHIERS MDB VERS POSTGRESQL
echo ============================================================================
echo.

REM Demander le code client
echo Clients disponibles :
echo   - PARTNER
echo   - RG_SHERLOCK
echo   - (autres clients configures)
echo.
set /p CLIENT_CODE="Entrez le code du client : "

if "%CLIENT_CODE%"=="" (
    echo.
    echo [ERREUR] Code client requis
    pause
    exit /b 1
)

echo.
REM Demander le chemin du fichier ou dossier
set /p MDB_PATH="Entrez le chemin du fichier .mdb ou du dossier : "

if not exist "%MDB_PATH%" (
    echo.
    echo [ERREUR] Chemin introuvable : %MDB_PATH%
    pause
    exit /b 1
)

echo.
REM Demander si mode test
set /p DRY_RUN="Mode test (sans insertion reelle) ? (O/N) : "

set DRY_RUN_FLAG=
if /i "%DRY_RUN%"=="O" set DRY_RUN_FLAG=--dry-run
if /i "%DRY_RUN%"=="OUI" set DRY_RUN_FLAG=--dry-run

echo.
echo ============================================================================
echo PARAMETRES DE L'IMPORT
echo ============================================================================
echo   Client      : %CLIENT_CODE%
echo   Chemin      : %MDB_PATH%
echo   Mode test   : %DRY_RUN%
echo ============================================================================
echo.

pause

echo.
echo Import en cours...
echo.

REM Vérifier si c'est un fichier ou un dossier
if exist "%MDB_PATH%\*" (
    REM C'est un dossier
    .venv\Scripts\python.exe backend\import_from_mdb.py --folder "%MDB_PATH%" --client-code %CLIENT_CODE% %DRY_RUN_FLAG%
) else (
    REM C'est un fichier
    .venv\Scripts\python.exe backend\import_from_mdb.py --file "%MDB_PATH%" --client-code %CLIENT_CODE% %DRY_RUN_FLAG%
)

if errorlevel 1 (
    echo.
    echo [ERREUR] L'import a echoue
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo IMPORT TERMINE
echo ============================================================================
echo.

if /i "%DRY_RUN%"=="O" (
    echo Mode test : Aucune donnee n'a ete inseree
    echo Pour un import reel, relancez sans le mode test
) else (
    echo Les donnees ont ete importees dans la base de donnees
    echo Verifiez dans l'interface web
)

echo.
pause
