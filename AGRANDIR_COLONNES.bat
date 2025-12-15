@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║      Agrandissement des colonnes PostgreSQL (fix import)      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set "BACKEND_DIR=%~dp0backend"
set "VENV_DIR=%BACKEND_DIR%\venv"

echo ► Activation de l'environnement virtuel...
cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
echo.

echo ► Configuration de DATABASE_URL...
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
echo.

echo ► Agrandissement des colonnes...
python agrandir_colonnes.py

if errorlevel 1 (
    echo.
    echo ❌ Échec de l'agrandissement
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ Colonnes agrandies avec succès                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant :
echo   1. Redémarrer le backend : DEMARRER_EOS_POSTGRESQL.bat
echo   2. Réessayer l'import de fichiers
echo.
pause

