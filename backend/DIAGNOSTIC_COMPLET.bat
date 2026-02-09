@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo 🔍 DIAGNOSTIC COMPLET - SHERLOCK
echo ============================================================
echo.
echo Ce script va identifier EXACTEMENT le problème...
echo.

REM Définir DATABASE_URL si pas déjà défini
if "%DATABASE_URL%"=="" (
    set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
)

REM Exécuter le diagnostic
python DIAGNOSTIC_COMPLET.py

echo.
echo ============================================================
echo.
pause
