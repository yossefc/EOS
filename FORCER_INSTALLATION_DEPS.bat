@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║     Installation manuelle des dépendances (mode forcé)       ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

cd /d D:\EOS\backend

echo Activation du venv...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Le venv n'existe pas
    echo Lancez d'abord : RECREER_VENV.bat EN TANT QU'ADMINISTRATEUR
    pause
    exit /b 1
)
echo ✓ Venv activé
echo.

echo Installation des dépendances avec options spéciales...
echo (ignore le cache, force la réinstallation, utilise un répertoire temporaire différent)
echo.

pip install --no-cache-dir --upgrade --force-reinstall -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERREUR persistante
    echo.
    echo Dernière solution :
    echo   1. Fermez TOUS les programmes (IDE, antivirus, etc.)
    echo   2. Redémarrez votre ordinateur
    echo   3. Lancez ce script EN TANT QU'ADMINISTRATEUR
    echo.
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                  ✅ Installation réussie !                    ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
pause

