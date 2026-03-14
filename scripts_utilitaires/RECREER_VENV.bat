@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║     Recréation de l'environnement virtuel Python (venv)      ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

cd /d D:\EOS\backend

echo [1/4] Suppression de l'ancien environnement virtuel...
if exist venv (
    rmdir /s /q venv
    echo ✓ Ancien venv supprimé
) else (
    echo ✓ Pas d'ancien venv à supprimer
)
echo.

echo [2/4] Création du nouveau venv...
python -m venv venv
if errorlevel 1 (
    echo ❌ ERREUR : Impossible de créer le venv
    echo Vérifiez que Python est installé : python --version
    pause
    exit /b 1
)
echo ✓ Nouveau venv créé
echo.

echo [3/4] Activation du venv et installation des dépendances...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'activer le venv
    pause
    exit /b 1
)
echo ✓ Venv activé
echo.

echo Installation des dépendances (cela peut prendre quelques minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'installer les dépendances
    pause
    exit /b 1
)
echo ✓ Dépendances installées
echo.

echo [4/4] Vérification...
python --version
echo.

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║              ✅ Environnement virtuel recréé !                ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Vous pouvez maintenant utiliser : DEMARRER_EOS_COMPLET.bat
echo.
pause

