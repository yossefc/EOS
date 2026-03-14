@echo off
REM Script ultra-simple pour rebuilder le frontend
cls

echo.
echo ================================================================
echo         REBUILD FRONTEND ULTRA-SIMPLE
echo ================================================================
echo.
echo ATTENTION : Ce script va rebuilder le frontend React.
echo Cela peut prendre 1-2 minutes.
echo.
pause
echo.

REM ============================================================
REM ALLER DANS FRONTEND
REM ============================================================
echo [1/4] Deplacement dans le dossier frontend...
echo.

if not exist frontend (
    echo [ERREUR] Le dossier frontend n'existe pas !
    echo Vous etes dans le mauvais repertoire.
    echo.
    echo Repertoire actuel :
    cd
    echo.
    pause
    exit /b 1
)

cd frontend

echo Repertoire actuel :
cd
echo.
pause
echo.

REM ============================================================
REM INSTALLER LES DEPENDANCES
REM ============================================================
echo [2/4] Installation des dependances npm...
echo (cela peut prendre 1-2 minutes)
echo.

npm install

if errorlevel 1 (
    echo.
    echo [ERREUR] npm install a echoue !
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependances installees
echo.
pause
echo.

REM ============================================================
REM SUPPRIMER L'ANCIEN BUILD
REM ============================================================
echo [3/4] Suppression de l'ancien build...
echo.

if exist dist (
    echo Suppression de dist/...
    rmdir /s /q dist
    echo [OK] dist/ supprime
) else (
    echo [INFO] Pas d'ancien build a supprimer
)

echo.
pause
echo.

REM ============================================================
REM BUILDER
REM ============================================================
echo [4/4] Build du frontend...
echo (cela peut prendre 30-60 secondes)
echo.

npm run build

if errorlevel 1 (
    echo.
    echo [ERREUR] Le build a echoue !
    echo Regardez les messages d'erreur ci-dessus.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Build termine !
echo.

REM Verifier que dist existe
if not exist dist (
    echo [ERREUR] Le dossier dist n'a pas ete cree !
    echo Le build a echoue silencieusement.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              BUILD TERMINE AVEC SUCCES !
echo ================================================================
echo.
echo MAINTENANT, FAITES CECI :
echo.
echo 1. Fermez TOUTES les fenetres du navigateur
echo.
echo 2. Lancez : DEMARRER_EOS_SIMPLE.bat
echo.
echo 3. Ouvrez : http://localhost:5173
echo.
echo 4. Dans le navigateur, appuyez sur : Ctrl + Shift + R
echo    (pour vider le cache)
echo.
echo 5. Si ca ne marche toujours pas :
echo    - F12 (ouvrir DevTools)
echo    - Onglet "Application" ou "Stockage"
echo    - Clic droit sur "localhost:5173"
echo    - "Effacer les donnees du site"
echo.
echo ================================================================
echo.
pause

cd ..

