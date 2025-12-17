@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         Création des tables manquantes PostgreSQL            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo ► Activation de l'environnement virtuel...
call D:\EOS\backend\venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR : Impossible d'activer le venv
    pause
    exit /b 1
)

echo ► Configuration de DATABASE_URL...
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db

echo ► Création des tables...
python D:\EOS\backend\creer_tables_manquantes.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Tables créées avec succès
    echo.
    echo Vous pouvez maintenant :
    echo   1. Redémarrer le backend : DEMARRER_EOS_COMPLET.bat
    echo   2. Tester les mises à jour d'enquêtes
) else (
    echo.
    echo ❌ Échec de la création des tables
)

pause

