@echo off
cls

echo ================================================================
echo        Mise a jour complete du frontend (rebuild)         
echo ================================================================
echo.
echo Ce script va :
echo   1. Verifier que node_modules est a jour
echo   2. Rebuilder le frontend React
echo   3. Copier les nouveaux fichiers dans dist/
echo.
pause
echo.

cd /d D:\EOS\frontend

echo [1/3] Verification des dependances npm...
echo.
npm install
if errorlevel 1 (
    echo.
    echo [ERREUR] Impossible d'installer les dependances
    pause
    exit /b 1
)
echo [OK] Dependances installees
echo.

echo [2/3] Nettoyage de l'ancien build...
if exist dist (
    rmdir /s /q dist
    echo [OK] Ancien build supprime
) else (
    echo [INFO] Pas d'ancien build a supprimer
)
echo.

echo [3/3] Build du nouveau frontend...
echo (cela peut prendre 30 secondes)
echo.
npm run build
if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors du build
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              Frontend rebuild avec succes !           
echo ================================================================
echo.
echo Actions a faire maintenant :
echo   1. Fermez toutes les fenetres du navigateur
echo   2. Relancez l'application : DEMARRER_EOS_SIMPLE.bat
echo   3. Ouvrez http://localhost:5173
echo   4. Faites Ctrl + Shift + R pour vider le cache
echo.
pause

