@echo off
chcp 65001 >nul
cls

echo ╔══════════════════════════════════════════════════════════╗
echo ║          APPLICATION EOS - PostgreSQL Mode              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set "BACKEND_DIR=%~dp0backend"
set "VENV_DIR=%BACKEND_DIR%\venv"

REM Vérifier que le venv existe
if not exist "%VENV_DIR%" (
    echo ❌ ERREUR : Environnement virtuel introuvable
    echo  Exécutez d'abord : .\02_installer_backend.bat
    echo.
    pause
    exit /b 1
)

echo ✓ Configuration PostgreSQL
echo   Base de données : eos_db@localhost:5432
echo.

echo 🚀 Démarrage du serveur Flask...
echo.

REM Aller dans le dossier backend
cd /d "%BACKEND_DIR%"

REM Activer le venv
call "%VENV_DIR%\Scripts\activate.bat"

REM Définir DATABASE_URL
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

REM Lancer l'application
echo ► Lancement de l'application...
python start_with_postgresql.py

REM Si l'application se ferme
echo.
pause

