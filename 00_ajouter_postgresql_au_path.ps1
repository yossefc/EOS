# Script pour ajouter PostgreSQL au PATH
# À exécuter sur l'ordinateur où PostgreSQL est installé

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Ajout de PostgreSQL au PATH" -ForegroundColor White
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Détecter la version de PostgreSQL installée
$pgVersions = Get-ChildItem "C:\Program Files\PostgreSQL" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object -Descending

if ($pgVersions.Count -eq 0) {
    Write-Host "❌ PostgreSQL n'est pas installé dans C:\Program Files\PostgreSQL" -ForegroundColor Red
    Write-Host ""
    Write-Host "Téléchargez PostgreSQL ici :" -ForegroundColor Yellow
    Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

$pgVersion = $pgVersions[0]
$pgPath = "C:\Program Files\PostgreSQL\$pgVersion\bin"

Write-Host "✅ PostgreSQL $pgVersion détecté" -ForegroundColor Green
Write-Host "   Chemin: $pgPath" -ForegroundColor Gray
Write-Host ""

# Vérifier que psql.exe existe
if (!(Test-Path "$pgPath\psql.exe")) {
    Write-Host "❌ psql.exe introuvable dans $pgPath" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✅ psql.exe trouvé" -ForegroundColor Green
Write-Host ""

# Vérifier si déjà dans le PATH
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
$currentMachinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")

if ($currentUserPath -like "*$pgPath*" -or $currentMachinePath -like "*$pgPath*") {
    Write-Host "ℹ️  PostgreSQL est déjà dans le PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Test de la commande psql..." -ForegroundColor Cyan
    
    # Rafraîchir le PATH de la session actuelle
    $env:Path = $currentMachinePath + ";" + $currentUserPath
    
    try {
        $version = & psql --version
        Write-Host "✅ $version" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Redémarrez PowerShell pour que le PATH soit pris en compte" -ForegroundColor Yellow
    }
    
    Write-Host ""
    pause
    exit 0
}

# Ajouter au PATH utilisateur
Write-Host "➕ Ajout de PostgreSQL au PATH utilisateur..." -ForegroundColor Cyan

try {
    [Environment]::SetEnvironmentVariable("Path", "$currentUserPath;$pgPath", "User")
    Write-Host "✅ PostgreSQL ajouté au PATH de manière permanente" -ForegroundColor Green
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ⚠️  ACTION REQUISE" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. FERMEZ cette fenêtre PowerShell" -ForegroundColor White
    Write-Host "  2. ROUVREZ une nouvelle fenêtre PowerShell" -ForegroundColor White
    Write-Host "  3. Tapez: psql --version" -ForegroundColor White
    Write-Host "  4. Si ça fonctionne, lancez: .\01_configurer_postgresql.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "❌ Erreur lors de l'ajout au PATH: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solution manuelle :" -ForegroundColor Yellow
    Write-Host "  1. Ouvrez les Paramètres Windows" -ForegroundColor Gray
    Write-Host "  2. Système → Informations système → Paramètres système avancés" -ForegroundColor Gray
    Write-Host "  3. Variables d'environnement → Path (utilisateur) → Modifier" -ForegroundColor Gray
    Write-Host "  4. Nouveau → Ajoutez: $pgPath" -ForegroundColor Gray
    Write-Host "  5. OK → Redémarrez l'ordinateur" -ForegroundColor Gray
    Write-Host ""
}

pause


