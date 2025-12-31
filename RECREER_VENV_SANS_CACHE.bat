@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║          Nettoyage du cache pip et recréation venv           ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

cd /d D:\EOS\backend

echo [1/5] Nettoyage du cache pip...
python -m pip cache purge
echo ✓ Cache pip nettoyé
echo.

echo [2/5] Suppression de l'ancien environnement virtuel...
if exist venv (
    rmdir /s /q venv
    echo ✓ Ancien venv supprimé
) else (
    echo ✓ Pas d'ancien venv à supprimer
)
echo.

echo [3/5] Création du nouveau venv...
python -m venv venv
if errorlevel 1 (
    echo ❌ ERREUR : Impossible de créer le venv
    echo Vérifiez que Python est installé : python --version
    pause
    exit /b 1
)
echo ✓ Nouveau venv créé
echo.

echo [4/5] Activation du venv et installation des dépendances...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'activer le venv
    pause
    exit /b 1
)
echo ✓ Venv activé
echo.

echo Installation des dépendances (SANS CACHE - peut être plus long)...
echo Cela peut prendre 5-10 minutes selon votre connexion Internet...
pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERREUR : Impossible d'installer les dépendances
    echo.
    echo Solutions possibles :
    echo   1. Relancez ce script EN TANT QU'ADMINISTRATEUR
    echo   2. Fermez tous les programmes Python en cours
    echo   3. Désactivez temporairement votre antivirus
    echo.
    pause
    exit /b 1
)
echo ✓ Dépendances installées
echo.

echo [5/5] Vérification...
python --version
echo.

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║              ✅ Environnement virtuel recréé !                ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant utiliser : DEMARRER_EOS_COMPLET.bat
echo.
pause

