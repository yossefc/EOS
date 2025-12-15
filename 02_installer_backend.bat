@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Étape 3 - Installation du backend EOS (Python)       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM Détection des chemins
REM ============================================================================
set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "VENV_DIR=%BACKEND_DIR%\venv"

if not exist "%BACKEND_DIR%" (
    echo ❌ ERREUR : Dossier backend introuvable : %BACKEND_DIR%
    echo  Vérifiez que le projet EOS est bien décompressé à cet endroit.
    echo.
    pause
    exit /b 1
)

REM Vérifier Python
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR : Python n'est pas installé ou n'est pas dans le PATH.
    echo  Installez Python 3.11+ depuis https://www.python.org/ et cochez
    echo  ^"Add Python to PATH^" pendant l'installation.
    echo.
    pause
    exit /b 1
)

echo ► Dossier backend : %BACKEND_DIR%
echo.

REM ============================================================================
REM 1) Création de l'environnement virtuel (venv) si nécessaire
REM ============================================================================
cd /d "%BACKEND_DIR%"

if exist "%VENV_DIR%" (
    echo ✅ Environnement virtuel déjà présent : %VENV_DIR%
) else (
    echo 📦 Création de l'environnement virtuel Python (venv) ...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERREUR : impossible de créer le venv.
        echo.
        pause
        exit /b 1
    )
    echo    ✅ venv créé.
)
echo.

REM ============================================================================
REM 2) Activation du venv et installation des dépendances
REM ============================================================================
echo 📦 Activation du venv et installation des dépendances (pip install) ...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ ERREUR : impossible d'activer le venv.
    echo.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ ERREUR : échec de la mise à jour de pip.
    echo.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERREUR : pip install -r requirements.txt a échoué.
    echo.
    pause
    exit /b 1
)
echo    ✅ Dépendances Python installées.
echo.

REM ============================================================================
REM 3) Configuration de DATABASE_URL et initialisation de la base
REM ============================================================================
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
setx DATABASE_URL "%DATABASE_URL%" >nul
echo 🔗 DATABASE_URL configurée pour ce système :
echo    %DATABASE_URL%
echo.

echo 🗄️ Initialisation / mise à jour de la base (fix_missing_columns.py) ...
python fix_missing_columns.py
if errorlevel 1 (
    echo ❌ ERREUR lors de l'exécution de fix_missing_columns.py.
    echo  Vérifiez que PostgreSQL est démarré et que la configuration est correcte.
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   ✅ Étape 3 terminée : backend installé et base initialisée  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause



