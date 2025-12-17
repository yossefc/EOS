@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    Agrandissement de la colonne elements_retrouves            ║
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
echo ► Agrandissement de la colonne...
python backend\agrandir_elements_retrouves.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de l'agrandissement
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ Colonne agrandie avec succès !                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant utiliser des textes longs pour
echo "Confirmation par qui" (jusqu'à 255 caractères).
echo.
pause

