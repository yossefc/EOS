@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║    RÉINITIALISATION COMPLÈTE - Solution FINALE                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Ce script va :
echo   1. Créer/vérifier le client EOS
echo   2. Créer/vérifier le profil d'import
echo   3. SUPPRIMER tous les anciens mappings incorrects
echo   4. CRÉER les VRAIS mappings depuis utils.py
echo.
pause

set "BACKEND_DIR=D:\EOS\backend"
set "VENV_DIR=%BACKEND_DIR%\venv"

echo.
echo ► Activation de l'environnement virtuel...
cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo ► Configuration de DATABASE_URL...
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"

echo ► Réinitialisation complète...
python reinit_complete_bdd.py

if errorlevel 1 (
    echo.
    echo ❌ Échec de la réinitialisation
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                       ✅ TOUT EST PRÊT !                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo PROCHAINES ÉTAPES :
echo   1. Redémarrez le backend (DEMARRER_EOS_POSTGRESQL.bat)
echo   2. Testez l'import d'un fichier TXT
echo.
echo Si l'import ne marche toujours pas, lancez d'abord :
echo   NETTOYER_FICHIERS.bat
echo.
pause

