@echo off
echo ============================================
echo     INSTALLATION AUTOMATIQUE - SYSTEME EOS
echo ============================================
echo.
echo Ce script va installer automatiquement tout ce qui est necessaire.
echo Assurez-vous d'etre connecte a internet.
echo.
pause

echo.
echo [1/6] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe!
    echo Veuillez telecharger Python depuis: https://python.org/downloads/
    echo Assurez-vous de cocher "Add Python to PATH"
    pause
    exit /b 1
)
echo ✓ Python detecte

echo.
echo [2/6] Verification de Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Node.js n'est pas installe!
    echo Veuillez telecharger Node.js depuis: https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js detecte

echo.
echo [3/6] Installation des dependances Python (backend)...
cd /d "%~dp0\backend"
if not exist venv (
    echo Creation de l'environnement virtuel Python...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installation des packages Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances Python!
    pause
    exit /b 1
)
echo ✓ Backend configure

echo.
echo [4/6] Installation des dependances JavaScript (frontend)...
cd /d "%~dp0\frontend"
echo Installation des packages JavaScript...
npm install
if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances JavaScript!
    pause
    exit /b 1
)
echo ✓ Frontend configure

echo.
echo [5/6] Verification de la base de donnees...
cd /d "%~dp0\backend"
if not exist "instance\eos.db" (
    echo Initialisation de la base de donnees...
    call venv\Scripts\activate.bat
    python init_db.py
)
echo ✓ Base de donnees prete

echo.
echo [6/6] Finalisation...
cd /d "%~dp0"
echo Creation du raccourci de demarrage...

:: Creer le script de demarrage
echo @echo off > DEMARRER_EOS.bat
echo echo ============================================ >> DEMARRER_EOS.bat
echo echo     DEMARRAGE DU SYSTEME EOS >> DEMARRER_EOS.bat
echo echo ============================================ >> DEMARRER_EOS.bat
echo echo. >> DEMARRER_EOS.bat
echo echo Demarrage du serveur backend... >> DEMARRER_EOS.bat
echo cd /d "%%~dp0\backend" >> DEMARRER_EOS.bat
echo call venv\Scripts\activate.bat >> DEMARRER_EOS.bat
echo start "EOS Backend" python app.py >> DEMARRER_EOS.bat
echo echo. >> DEMARRER_EOS.bat
echo echo Demarrage du frontend... >> DEMARRER_EOS.bat
echo timeout /t 3 /nobreak ^>nul >> DEMARRER_EOS.bat
echo cd /d "%%~dp0\frontend" >> DEMARRER_EOS.bat
echo start "EOS Frontend" npm run dev >> DEMARRER_EOS.bat
echo echo. >> DEMARRER_EOS.bat
echo echo ============================================ >> DEMARRER_EOS.bat
echo echo Le systeme EOS demarrera dans quelques secondes... >> DEMARRER_EOS.bat
echo echo. >> DEMARRER_EOS.bat
echo echo ACCÈS AU SYSTEME : >> DEMARRER_EOS.bat
echo echo - Interface Admin : http://localhost:5173 >> DEMARRER_EOS.bat
echo echo - Interface Enquêteurs : http://localhost:5173/enqueteur.html >> DEMARRER_EOS.bat
echo echo. >> DEMARRER_EOS.bat
echo echo Appuyez sur une touche pour ouvrir automatiquement... >> DEMARRER_EOS.bat
echo pause >> DEMARRER_EOS.bat
echo start http://localhost:5173 >> DEMARRER_EOS.bat

echo.
echo ============================================
echo        INSTALLATION TERMINEE AVEC SUCCES!
echo ============================================
echo.
echo Le systeme EOS est maintenant pret a utiliser.
echo.
echo POUR DEMARRER LE SYSTEME :
echo 1. Double-cliquez sur "DEMARRER_EOS.bat"
echo 2. Attendez quelques secondes
echo 3. Le navigateur s'ouvrira automatiquement
echo.
echo COMPTES PAR DEFAUT :
echo - Admin : admin / admin123
echo - Enqueteur test : enq001 / pass123
echo.
echo FICHIERS IMPORTANTS :
echo - DEMARRER_EOS.bat = Pour lancer le systeme
echo - GUIDE_PARTAGE_COMPLET.md = Documentation complete
echo.
echo ============================================
pause