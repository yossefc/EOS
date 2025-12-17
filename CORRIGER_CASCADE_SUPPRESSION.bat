@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║      Correction de la contrainte de suppression CASCADE       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Définir DATABASE_URL
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
echo ✓ DATABASE_URL définie

REM Activer l'environnement virtuel
echo.
echo ► Activation de l'environnement virtuel...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo ✓ Environnement virtuel activé

REM Exécuter le script Python
echo.
echo ► Correction de la contrainte...
python backend\corriger_cascade_suppression.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de la correction
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ Correction terminée avec succès !              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant supprimer des dossiers sans erreur.
echo.
pause

