@echo off
echo Starting EOS System...

:: Démarrer le backend
cd backend
start cmd /k "python app.py"

:: Attendre quelques secondes
timeout /t 5

:: Démarrer le frontend
cd ../frontend
start cmd /k "npm run dev"

echo.
echo Serveurs démarrés !
echo Backend: http://localhost:5000
echo.
echo Interface Admin: http://localhost:5173
echo Interface Enquêteur: http://localhost:5173/enqueteur.html
echo.
echo Pour arrêter les serveurs, fermez les fenêtres de commande.
pause
