@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   🚀 DÉMARRAGE EOS                            ║
echo ║          Application de Gestion des Enquêtes                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM Configuration
REM ============================================================
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
set FRONTEND_URL=http://localhost:5173
set BACKEND_PORT=5000

REM ============================================================
REM Vérifications préliminaires
REM ============================================================
echo [1/5] 🔍 Vérification de l'environnement...

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Téléchargez Python depuis: https://www.python.org/downloads/
    echo ⚠️  N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    pause
    exit /b 1
)
echo    ✅ Python trouvé

REM Vérifier Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERREUR: Node.js n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Téléchargez Node.js depuis: https://nodejs.org/
    pause
    exit /b 1
)
echo    ✅ Node.js trouvé

REM Vérifier que les dossiers existent
if not exist "%BACKEND_DIR%" (
    echo ❌ ERREUR: Dossier backend introuvable: %BACKEND_DIR%
    pause
    exit /b 1
)
if not exist "%FRONTEND_DIR%" (
    echo ❌ ERREUR: Dossier frontend introuvable: %FRONTEND_DIR%
    pause
    exit /b 1
)
echo    ✅ Dossiers backend et frontend trouvés
echo.

REM ============================================================
REM Vérifier les dépendances
REM ============================================================
echo [2/5] 📦 Vérification des dépendances...

REM Vérifier les dépendances Python
if not exist "%BACKEND_DIR%\venv" (
    echo    ⚠️  Environnement virtuel Python non trouvé
    echo    Vous devriez créer un venv: python -m venv backend\venv
) else (
    echo    ✅ Environnement virtuel Python trouvé
)

REM Vérifier les dépendances npm
if not exist "%FRONTEND_DIR%\node_modules" (
    echo    ⚠️  node_modules non trouvé dans le frontend
    echo    ℹ️  Installation des dépendances npm...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if %errorlevel% neq 0 (
        echo    ❌ Erreur lors de l'installation des dépendances npm
        pause
        exit /b 1
    )
    cd /d "%~dp0"
) else (
    echo    ✅ node_modules trouvé
)
echo.

REM ============================================================
REM Démarrer le Backend
REM ============================================================
echo [3/5] 🔧 Démarrage du Backend (Flask)...

REM Créer un fichier temporaire pour démarrer le backend
echo @echo off > "%TEMP%\eos_backend.bat"
echo title EOS Backend (Flask) >> "%TEMP%\eos_backend.bat"
echo cd /d "%BACKEND_DIR%" >> "%TEMP%\eos_backend.bat"
echo set DATABASE_URL=%DATABASE_URL% >> "%TEMP%\eos_backend.bat"
echo echo ✓ DATABASE_URL définie >> "%TEMP%\eos_backend.bat"
echo echo. >> "%TEMP%\eos_backend.bat"
echo python start_with_postgresql.py >> "%TEMP%\eos_backend.bat"
echo pause >> "%TEMP%\eos_backend.bat"

REM Lancer le backend dans une nouvelle fenêtre
start "EOS Backend" cmd /k "%TEMP%\eos_backend.bat"

echo    ✅ Backend lancé dans une nouvelle fenêtre
echo    📍 URL: http://localhost:%BACKEND_PORT%
echo.

REM Attendre que le backend démarre
echo    ⏳ Attente du démarrage du backend (5 secondes)...
timeout /t 5 /nobreak >nul
echo.

REM ============================================================
REM Démarrer le Frontend
REM ============================================================
echo [4/5] 🎨 Démarrage du Frontend (Vite)...

REM Créer un fichier temporaire pour démarrer le frontend
echo @echo off > "%TEMP%\eos_frontend.bat"
echo title EOS Frontend (Vite) >> "%TEMP%\eos_frontend.bat"
echo cd /d "%FRONTEND_DIR%" >> "%TEMP%\eos_frontend.bat"
echo npm run dev >> "%TEMP%\eos_frontend.bat"
echo pause >> "%TEMP%\eos_frontend.bat"

REM Lancer le frontend dans une nouvelle fenêtre
start "EOS Frontend" cmd /k "%TEMP%\eos_frontend.bat"

echo    ✅ Frontend lancé dans une nouvelle fenêtre
echo    📍 URL: %FRONTEND_URL%
echo.

REM Attendre que le frontend démarre
echo    ⏳ Attente du démarrage du frontend (8 secondes)...
timeout /t 8 /nobreak >nul
echo.

REM ============================================================
REM Ouvrir le navigateur
REM ============================================================
echo [5/5] 🌐 Ouverture du navigateur...

start "" "%FRONTEND_URL%"

echo    ✅ Navigateur ouvert
echo.

REM ============================================================
REM Résumé
REM ============================================================
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ DÉMARRAGE TERMINÉ                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📊 Services démarrés:
echo    🔧 Backend Flask  : http://localhost:%BACKEND_PORT%
echo    🎨 Frontend Vite  : %FRONTEND_URL%
echo.
echo 💡 Conseils:
echo    • Ne fermez pas les fenêtres Backend et Frontend
echo    • Pour arrêter l'application, appuyez sur Ctrl+C dans chaque fenêtre
echo    • Les logs s'affichent dans les fenêtres Backend et Frontend
echo.
echo 🔄 Pour redémarrer l'application, double-cliquez à nouveau sur start_eos.bat
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              Appuyez sur une touche pour quitter              ║
echo ╚════════════════════════════════════════════════════════════════╝

pause >nul
exit /b 0


