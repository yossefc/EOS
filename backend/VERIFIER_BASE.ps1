# Script PowerShell pour vérifier les données Sherlock en base
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VÉRIFICATION DES DONNÉES SHERLOCK EN BASE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Définir DATABASE_URL si pas déjà défini
if (-not $env:DATABASE_URL) {
    Write-Host "Configuration de DATABASE_URL..." -ForegroundColor Yellow
    $env:DATABASE_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
}

Write-Host "Base de données: $($env:DATABASE_URL)" -ForegroundColor Green
Write-Host ""

# Exécuter le script Python
python verifier_donnees_sherlock.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
