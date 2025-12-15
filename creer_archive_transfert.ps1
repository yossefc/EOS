# Script PowerShell pour créer une archive de transfert du projet EOS
# Usage: .\creer_archive_transfert.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          📦 CRÉATION D'ARCHIVE DE TRANSFERT EOS               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Vérifier qu'on est à la racine du projet
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ ERREUR: Ce script doit être exécuté à la racine du projet EOS" -ForegroundColor Red
    Write-Host "   (Le dossier doit contenir les dossiers 'backend' et 'frontend')" -ForegroundColor Yellow
    pause
    exit 1
}

# Nom du fichier d'archive avec date
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$archiveName = "EOS_Transfer_$timestamp.zip"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Dossier source : $(Get-Location)" -ForegroundColor White
Write-Host "   Archive cible  : $archiveName" -ForegroundColor White
Write-Host ""

# Liste des fichiers/dossiers à inclure
Write-Host "📂 Fichiers à inclure:" -ForegroundColor Green
Write-Host "   ✓ backend/ (sans venv et __pycache__)" -ForegroundColor Gray
Write-Host "   ✓ frontend/ (sans node_modules et dist)" -ForegroundColor Gray
Write-Host "   ✓ *.md (documentation)" -ForegroundColor Gray
Write-Host "   ✓ start_eos.bat" -ForegroundColor Gray
Write-Host ""

# Créer un dossier temporaire pour l'archive
$tempDir = "EOS_temp_archive"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "⏳ Copie des fichiers..." -ForegroundColor Yellow

# Copier le backend (sans venv et __pycache__)
Write-Host "   → Backend..." -ForegroundColor Gray
robocopy backend "$tempDir\backend" /E /XD venv __pycache__ instance /XF *.pyc *.db /NFL /NDL /NJH /NJS | Out-Null

# Copier le frontend (sans node_modules et dist)
Write-Host "   → Frontend..." -ForegroundColor Gray
robocopy frontend "$tempDir\frontend" /E /XD node_modules dist .vite /NFL /NDL /NJH /NJS | Out-Null

# Copier les fichiers à la racine
Write-Host "   → Documentation..." -ForegroundColor Gray
Copy-Item "*.md" $tempDir -ErrorAction SilentlyContinue
Copy-Item "start_eos.bat" $tempDir -ErrorAction SilentlyContinue
Copy-Item ".gitignore" $tempDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "📦 Création de l'archive..." -ForegroundColor Yellow

# Créer l'archive ZIP
Compress-Archive -Path "$tempDir\*" -DestinationPath $archiveName -Force

# Nettoyer le dossier temporaire
Remove-Item $tempDir -Recurse -Force

# Calculer la taille
$fileSize = (Get-Item $archiveName).Length / 1MB
$fileSizeFormatted = "{0:N2}" -f $fileSize

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ ARCHIVE CRÉÉE                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📄 Fichier créé : $archiveName" -ForegroundColor White
Write-Host "📊 Taille       : $fileSizeFormatted MB" -ForegroundColor White
Write-Host "📍 Emplacement  : $(Get-Location)\$archiveName" -ForegroundColor White
Write-Host ""
Write-Host "📤 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Transférer ce fichier sur le nouvel ordinateur" -ForegroundColor Gray
Write-Host "   2. Extraire l'archive" -ForegroundColor Gray
Write-Host "   3. Suivre les instructions dans GUIDE_INSTALLATION.md" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 L'archive ne contient PAS:" -ForegroundColor Yellow
Write-Host "   • venv/ (environnement Python) - À recréer" -ForegroundColor Gray
Write-Host "   • node_modules/ (dépendances npm) - À recréer" -ForegroundColor Gray
Write-Host "   • Base de données - À reconfigurer" -ForegroundColor Gray
Write-Host ""

# Proposer d'ouvrir l'explorateur
$openExplorer = Read-Host "Voulez-vous ouvrir l'explorateur à cet emplacement ? (O/N)"
if ($openExplorer -eq "O" -or $openExplorer -eq "o") {
    Start-Process explorer.exe -ArgumentList "/select,`"$(Get-Location)\$archiveName`""
}

Write-Host ""
Write-Host "Appuyez sur une touche pour quitter..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


