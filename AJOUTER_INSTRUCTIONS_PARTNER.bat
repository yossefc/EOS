@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        Ajout du champ INSTRUCTIONS pour PARTNER               ║
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
echo ► Ajout de la colonne 'instructions'...
python backend\ajouter_instructions_partner.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de l'ajout de la colonne
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ Colonne ajoutée avec succès !                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause


