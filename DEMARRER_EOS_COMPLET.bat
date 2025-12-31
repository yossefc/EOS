@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║           Démarrage complet de l'application EOS              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Ce script va :
echo   1. Démarrer le backend Flask (PostgreSQL)
echo   2. Démarrer le frontend React (Vite)
echo   3. Ouvrir automatiquement Chrome
echo.
echo ⏳ Patientez quelques secondes...
echo.

REM Démarrer le backend dans une nouvelle fenêtre
echo ► Démarrage du backend...
 
REM Attendre 3 secondes que le backend démarre
timeout /t 3 /nobreak >nul
echo   ✅ Backend démarré

REM Démarrer le frontend dans une nouvelle fenêtre
echo ► Démarrage du frontend...
start "EOS Frontend - Vite" cmd /k "cd /d D:\EOS\frontend && npm run dev"

REM Attendre 8 secondes que le frontend démarre
echo ⏳ Attente du démarrage des serveurs...
timeout /t 8 /nobreak >nul
echo   ✅ Frontend démarré

REM Ouvrir Chrome sur l'application
echo ► Ouverture de Chrome...
start chrome http://localhost:5173

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ APPLICATION EOS DÉMARRÉE !                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Backend :  http://localhost:5000
echo 🌐 Frontend : http://localhost:5173
echo.
echo Les serveurs tournent dans des fenêtres séparées.
echo Fermez ces fenêtres pour arrêter l'application.
echo.
echo Appuyez sur une touche pour fermer cette fenêtre...
pause >nul





