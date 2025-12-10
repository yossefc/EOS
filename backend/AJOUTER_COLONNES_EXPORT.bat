@echo off
chcp 65001 >nul
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  MIGRATION: Ajout des colonnes d'export                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  IMPORTANT: Le serveur Flask doit être ARRÊTÉ
echo.
pause
echo.

cd /d "%~dp0"

echo → Exécution de la migration...
python setup_export_features.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║  ✅ MIGRATION TERMINÉE AVEC SUCCÈS                          ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo Redémarrez maintenant le serveur Flask:
    echo   python app.py
    echo.
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║  ❌ ERREUR                                                   ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo Le serveur Flask est peut-être encore en cours d'exécution.
    echo Arrêtez-le avec Ctrl+C et relancez ce script.
    echo.
)

pause

