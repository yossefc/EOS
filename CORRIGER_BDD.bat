@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║      Diagnostic et correction de la base de données           ║
echo ╚════════════════════════════════════════════════════════════════╝
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

echo ► Activation de l'environnement virtuel...
cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
echo.

echo ► Configuration de DATABASE_URL...
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
echo.

echo ► Exécution du diagnostic et correction...
echo.
python reinit_complete_bdd.py

if errorlevel 1 (
    echo.
    echo ❌ La correction a échoué
    echo.
    echo Solutions possibles :
    echo   1. Vérifiez que PostgreSQL est démarré
    echo   2. Exécutez : .\EXECUTER_MIGRATIONS.bat
    echo   3. Vérifiez les logs ci-dessus pour plus de détails
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ Base de données corrigée                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant :
echo   1. Redémarrer le backend : DEMARRER_EOS_POSTGRESQL.bat
echo   2. Réessayer l'import de fichiers
echo.
pause

