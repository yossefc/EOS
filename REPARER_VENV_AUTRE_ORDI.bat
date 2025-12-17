@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║       Réparation du venv Python (autre ordinateur)            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Ce script va :
echo   1. Supprimer l'ancien venv cassé
echo   2. Créer un nouveau venv
echo   3. Installer les dépendances
echo.
pause

set "BACKEND_DIR=D:\EOS\backend"

echo.
echo ► Suppression de l'ancien venv...
cd /d "%BACKEND_DIR%"
if exist venv (
    rmdir /s /q venv
    echo   ✅ Ancien venv supprimé
) else (
    echo   ⚠️  Pas de venv à supprimer
)

echo.
echo ► Vérification de Python...
python --version
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo ► Création du nouveau venv...
python -m venv venv
if errorlevel 1 (
    echo ❌ Échec de la création du venv
    pause
    exit /b 1
)
echo   ✅ Nouveau venv créé

echo.
echo ► Activation du venv...
call venv\Scripts\activate.bat

echo.
echo ► Installation des dépendances...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Échec de l'installation des dépendances
    pause
    exit /b 1
)
echo   ✅ Dépendances installées

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  ✅ VENV RÉPARÉ !                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Le backend est maintenant prêt.
echo.
echo PROCHAINES ÉTAPES :
echo   1. Lance : CORRIGER_BDD.bat
echo   2. Lance : REINIT_COMPLETE_BDD.bat
echo   3. Lance : DEMARRER_EOS_POSTGRESQL.bat
echo.
pause


