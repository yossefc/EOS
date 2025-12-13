@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Étape 4 - Installation du frontend EOS (npm)         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM Détection des chemins
REM ============================================================================
set "ROOT=%~dp0"
set "FRONTEND_DIR=%ROOT%frontend"

if not exist "%FRONTEND_DIR%" (
    echo ❌ ERREUR : Dossier frontend introuvable : %FRONTEND_DIR%
    echo  Vérifiez que le projet EOS est bien décompressé à cet endroit.
    echo.
    pause
    exit /b 1
)

REM Vérifier npm
where npm >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR : npm n'est pas installé ou n'est pas dans le PATH.
    echo  Installez Node.js (version LTS) depuis https://nodejs.org/
    echo  puis relancez ce script.
    echo.
    pause
    exit /b 1
)

echo ► Dossier frontend : %FRONTEND_DIR%
echo.

REM ============================================================================
REM Installation des dépendances npm
REM ============================================================================
cd /d "%FRONTEND_DIR%"

echo 📦 Installation des dépendances npm (npm install) ...
npm install
if errorlevel 1 (
    echo ❌ ERREUR : npm install a échoué.
    echo  Vérifiez votre connexion internet et réessayez.
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     ✅ Étape 4 terminée : frontend installé avec succès       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause


