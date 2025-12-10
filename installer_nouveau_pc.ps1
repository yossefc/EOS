# ============================================
# Script d'installation EOS sur nouveau PC
# ============================================
# Exécutez ce script après avoir décompressé le ZIP
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation EOS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$EosPath = $PSScriptRoot

# Vérifier Python
Write-Host "Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python non trouvé !" -ForegroundColor Red
    Write-Host "    Téléchargez Python sur: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "    IMPORTANT: Cochez 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Appuyez sur une touche pour quitter..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Vérifier Node.js
Write-Host "Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js trouvé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js non trouvé !" -ForegroundColor Red
    Write-Host "    Téléchargez Node.js sur: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Appuyez sur une touche pour quitter..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Host ""

# Installation du Backend
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation du Backend (Python/Flask)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "$EosPath\backend"

# Créer l'environnement virtuel
Write-Host "Création de l'environnement virtuel Python..." -ForegroundColor Yellow
python -m venv venv

# Activer l'environnement
Write-Host "Activation de l'environnement..." -ForegroundColor Yellow
& "$EosPath\backend\venv\Scripts\Activate.ps1"

# Installer les dépendances
Write-Host "Installation des dépendances Python..." -ForegroundColor Yellow
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

Write-Host "  ✓ Backend installé" -ForegroundColor Green
Write-Host ""

# Installation du Frontend
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation du Frontend (React/Vite)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Set-Location "$EosPath\frontend"

Write-Host "Installation des dépendances Node.js..." -ForegroundColor Yellow
npm install

Write-Host "  ✓ Frontend installé" -ForegroundColor Green
Write-Host ""

# Configuration IP
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Configuration réseau" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Obtenir l'adresse IP
$IPAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.*" } | Select-Object -First 1).IPAddress

if ($IPAddress) {
    Write-Host "Adresse IP détectée: $IPAddress" -ForegroundColor Green
    
    # Demander si on veut configurer pour accès réseau
    Write-Host ""
    Write-Host "Voulez-vous configurer l'accès réseau ? (o/n)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "o" -or $response -eq "O") {
        # Modifier le fichier config.js
        $configPath = "$EosPath\frontend\src\config.js"
        if (Test-Path $configPath) {
            $configContent = Get-Content $configPath -Raw
            $newConfig = $configContent -replace "http://localhost:5000", "http://${IPAddress}:5000"
            $newConfig = $newConfig -replace "http://127\.0\.0\.1:5000", "http://${IPAddress}:5000"
            $newConfig | Out-File -FilePath $configPath -Encoding UTF8
            Write-Host "  ✓ Configuration mise à jour pour $IPAddress" -ForegroundColor Green
        }
    }
} else {
    Write-Host "Impossible de détecter l'adresse IP automatiquement" -ForegroundColor Yellow
    Write-Host "Vous devrez configurer manuellement frontend/src/config.js" -ForegroundColor Yellow
}

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
echo Démarrage du Backend...
start "EOS Backend" cmd /k "cd /d $EosPath\backend && call venv\Scripts\activate.bat && python app.py"

echo Attente du démarrage du backend (5 secondes)...
timeout /t 5 /nobreak > nul

echo Démarrage du Frontend...
start "EOS Frontend" cmd /k "cd /d $EosPath\frontend && npm run dev"

echo.
echo ============================================
echo   EOS démarré !
echo ============================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
if ("$IPAddress" -ne "") {
    echo.
    echo Accès réseau: http://${IPAddress}:5173
}
echo.
echo Appuyez sur une touche pour fermer cette fenêtre...
pause > nul
"@
$startAll | Out-File -FilePath "$EosPath\DEMARRER_EOS.bat" -Encoding ASCII

Write-Host "  ✓ Scripts de démarrage créés" -ForegroundColor Green
Write-Host ""

# Résumé final
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer l'application :" -ForegroundColor White
Write-Host ""
Write-Host "  Option 1 (Recommandée) :" -ForegroundColor Yellow
Write-Host "    Double-cliquez sur DEMARRER_EOS.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "  Option 2 (Séparément) :" -ForegroundColor Yellow
Write-Host "    1. Double-cliquez sur DEMARRER_BACKEND.bat" -ForegroundColor Gray
Write-Host "    2. Double-cliquez sur DEMARRER_FRONTEND.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "Accès à l'application :" -ForegroundColor White
Write-Host "  - Local  : http://localhost:5173" -ForegroundColor Gray
if ($IPAddress) {
    Write-Host "  - Réseau : http://${IPAddress}:5173" -ForegroundColor Gray
}
Write-Host ""

# Demander si on veut démarrer maintenant
Write-Host "Voulez-vous démarrer l'application maintenant ? (o/n)" -ForegroundColor Yellow
$startNow = Read-Host

if ($startNow -eq "o" -or $startNow -eq "O") {
    Set-Location $EosPath
    Start-Process "$EosPath\DEMARRER_EOS.bat"
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

