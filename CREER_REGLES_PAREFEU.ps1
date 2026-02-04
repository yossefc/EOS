# ╔════════════════════════════════════════════════════════════════════╗
# ║   CRÉATION DES RÈGLES DE PARE-FEU POUR EOS                        ║
# ╚════════════════════════════════════════════════════════════════════╝

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   CRÉATION DES RÈGLES DE PARE-FEU POUR EOS               " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Vérifier les droits administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERREUR : Ce script nécessite des droits administrateur !" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour exécuter ce script avec les droits admin :" -ForegroundColor Yellow
    Write-Host "1. Faites un clic droit sur PowerShell" -ForegroundColor White
    Write-Host "2. Sélectionnez 'Exécuter en tant qu'administrateur'" -ForegroundColor White
    Write-Host "3. Relancez ce script : .\CREER_REGLES_PAREFEU.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Appuyez sur une touche pour quitter..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✅ Droits administrateur détectés" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# RÈGLE 1 : Backend (Port 5000)
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ Création de la règle pour le Backend (Port 5000)..." -ForegroundColor Yellow
Write-Host ""

# Vérifier si la règle existe déjà
$existingBackend = Get-NetFirewallRule -DisplayName "EOS Backend (Port 5000)" -ErrorAction SilentlyContinue

if ($existingBackend) {
    Write-Host "   ℹ️  La règle existe déjà. Suppression..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "EOS Backend (Port 5000)"
}

# Créer la nouvelle règle
try {
    New-NetFirewallRule `
        -DisplayName "EOS Backend (Port 5000)" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5000 `
        -Action Allow `
        -Profile Domain,Private,Public `
        -Description "Autoriser l'accès au backend EOS (Flask) sur le port 5000"
    
    Write-Host "   ✅ Règle Backend créée avec succès !" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur lors de la création de la règle Backend : $_" -ForegroundColor Red
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# RÈGLE 2 : Frontend (Port 5173)
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ Création de la règle pour le Frontend (Port 5173)..." -ForegroundColor Yellow
Write-Host ""

# Vérifier si la règle existe déjà
$existingFrontend = Get-NetFirewallRule -DisplayName "EOS Frontend (Port 5173)" -ErrorAction SilentlyContinue

if ($existingFrontend) {
    Write-Host "   ℹ️  La règle existe déjà. Suppression..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "EOS Frontend (Port 5173)"
}

# Créer la nouvelle règle
try {
    New-NetFirewallRule `
        -DisplayName "EOS Frontend (Port 5173)" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5173 `
        -Action Allow `
        -Profile Domain,Private,Public `
        -Description "Autoriser l'accès au frontend EOS (Vite/React) sur le port 5173"
    
    Write-Host "   ✅ Règle Frontend créée avec succès !" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur lors de la création de la règle Frontend : $_" -ForegroundColor Red
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   VÉRIFICATION DES RÈGLES CRÉÉES                         " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$rules = Get-NetFirewallRule -DisplayName "*EOS*" | Select-Object DisplayName, Enabled, Direction, Action

if ($rules) {
    $rules | Format-Table -AutoSize
    Write-Host ""
    Write-Host "✅ Les règles de pare-feu sont configurées !" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Vous pouvez maintenant accéder à l'application depuis d'autres ordinateurs." -ForegroundColor White
    Write-Host ""
    Write-Host "PROCHAINE ÉTAPE :" -ForegroundColor Yellow
    Write-Host "1. Démarrez l'application : .\DEMARRER_EOS_SIMPLE.bat" -ForegroundColor White
    Write-Host "2. Trouvez votre IP : ipconfig" -ForegroundColor White
    Write-Host "3. Sur l'autre PC, ouvrez : http://[VOTRE_IP]:5173" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Aucune règle EOS trouvée. Quelque chose s'est mal passé." -ForegroundColor Red
    Write-Host ""
}

Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

