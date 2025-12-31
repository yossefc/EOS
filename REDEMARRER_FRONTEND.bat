@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              Redémarrage du frontend React                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  Instructions :
echo.
echo 1. Dans le terminal où tourne le frontend (npm run dev)
echo    Appuyez sur Ctrl+C pour l'arrêter
echo.
echo 2. Puis relancez-le avec :
echo    cd frontend
echo    npm run dev
echo.
echo 3. Attendez que Vite recompile (quelques secondes)
echo.
echo 4. Rafraîchissez votre navigateur (F5)
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo Alternative automatique :
echo.
pause
echo.
echo ► Changement de répertoire vers frontend...
cd frontend

echo.
echo ► Démarrage de Vite...
echo.
echo ⚠️  Si le port 5173 est déjà utilisé, arrêtez d'abord l'ancien processus (Ctrl+C)
echo.

call npm run dev





