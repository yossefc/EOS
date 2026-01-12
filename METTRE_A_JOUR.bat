@echo off
REM ==============================================================================
REM Script de Mise à Jour EOS (Version Batch)
REM Lance le script PowerShell de mise à jour
REM ==============================================================================

echo.
echo ========================================
echo    MISE A JOUR DU SYSTEME EOS
echo ========================================
echo.

REM Vérifier que PowerShell est disponible
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] PowerShell n'est pas installe ou n'est pas dans le PATH
    pause
    exit /b 1
)

REM Lancer le script PowerShell
powershell.exe -ExecutionPolicy Bypass -File "%~dp0METTRE_A_JOUR.ps1"

exit /b %ERRORLEVEL%
