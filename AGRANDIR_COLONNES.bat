@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║      Agrandissement des colonnes PostgreSQL                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Se déplacer vers le répertoire du script
cd /d "%~dp0"

REM Activation de l'environnement virtuel
echo [1/2] Activation de l'environnement virtuel...
call backend\venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR : Environnement virtuel introuvable !
    echo    Chemin attendu : %CD%\backend\venv\Scripts\activate.bat
    echo    Exécutez d'abord : REPARER_VENV_AUTRE_ORDI.bat
    pause
    exit /b 1
)
echo.

REM Configuration de DATABASE_URL
echo [2/2] Configuration de DATABASE_URL...
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
echo.

REM Exécution du script
python backend\agrandir_colonnes.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║              ✅ Colonnes agrandies avec succès                ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo Vous pouvez maintenant :
    echo   1. Redémarrer l'application : DEMARRER_EOS_COMPLET.bat
    echo   2. Réessayer l'import de fichiers
) else (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║              ❌ Échec de l'agrandissement                     ║
    echo ╚════════════════════════════════════════════════════════════════╝
)

echo.
pause
