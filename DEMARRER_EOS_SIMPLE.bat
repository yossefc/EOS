@echo off
cls

echo ================================================================
echo           Demarrage complet de l'application EOS              
echo ================================================================
echo.
echo Ce script va :
echo   1. Demarrer le backend Flask (PostgreSQL)
echo   2. Demarrer le frontend React (Vite)
echo   3. Ouvrir automatiquement Chrome
echo.
echo Patientez quelques secondes...
echo.

REM Demarrer le backend dans une nouvelle fenetre
echo [+] Demarrage du backend...
start "EOS Backend - Flask" cmd /k "cd /d D:\EOS\backend && call venv\Scripts\activate.bat && set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db && python start_with_postgresql.py"

REM Attendre 3 secondes que le backend demarre
timeout /t 3 /nobreak >nul
echo   [OK] Backend demarre

REM Demarrer le frontend dans une nouvelle fenetre
echo [+] Demarrage du frontend...
start "EOS Frontend - Vite" cmd /k "cd /d D:\EOS\frontend && npm run dev"

REM Attendre 8 secondes que le frontend demarre
echo Attente du demarrage des serveurs...
timeout /t 8 /nobreak >nul
echo   [OK] Frontend demarre

REM Ouvrir Chrome sur l'application
echo [+] Ouverture de Chrome...
start chrome http://localhost:5173

echo.
echo ================================================================
echo              APPLICATION EOS DEMARREE !                    
echo ================================================================
echo.
echo Backend :  http://localhost:5000
echo Frontend : http://localhost:5173
echo.
echo Les serveurs tournent dans des fenetres separees.
echo Fermez ces fenetres pour arreter l'application.
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul

