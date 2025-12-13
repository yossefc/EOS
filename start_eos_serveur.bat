@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║               EOS - MODE SERVEUR (Multi-utilisateurs)         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM Configuration du serveur
REM ============================================================
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db

REM ============================================================
REM Détection de l'adresse IP du serveur
REM ============================================================
echo [1/4] 🔍 Détection de l'adresse IP du serveur...

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP_TEMP=%%a
    goto :ip_found
)
:ip_found
set IP_SERVEUR=%IP_TEMP:~1%
echo    ✅ Adresse IP détectée : %IP_SERVEUR%
echo.

REM ============================================================
REM Vérifications
REM ============================================================
echo [2/4] 🔍 Vérification de l'environnement...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ ERREUR: Python n'est pas installé
    pause
    exit /b 1
)
echo    ✅ Python trouvé

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ ERREUR: Node.js n'est pas installé
    pause
    exit /b 1
)
echo    ✅ Node.js trouvé
echo.

REM ============================================================
REM Compilation du frontend (optionnel - pour mode production)
REM ============================================================
echo [3/4] 🎨 Vérification du frontend compilé...

if exist "%FRONTEND_DIR%\dist" (
    echo    ✅ Frontend déjà compilé (dist/ existe)
) else (
    echo    ⚠️  Frontend non compilé
    echo    ℹ️  Le frontend sera lancé en mode développement
)
echo.

REM ============================================================
REM Démarrage du backend en mode serveur
REM ============================================================
echo [4/4] 🔧 Démarrage du serveur backend...

echo @echo off > "%TEMP%\eos_backend_serveur.bat"
echo title EOS Backend - SERVEUR >> "%TEMP%\eos_backend_serveur.bat"
echo cd /d "%BACKEND_DIR%" >> "%TEMP%\eos_backend_serveur.bat"
echo set DATABASE_URL=%DATABASE_URL% >> "%TEMP%\eos_backend_serveur.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_serveur.bat"
echo echo    EOS SERVEUR BACKEND >> "%TEMP%\eos_backend_serveur.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_serveur.bat"
echo echo. >> "%TEMP%\eos_backend_serveur.bat"
echo echo ✓ Mode : SERVEUR (accessible depuis le réseau) >> "%TEMP%\eos_backend_serveur.bat"
echo echo ✓ Adresse IP : %IP_SERVEUR% >> "%TEMP%\eos_backend_serveur.bat"
echo echo. >> "%TEMP%\eos_backend_serveur.bat"
echo echo Les clients peuvent se connecter via : >> "%TEMP%\eos_backend_serveur.bat"
echo echo   http://%IP_SERVEUR%:5000 >> "%TEMP%\eos_backend_serveur.bat"
echo echo. >> "%TEMP%\eos_backend_serveur.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_serveur.bat"
echo echo. >> "%TEMP%\eos_backend_serveur.bat"
echo python start_with_postgresql.py >> "%TEMP%\eos_backend_serveur.bat"
echo pause >> "%TEMP%\eos_backend_serveur.bat"

start "EOS Backend - SERVEUR" cmd /k "%TEMP%\eos_backend_serveur.bat"

echo    ✅ Backend serveur lancé
echo.

timeout /t 3 /nobreak >nul

REM ============================================================
REM Démarrage optionnel du frontend
REM ============================================================
choice /C ON /N /M "Voulez-vous aussi démarrer le frontend sur ce serveur ? (O/N) : "
if errorlevel 2 goto :skip_frontend

echo.
echo 🎨 Démarrage du frontend...

echo @echo off > "%TEMP%\eos_frontend_serveur.bat"
echo title EOS Frontend - SERVEUR >> "%TEMP%\eos_frontend_serveur.bat"
echo cd /d "%FRONTEND_DIR%" >> "%TEMP%\eos_frontend_serveur.bat"
echo npm run dev >> "%TEMP%\eos_frontend_serveur.bat"
echo pause >> "%TEMP%\eos_frontend_serveur.bat"

start "EOS Frontend - SERVEUR" cmd /k "%TEMP%\eos_frontend_serveur.bat"

timeout /t 8 /nobreak >nul

start "" "http://localhost:5173"

:skip_frontend

REM ============================================================
REM Résumé
REM ============================================================
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ SERVEUR EOS DÉMARRÉ                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📡 SERVEUR BACKEND :
echo    Adresse locale  : http://localhost:5000
echo    Adresse réseau  : http://%IP_SERVEUR%:5000
echo.
echo 📱 ACCÈS CLIENTS :
echo.
echo    Les autres utilisateurs peuvent accéder à l'application via :
echo.
echo    1. Depuis leur navigateur :
echo       → http://%IP_SERVEUR%:5000
echo.
echo    2. Ou installer le frontend sur leur PC et configurer :
echo       → API_URL = http://%IP_SERVEUR%:5000
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚙️  CONFIGURATION REQUISE :
echo.
echo    Pour que les clients puissent se connecter, assurez-vous que :
echo.
echo    ✓ PostgreSQL accepte les connexions réseau
echo      → Voir : CONFIGURATION_MULTI_UTILISATEURS.md
echo.
echo    ✓ Le pare-feu Windows autorise les ports :
echo      → Port 5432 (PostgreSQL)
echo      → Port 5000 (Flask API)
echo.
echo    ✓ Les clients sont sur le même réseau
echo      → Ou vous avez configuré le routage/VPN
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 💡 COMMANDES UTILES :
echo.
echo    Voir l'IP du serveur :
echo    → ipconfig
echo.
echo    Autoriser les ports dans le pare-feu (Admin) :
echo    → netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=TCP localport=5432
echo    → netsh advfirewall firewall add rule name="Flask API" dir=in action=allow protocol=TCP localport=5000
echo.
echo    Tester depuis un client :
echo    → ping %IP_SERVEUR%
echo    → telnet %IP_SERVEUR% 5000
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📖 Pour plus d'informations, consultez :
echo    CONFIGURATION_MULTI_UTILISATEURS.md
echo.
echo ⚠️  NE FERMEZ PAS cette fenêtre tant que vous voulez que le serveur reste accessible
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

