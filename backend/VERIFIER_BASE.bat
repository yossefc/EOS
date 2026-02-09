@echo off
chcp 65001 >nul
echo ============================================================
echo VÉRIFICATION DES DONNÉES SHERLOCK EN BASE
echo ============================================================
echo.

REM Définir DATABASE_URL si pas déjà défini
if "%DATABASE_URL%"=="" (
    echo Configuration de DATABASE_URL...
    set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
)

echo Base de données: %DATABASE_URL%
echo.

REM Exécuter le script Python
python verifier_donnees_sherlock.py

echo.
echo ============================================================
echo Appuyez sur une touche pour fermer...
pause >nul
