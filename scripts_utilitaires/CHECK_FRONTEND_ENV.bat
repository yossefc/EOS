@echo off
cls

echo ================================================================
echo    Verification environnement frontend (pre-build check)     
echo ================================================================
echo.

REM Detecter le repertoire du projet
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [CHECK 1/7] Repertoire du projet
echo Repertoire actuel : %CD%
echo.

if exist "frontend" (
    echo [OK] Dossier frontend/ existe
) else (
    echo [ERREUR] Dossier frontend/ INTROUVABLE !
    goto :error
)
echo.

echo [CHECK 2/7] Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installe !
    echo.
    echo Telechargez-le depuis : https://nodejs.org/
    goto :error
) else (
    for /f "tokens=*" %%v in ('node --version 2^>nul') do set NODE_VERSION=%%v
    echo [OK] Node.js !NODE_VERSION! detecte
)
echo.

echo [CHECK 3/7] npm
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] npm n'est pas installe !
    goto :error
) else (
    for /f "tokens=*" %%v in ('npm --version 2^>nul') do set NPM_VERSION=%%v
    echo [OK] npm !NPM_VERSION! detecte
)
echo.

echo [CHECK 4/7] package.json
if exist "frontend\package.json" (
    echo [OK] frontend/package.json existe
) else (
    echo [ERREUR] frontend/package.json INTROUVABLE !
    goto :error
)
echo.

echo [CHECK 5/7] Fichiers source
if exist "frontend\src" (
    echo [OK] frontend/src/ existe
    for /f %%a in ('dir /b /s frontend\src\*.jsx 2^>nul ^| find /c /v ""') do set JSX_COUNT=%%a
    echo    - !JSX_COUNT! fichiers .jsx trouves
) else (
    echo [ERREUR] frontend/src/ INTROUVABLE !
    goto :error
)
echo.

echo [CHECK 6/7] node_modules
if exist "frontend\node_modules" (
    echo [OK] frontend/node_modules/ existe
    echo    Dependencies deja installees
) else (
    echo [WARNING] frontend/node_modules/ n'existe pas
    echo    Les dependances devront etre installees
)
echo.

echo [CHECK 7/7] Scripts de build
cd frontend
for /f "tokens=*" %%s in ('npm run 2^>^&1 ^| findstr /C:"build"') do (
    echo [OK] Script 'npm run build' disponible
    goto :build_found
)
echo [WARNING] Script 'build' introuvable dans package.json
:build_found
cd ..
echo.

echo ================================================================
echo                  TOUS LES CHECKS PASSES !                  
echo ================================================================
echo.
echo Votre environnement est pret pour le build.
echo.
echo Vous pouvez maintenant executer :
echo    REBUILD_FRONTEND_ROBUSTE.bat
echo.
goto :end

:error
echo.
echo ================================================================
echo                     ERREUR DETECTEE                        
echo ================================================================
echo.
echo Veuillez corriger les erreurs ci-dessus avant de continuer.
echo.

:end
pause

