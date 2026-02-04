@echo off
REM ============================================================================
REM Script d'analyse de la structure des fichiers MDB
REM ============================================================================

echo.
echo ============================================================================
echo ANALYSEUR DE STRUCTURE MDB
echo ============================================================================
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
echo Verification des pilotes ODBC...
.venv\Scripts\python.exe backend\analyze_mdb_structure.py --test-connection

if errorlevel 1 (
    echo.
    echo [ERREUR] Pilotes ODBC non disponibles
    echo.
    echo INSTALLATION REQUISE :
    echo   Telechargez et installez :
    echo   Microsoft Access Database Engine 2016 Redistributable
    echo   https://www.microsoft.com/en-us/download/details.aspx?id=54920
    echo.
    pause
    exit /b 1
)

echo.
echo Analyse en cours...
echo.

REM Vérifier si c'est un fichier ou un dossier
if exist "%MDB_PATH%\*" (
    REM C'est un dossier
    .venv\Scripts\python.exe backend\analyze_mdb_structure.py --folder "%MDB_PATH%"
) else (
    REM C'est un fichier
    .venv\Scripts\python.exe backend\analyze_mdb_structure.py --file "%MDB_PATH%"
)

if errorlevel 1 (
    echo.
    echo [ERREUR] L'analyse a echoue
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo ANALYSE TERMINEE
echo ============================================================================
echo.
echo Les rapports JSON ont ete crees dans le dossier actuel.
echo Consultez ces fichiers pour voir la structure des tables MDB.
echo.

pause
