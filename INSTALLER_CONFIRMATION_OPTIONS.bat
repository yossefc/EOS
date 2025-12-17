@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    Installation du système de confirmation personnalisée      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Définir DATABASE_URL
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
echo ✓ DATABASE_URL définie

REM Activer l'environnement virtuel
echo.
echo ► Activation de l'environnement virtuel...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo ✓ Environnement virtuel activé

REM Étape 1 : Agrandir la colonne elements_retrouves
echo.
echo ═══════════════════════════════════════════════════════════════
echo ÉTAPE 1/2 : Agrandissement de la colonne elements_retrouves
echo ═══════════════════════════════════════════════════════════════
python backend\agrandir_elements_retrouves.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de l'agrandissement
    pause
    exit /b 1
)

REM Étape 2 : Créer la table confirmation_options
echo.
echo ═══════════════════════════════════════════════════════════════
echo ÉTAPE 2/2 : Création de la table confirmation_options
echo ═══════════════════════════════════════════════════════════════
python backend\creer_table_confirmation_options.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de la création de la table
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         ✅ Installation terminée avec succès !                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🔄 PROCHAINES ÉTAPES :
echo.
echo 1. Redémarrez le BACKEND (Ctrl+C puis relancer)
echo 2. Redémarrez le FRONTEND (Ctrl+C puis relancer)
echo 3. Rafraîchissez le navigateur (F5 ou Ctrl+F5)
echo.
echo 💡 NOUVEAU COMPORTEMENT :
echo.
echo Quand vous utilisez "Autre" pour saisir une confirmation :
echo   • Le texte est enregistré dans le dossier
echo   • Il est automatiquement ajouté à la liste
echo   • La prochaine fois, vous le retrouverez dans la liste
echo   • Plus besoin de le ressaisir !
echo.
pause


