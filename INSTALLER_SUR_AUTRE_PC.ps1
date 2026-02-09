# Script PowerShell pour installer les fichiers sur l'autre PC
# À LANCER SUR L'AUTRE ORDINATEUR après avoir copié les fichiers

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 INSTALLATION DES CORRECTIONS SHERLOCK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier qu'on est dans le bon dossier
$currentPath = Get-Location
Write-Host "Dossier actuel: $currentPath" -ForegroundColor Gray
Write-Host ""

# Demander confirmation
Write-Host "⚠️  ATTENTION: Ce script va:" -ForegroundColor Yellow
Write-Host "   1. Remplacer 3 fichiers dans D:\EOS\backend" -ForegroundColor White
Write-Host "   2. Créer des backups des anciens fichiers" -ForegroundColor White
Write-Host ""
Write-Host "Voulez-vous continuer? (O/N): " -NoNewline -ForegroundColor Yellow
$confirmation = Read-Host

if ($confirmation -ne "O" -and $confirmation -ne "o") {
    Write-Host ""
    Write-Host "❌ Installation annulée" -ForegroundColor Red
    Write-Host ""
    pause
    exit
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 INSTALLATION EN COURS..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Créer un dossier de backup
$backupFolder = "D:\EOS\BACKUP_AVANT_SHERLOCK_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "Création du backup: $backupFolder" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null

# Liste des fichiers à installer
$files = @(
    @{
        Source = "import_engine.py"
        Dest = "D:\EOS\backend\import_engine.py"
        Name = "import_engine.py"
    },
    @{
        Source = "import_config.py"
        Dest = "D:\EOS\backend\models\import_config.py"
        Name = "import_config.py"
    },
    @{
        Source = "app.py"
        Dest = "D:\EOS\backend\app.py"
        Name = "app.py"
    }
)

$success = 0
$failed = 0

foreach ($file in $files) {
    Write-Host ""
    Write-Host "📄 Installation: $($file.Name)" -ForegroundColor Cyan
    
    # Vérifier que le fichier source existe
    if (-not (Test-Path $file.Source)) {
        Write-Host "   ❌ ERREUR: Fichier source introuvable: $($file.Source)" -ForegroundColor Red
        $failed++
        continue
    }
    
    # Backup de l'ancien fichier si il existe
    if (Test-Path $file.Dest) {
        $backupFile = Join-Path $backupFolder $file.Name
        Copy-Item -Path $file.Dest -Destination $backupFile -Force
        Write-Host "   💾 Backup créé" -ForegroundColor Gray
    }
    
    # Copier le nouveau fichier
    try {
        # Créer le dossier parent si nécessaire
        $parentFolder = Split-Path -Parent $file.Dest
        if (-not (Test-Path $parentFolder)) {
            New-Item -ItemType Directory -Path $parentFolder -Force | Out-Null
        }
        
        Copy-Item -Path $file.Source -Destination $file.Dest -Force
        Write-Host "   ✅ Installé avec succès" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "   ❌ ERREUR lors de la copie: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Fichiers installés: $success" -ForegroundColor Green
Write-Host "❌ Échecs: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "💾 Backup dans: $backupFolder" -ForegroundColor Gray
Write-Host ""

if ($success -eq $files.Count) {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ INSTALLATION RÉUSSIE!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 PROCHAINES ÉTAPES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1️⃣ REDÉMARRER Flask (OBLIGATOIRE!)" -ForegroundColor White
    Write-Host "   → Arrêter: Ctrl+C dans le terminal Flask" -ForegroundColor Gray
    Write-Host "   → Redémarrer:" -ForegroundColor Gray
    Write-Host "     cd D:\EOS\backend" -ForegroundColor Gray
    Write-Host "     python app.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2️⃣ VÉRIFIER l'installation:" -ForegroundColor White
    Write-Host "   cd D:\EOS\backend" -ForegroundColor Gray
    Write-Host "   python DIAGNOSTIC_COMPLET.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3️⃣ SUPPRIMER l'ancien fichier Sherlock" -ForegroundColor White
    Write-Host "   → Dans l'interface web" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4️⃣ RÉIMPORTER le fichier Excel" -ForegroundColor White
    Write-Host ""
    Write-Host "5️⃣ TESTER l'export" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "⚠️  INSTALLATION INCOMPLÈTE" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Certains fichiers n'ont pas pu être installés." -ForegroundColor Yellow
    Write-Host "Vérifiez les erreurs ci-dessus et réessayez." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
