@echo off
chcp 65001 >nul
echo.
echo ========================================
echo Migration PostgreSQL pour CLIENT_X
echo ========================================
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

REM Exécution de la migration
echo [2/2] Ajout des colonnes CLIENT_X dans PostgreSQL...
python backend\ajouter_colonnes_client_x.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ La migration a échoué !
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Migration réussie !
echo ========================================
echo.
echo Les colonnes CLIENT_X ont été ajoutées à la base de données.
echo Vous pouvez maintenant exécuter : INSTALLER_CLIENT_X.bat
echo.
pause

