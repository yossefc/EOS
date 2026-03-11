@echo off
chcp 65001 >nul
cls

echo ================================================================
echo         MISE A JOUR EOS APRES GIT PULL
echo ================================================================
echo.
echo Ce script va :
echo   1. Mettre a jour les dependances Python (pip)
echo   2. Appliquer les migrations de base de donnees (alembic)
echo.

REM Chemin automatique : le dossier ou se trouve ce script
set EOS_DIR=%~dp0
set BACKEND_DIR=%EOS_DIR%backend
set VENV_PYTHON=%BACKEND_DIR%\venv\Scripts\python.exe
set VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate.bat

REM Verifier que le venv existe
if not exist "%VENV_PYTHON%" (
    echo [XX] Environnement virtuel Python introuvable : %VENV_PYTHON%
    echo [XX] Lance d'abord INSTALLER_EOS_DISTANT.ps1 pour configurer le poste.
    echo.
    pause
    exit /b 1
)

echo [--] Dossier EOS    : %EOS_DIR%
echo [--] Dossier backend: %BACKEND_DIR%
echo.

REM ================================================================
REM ETAPE 1 : Mise a jour des dependances Python
REM ================================================================
echo ================================================================
echo   ETAPE 1 : Mise a jour des dependances Python
echo ================================================================
echo.
echo [--] Installation / mise a jour des packages (pip)...
echo.

call "%VENV_ACTIVATE%"
cd /d "%BACKEND_DIR%"

pip install -r requirements.txt --quiet

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!!] pip install a signale des avertissements ou erreurs.
    echo [!!] Verifie les messages ci-dessus. On continue quand meme...
    echo.
) else (
    echo [OK] Dependances Python a jour.
)
echo.

REM ================================================================
REM ETAPE 2 : Migrations Alembic
REM ================================================================
echo ================================================================
echo   ETAPE 2 : Migrations de la base de donnees (Alembic)
echo ================================================================
echo.
echo [--] Application des nouvelles migrations...
echo.

alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [XX] Les migrations Alembic ont ECHOUE (code %ERRORLEVEL%).
    echo.
    echo     Causes possibles :
    echo       - PostgreSQL n'est pas demarre
    echo       - Les identifiants BDD sont incorrects dans .env
    echo       - Un conflit de migration existe
    echo.
    echo     Verifie le fichier : %BACKEND_DIR%\.env
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Migrations appliquees avec succes.
echo.

REM ================================================================
REM RESUME
REM ================================================================
echo ================================================================
echo              MISE A JOUR TERMINEE !
echo ================================================================
echo.
echo [OK] Dependances Python    : a jour
echo [OK] Schema base de donnees: a jour (alembic upgrade head)
echo.
echo Tu peux maintenant demarrer EOS avec DEMARRER_EOS_SIMPLE.bat
echo.
pause
