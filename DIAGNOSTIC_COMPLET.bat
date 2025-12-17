@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       DIAGNOSTIC COMPLET - Configuration d'import EOS         ║
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

echo ► Lancement du diagnostic...
python D:\EOS\backend\diagnostic_complet.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Diagnostic terminé avec succès
) else (
    echo.
    echo ❌ Échec du diagnostic
)

pause

