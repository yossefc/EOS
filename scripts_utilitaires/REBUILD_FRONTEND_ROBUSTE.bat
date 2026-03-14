@echo off
setlocal enabledelayedexpansion
cls

echo ================================================================
echo        Reconstruction du frontend (version robuste)         
echo ================================================================
echo.

REM Detecter le repertoire du projet
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [INFO] Repertoire du projet : %CD%
echo.

REM Verifier que le dossier frontend existe
if not exist "frontend" (
    echo.
    echo [ERREUR] Le dossier 'frontend' n'existe pas !
    echo.
    echo Repertoire actuel : %CD%
    echo.
    echo Contenu du repertoire :
    dir /b
    echo.
    echo Verifiez que vous etes bien dans le bon repertoire.
    echo.
    pause
    exit /b 1
)

echo [OK] Dossier frontend trouve
echo.

REM Se deplacer dans le dossier frontend
cd frontend

echo [INFO] Repertoire frontend : %CD%
echo.

REM Verifier que npm est installe
echo [1/4] Verification de Node.js et npm...
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERREUR] npm n'est pas installe ou n'est pas dans le PATH !
    echo.
    echo Veuillez installer Node.js depuis : https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('npm --version 2^>nul') do set NPM_VERSION=%%v
for /f "tokens=*" %%v in ('node --version 2^>nul') do set NODE_VERSION=%%v

echo [OK] Node.js %NODE_VERSION% detecte
echo [OK] npm %NPM_VERSION% detecte
echo.

REM Verifier que package.json existe
if not exist "package.json" (
    echo.
    echo [ERREUR] Le fichier package.json n'existe pas dans frontend/
    echo.
    pause
    exit /b 1
)

echo [OK] package.json trouve
echo.

REM Installation des dependances
echo [2/4] Installation des dependances npm...
echo (cela peut prendre quelques minutes la premiere fois)
echo.

npm install
if errorlevel 1 (
    echo.
    echo [ERREUR] Impossible d'installer les dependances npm
    echo.
    echo Erreur detectee. Verifiez les messages ci-dessus.
    echo.
    echo Solutions possibles :
    echo   1. Supprimer node_modules et reessayer
    echo   2. Verifier votre connexion internet
    echo   3. Executer en tant qu'administrateur
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependances installees avec succes
echo.

REM Nettoyage de l'ancien build
echo [3/4] Nettoyage de l'ancien build...
echo.

if exist "dist" (
    rmdir /s /q dist 2>nul
    if exist "dist" (
        echo [WARNING] Impossible de supprimer dist/ (fichiers verrouilles?)
        echo Tentative de suppression des fichiers individuellement...
        del /f /s /q dist\* 2>nul
    ) else (
        echo [OK] Ancien build supprime
    )
) else (
    echo [INFO] Pas d'ancien build a supprimer
)
echo.

REM Build du frontend
echo [4/4] Build du nouveau frontend...
echo (cela peut prendre 30-60 secondes)
echo.

npm run build
set BUILD_RESULT=%errorlevel%

echo.

if %BUILD_RESULT% neq 0 (
    echo.
    echo [ERREUR] Le build a echoue (code erreur: %BUILD_RESULT%)
    echo.
    echo Verifiez les messages d'erreur ci-dessus.
    echo.
    echo Solutions possibles :
    echo   1. Verifier qu'il n'y a pas d'erreurs de syntaxe dans le code
    echo   2. Supprimer node_modules et reessayer
    echo   3. Verifier que tous les imports sont corrects
    echo.
    pause
    exit /b 1
)

REM Verification que dist/ a ete cree
if not exist "dist" (
    echo.
    echo [ERREUR] Le dossier dist/ n'a pas ete cree !
    echo.
    echo Le build semble avoir echoue silencieusement.
    echo.
    pause
    exit /b 1
)

echo [OK] Build termine avec succes
echo.

REM Compter les fichiers generes
for /f %%a in ('dir /b /s dist 2^>nul ^| find /c /v ""') do set FILE_COUNT=%%a

echo.
echo ================================================================
echo              FRONTEND RECONSTRUIT AVEC SUCCES !           
echo ================================================================
echo.
echo Fichiers generes dans dist/ : %FILE_COUNT%
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  IMPORTANT : ACTIONS A FAIRE MAINTENANT                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. FERMEZ TOUTES les fenetres du navigateur
echo.
echo 2. Relancez l'application :
echo    DEMARRER_EOS_SIMPLE.bat
echo.
echo 3. Ouvrez dans le navigateur :
echo    http://localhost:5173
echo.
echo 4. Videz le cache du navigateur :
echo    - Chrome/Edge : Ctrl + Shift + R
echo    - Firefox : Ctrl + F5
echo    - Ou : F12 ^> Reseau ^> Desactiver le cache
echo.
echo 5. Si ca ne marche toujours pas :
echo    - Parametres du navigateur ^> Confidentialite
echo    - Effacer les donnees de navigation
echo    - Cocher : Cache, Cookies
echo    - Periode : Derniere heure
echo.
echo ================================================================
echo.
pause

