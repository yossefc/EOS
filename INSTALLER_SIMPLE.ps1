# Script d'installation simplifié pour EOS
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation EOS - Version Simplifiée" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$EosPath = $PSScriptRoot

# Vérifier Python
Write-Host "Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  OK - Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERREUR - Python non trouvé !" -ForegroundColor Red
    Write-Host "  Téléchargez Python sur: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANT: Cochez 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    pause
    exit 1
}

# Vérifier Node.js
Write-Host "Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  OK - Node.js trouvé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERREUR - Node.js non trouvé !" -ForegroundColor Red
    Write-Host "  Téléchargez Node.js sur: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""

# Installation du Backend
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation du Backend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "$EosPath\backend"

Write-Host "Création de l'environnement virtuel Python..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Installation des dépendances Python..." -ForegroundColor Yellow
& "$EosPath\backend\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$EosPath\backend\venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "  OK - Backend installé" -ForegroundColor Green
Write-Host ""

# Installation du Frontend
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation du Frontend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "$EosPath\frontend"

Write-Host "Installation des dépendances Node.js..." -ForegroundColor Yellow
npm install

Write-Host "  OK - Frontend installé" -ForegroundColor Green
Write-Host ""

# Créer les scripts de démarrage
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Création des scripts de démarrage" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Script démarrage backend
$startBackend = @"
@echo off
cd /d "$EosPath\backend"
call venv\Scripts\activate.bat
python app.py
pause
"@
$startBackend | Out-File -FilePath "$EosPath\DEMARRER_BACKEND.bat" -Encoding ASCII

# Script démarrage frontend
$startFrontend = @"
@echo off
cd /d "$EosPath\frontend"
npm run dev
pause
"@
$startFrontend | Out-File -FilePath "$EosPath\DEMARRER_FRONTEND.bat" -Encoding ASCII

# Script démarrage complet
$startAll = @"
@echo off
echo Demarrage du Backend...
start "EOS Backend" cmd /k "cd /d $EosPath\backend && call venv\Scripts\activate.bat && python app.py"

echo Attente du demarrage du backend (5 secondes)...
timeout /t 5 /nobreak > nul

echo Demarrage du Frontend...
start "EOS Frontend" cmd /k "cd /d $EosPath\frontend && npm run dev"

echo.
echo ============================================
echo   EOS demarre !
echo ============================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
"@
$startAll | Out-File -FilePath "$EosPath\DEMARRER_EOS.bat" -Encoding ASCII

Write-Host "  OK - Scripts de démarrage créés" -ForegroundColor Green
Write-Host ""

# Résumé final
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer l'application :" -ForegroundColor White
Write-Host "  Double-cliquez sur DEMARRER_EOS.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "Acces a l'application :" -ForegroundColor White
Write-Host "  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
pause
