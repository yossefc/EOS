# ============================================
# Script de préparation du transfert EOS
# ============================================
# Ce script crée une archive ZIP propre du projet EOS
# sans les fichiers inutiles (node_modules, venv, etc.)
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Préparation du transfert EOS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Définir les chemins
$SourcePath = $PSScriptRoot
$ExportPath = "$env:USERPROFILE\Desktop\EOS_TRANSFERT"
$ZipPath = "$env:USERPROFILE\Desktop\EOS_TRANSFERT.zip"

# Supprimer l'ancien export s'il existe
if (Test-Path $ExportPath) {
    Write-Host "Suppression de l'ancien dossier d'export..." -ForegroundColor Yellow
    Remove-Item -Path $ExportPath -Recurse -Force
}

if (Test-Path $ZipPath) {
    Write-Host "Suppression de l'ancien fichier ZIP..." -ForegroundColor Yellow
    Remove-Item -Path $ZipPath -Force
}

# Créer le dossier d'export
Write-Host "Création du dossier d'export..." -ForegroundColor Green
New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null

# Liste des dossiers/fichiers à exclure
$ExcludeDirs = @(
    "node_modules",
    "venv",
    "__pycache__",
    ".git",
    ".vscode",
    "instance",
    "exports"
)

$ExcludeFiles = @(
    "*.db",
    "*.log",
    "*.pyc",
    "*.pyo",
    ".env"
)

# Copier les fichiers
Write-Host "Copie des fichiers..." -ForegroundColor Green

# Construire la liste d'exclusion pour robocopy
$ExcludeDirArgs = $ExcludeDirs | ForEach-Object { "/XD", $_ }
$ExcludeFileArgs = $ExcludeFiles | ForEach-Object { "/XF", $_ }

# Exécuter robocopy
$robocopyArgs = @($SourcePath, $ExportPath, "/E", "/NFL", "/NDL", "/NJH", "/NJS") + $ExcludeDirArgs + $ExcludeFileArgs
& robocopy @robocopyArgs | Out-Null

# Créer les dossiers vides nécessaires
Write-Host "Création des dossiers de structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path "$ExportPath\backend\instance" -Force | Out-Null
New-Item -ItemType Directory -Path "$ExportPath\backend\exports\batches" -Force | Out-Null

# Créer un fichier .gitkeep dans les dossiers vides
"" | Out-File -FilePath "$ExportPath\backend\instance\.gitkeep"
"" | Out-File -FilePath "$ExportPath\backend\exports\batches\.gitkeep"

# Vérifier que requirements.txt existe, sinon le créer
$RequirementsPath = "$ExportPath\backend\requirements.txt"
if (-not (Test-Path $RequirementsPath)) {
    Write-Host "Création du fichier requirements.txt..." -ForegroundColor Yellow
    @"
flask>=2.3.0
flask-cors>=4.0.0
flask-sqlalchemy>=3.0.0
python-docx>=0.8.11
openpyxl>=3.1.0
Werkzeug>=2.3.0
SQLAlchemy>=2.0.0
"@ | Out-File -FilePath $RequirementsPath -Encoding UTF8
}

# Créer le fichier ZIP
Write-Host "Création de l'archive ZIP..." -ForegroundColor Green
Compress-Archive -Path "$ExportPath\*" -DestinationPath $ZipPath -Force

# Calculer la taille
$ZipSize = (Get-Item $ZipPath).Length / 1MB
$ZipSizeStr = "{0:N2} MB" -f $ZipSize

# Résumé
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Transfert préparé avec succès !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fichiers créés :" -ForegroundColor White
Write-Host "  - Dossier : $ExportPath" -ForegroundColor Gray
Write-Host "  - ZIP     : $ZipPath ($ZipSizeStr)" -ForegroundColor Gray
Write-Host ""
Write-Host "Prochaines étapes :" -ForegroundColor White
Write-Host "  1. Copiez le fichier ZIP sur une clé USB ou envoyez-le" -ForegroundColor Gray
Write-Host "  2. Sur le nouveau PC, décompressez le ZIP" -ForegroundColor Gray
Write-Host "  3. Suivez le guide GUIDE_INSTALLATION_NOUVEAU_PC.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Le fichier ZIP se trouve sur votre Bureau :" -ForegroundColor Yellow
Write-Host "  $ZipPath" -ForegroundColor Yellow
Write-Host ""

# Ouvrir l'explorateur
Write-Host "Ouverture de l'explorateur..." -ForegroundColor Green
explorer.exe "/select,$ZipPath"

Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


