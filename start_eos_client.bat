@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                EOS - MODE CLIENT (Multi-utilisateurs)         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM Configuration
REM ============================================================
REM ⚠️ IMPORTANT : Modifier l'IP ci-dessous avec celle du serveur
set SERVEUR_IP=192.168.1.100
REM ============================================================

set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@%SERVEUR_IP%:5432/eos_db

echo ═══════════════════════════════════════════════════════════════
echo.
echo 📡 Configuration :
echo    Adresse du serveur : %SERVEUR_IP%
echo.
echo ⚠️  Si cette adresse est incorrecte, modifiez la variable
echo    SERVEUR_IP dans ce fichier (start_eos_client.bat)
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

REM ============================================================
REM Test de connexion au serveur
REM ============================================================
echo [1/3] 🔍 Test de connexion au serveur...

ping -n 1 %SERVEUR_IP% >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ ERREUR: Impossible de joindre le serveur %SERVEUR_IP%
    echo.
    echo    Vérifiez que :
    echo    • Le serveur est démarré
    echo    • L'adresse IP est correcte
    echo    • Vous êtes sur le même réseau
    echo.
    pause
    exit /b 1
)
echo    ✅ Serveur joignable
echo.

REM ============================================================
REM Démarrage du backend local (proxy)
REM ============================================================
echo [2/3] 🔧 Démarrage du backend local (connexion au serveur)...

echo @echo off > "%TEMP%\eos_backend_client.bat"
echo title EOS Backend - CLIENT >> "%TEMP%\eos_backend_client.bat"
echo cd /d "%BACKEND_DIR%" >> "%TEMP%\eos_backend_client.bat"
echo set DATABASE_URL=%DATABASE_URL% >> "%TEMP%\eos_backend_client.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_client.bat"
echo echo    EOS CLIENT >> "%TEMP%\eos_backend_client.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_client.bat"
echo echo. >> "%TEMP%\eos_backend_client.bat"
echo echo ✓ Mode : CLIENT >> "%TEMP%\eos_backend_client.bat"
echo echo ✓ Connexion au serveur : %SERVEUR_IP% >> "%TEMP%\eos_backend_client.bat"
echo echo. >> "%TEMP%\eos_backend_client.bat"
echo echo ══════════════════════════════════════════════════════════════ >> "%TEMP%\eos_backend_client.bat"
echo echo. >> "%TEMP%\eos_backend_client.bat"
echo python start_with_postgresql.py >> "%TEMP%\eos_backend_client.bat"
echo pause >> "%TEMP%\eos_backend_client.bat"

start "EOS Backend - CLIENT" cmd /k "%TEMP%\eos_backend_client.bat"

echo    ✅ Backend client lancé
echo.

timeout /t 5 /nobreak >nul

REM ============================================================
REM Démarrage du frontend
REM ============================================================
echo [3/3] 🎨 Démarrage du frontend...

echo @echo off > "%TEMP%\eos_frontend_client.bat"
echo title EOS Frontend - CLIENT >> "%TEMP%\eos_frontend_client.bat"
echo cd /d "%FRONTEND_DIR%" >> "%TEMP%\eos_frontend_client.bat"
echo npm run dev >> "%TEMP%\eos_frontend_client.bat"
echo pause >> "%TEMP%\eos_frontend_client.bat"

start "EOS Frontend - CLIENT" cmd /k "%TEMP%\eos_frontend_client.bat"

echo    ✅ Frontend lancé
echo.

timeout /t 8 /nobreak >nul

REM ============================================================
REM Ouverture du navigateur
REM ============================================================
echo 🌐 Ouverture du navigateur...

start "" "http://localhost:5173"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  ✅ CLIENT EOS DÉMARRÉ                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📡 Connexion :
echo    Serveur backend : http://%SERVEUR_IP%:5000
echo    Frontend local  : http://localhost:5173
echo.
echo 💡 Vous travaillez sur la même base de données que les autres utilisateurs
echo    connectés au serveur %SERVEUR_IP%
echo.
echo ⚠️  Ne fermez pas les fenêtres Backend et Frontend
echo.

pause


