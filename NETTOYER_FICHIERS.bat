@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║         Nettoyage des fichiers bloqués (fix 409/500)          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  Ce script va supprimer TOUS les fichiers importés et leurs données
echo.
echo Appuyez sur CTRL+C pour annuler, ou
pause

set "BACKEND_DIR=%~dp0backend"
set "VENV_DIR=%BACKEND_DIR%\venv"

echo.
echo ► Activation de l'environnement virtuel...
cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

python nettoyer_fichiers.py

if errorlevel 1 (
    echo.
    echo ❌ Échec du nettoyage
    pause
    exit /b 1
)

echo.
pause

