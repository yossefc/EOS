@echo off
REM ============================================================================
REM Script d'import batch de fichiers Excel vers PostgreSQL
REM ============================================================================

echo.
echo ============================================================================
echo IMPORT BATCH DE FICHIERS EXCEL
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
REM Demander le chemin du dossier
set /p FOLDER_PATH="Entrez le chemin du dossier contenant les fichiers Excel : "

if not exist "%FOLDER_PATH%" (
    echo.
    echo [ERREUR] Dossier introuvable : %FOLDER_PATH%
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
echo   Dossier     : %FOLDER_PATH%
echo   Mode test   : %DRY_RUN%
echo ============================================================================
echo.

echo Import en cours...
echo.

.venv\Scripts\python.exe backend\import_excel_batch.py --folder "%FOLDER_PATH%" --client-code %CLIENT_CODE% %DRY_RUN_FLAG%

if errorlevel 1 (
    echo.
    echo [ERREUR] L'import a echoue
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo IMPORT BATCH TERMINE
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
