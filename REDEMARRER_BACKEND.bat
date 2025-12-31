@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              Redémarrage du backend Flask                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  Instructions :
echo.
echo 1. Dans le terminal où tourne le backend (python app.py)
echo    Appuyez sur Ctrl+C pour l'arrêter
echo.
echo 2. Puis relancez-le avec la commande ci-dessous
echo.
echo ════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo ► Activation de l'environnement virtuel...
cd backend
call venv\Scripts\activate.bat

echo.
echo ► Démarrage de Flask...
echo.

python app.py





