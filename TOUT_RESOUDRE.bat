@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║         🚀 RÉSOLUTION COMPLÈTE - Tous les problèmes d'import                 ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo Ce script va résoudre TOUS les problèmes rencontrés :
echo   1. Installer openpyxl (lecture Excel)
echo   2. Agrandir les colonnes (VARCHAR 32 → 255)
echo   3. Ajouter les colonnes CLIENT_X
echo.
echo ⏱️  Temps total : environ 2 minutes
echo.
pause
echo.

REM Se déplacer vers le répertoire du script
cd /d "%~dp0"

REM ============================================================================
REM ÉTAPE 1 : Installer openpyxl
REM ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  ÉTAPE 1/3 : Installation de openpyxl                             ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

call backend\venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR : Environnement virtuel introuvable !
    echo    Exécutez d'abord : REPARER_VENV_AUTRE_ORDI.bat
    pause
    exit /b 1
)

pip install openpyxl
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Échec de l'installation de openpyxl
    pause
    exit /b 1
)
echo   ✅ openpyxl installé

REM ============================================================================
REM ÉTAPE 2 : Agrandir les colonnes
REM ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  ÉTAPE 2/3 : Agrandissement des colonnes PostgreSQL               ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
python backend\agrandir_colonnes.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Échec de l'agrandissement des colonnes
    pause
    exit /b 1
)

REM ============================================================================
REM ÉTAPE 3 : Ajouter les colonnes CLIENT_X
REM ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  ÉTAPE 3/3 : Ajout des colonnes CLIENT_X                          ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

python backend\ajouter_colonnes_client_x.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Échec de l'ajout des colonnes CLIENT_X
    pause
    exit /b 1
)

REM ============================================================================
REM SUCCÈS
REM ============================================================================
echo.
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                    ✅ TOUS LES PROBLÈMES RÉSOLUS !                           ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo Ce qui a été fait :
echo   ✅ openpyxl installé (lecture de fichiers Excel)
echo   ✅ 29 colonnes agrandies (VARCHAR 32 → 255)
echo   ✅ 5 colonnes CLIENT_X ajoutées (tarif_lettre, recherche, etc.)
echo.
echo 🎯 PROCHAINE ÉTAPE :
echo   1. Retournez dans l'interface web (http://localhost:5000)
echo   2. Réessayez l'import de votre fichier Excel
echo   3. ✅ L'import devrait maintenant fonctionner !
echo.
echo ⚠️  Note : Vous n'avez PAS besoin de redémarrer l'application
echo.
pause


