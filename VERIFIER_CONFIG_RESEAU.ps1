# ╔════════════════════════════════════════════════════════════════════╗
# ║   VÉRIFICATION DE LA CONFIGURATION RÉSEAU EOS                     ║
# ╚════════════════════════════════════════════════════════════════════╝

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   VÉRIFICATION DE LA CONFIGURATION RÉSEAU EOS             " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 1 : Adresse IP de cet ordinateur
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ ÉTAPE 1 : Adresse IP de cet ordinateur" -ForegroundColor Yellow
Write-Host ""

$ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" } | Select-Object -First 1

if ($ip) {
    Write-Host "   ✅ Adresse IP trouvée : $($ip.IPAddress)" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📋 Pour vous connecter depuis un autre PC, utilisez :" -ForegroundColor White
    Write-Host "      http://$($ip.IPAddress):5173" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "   ❌ Impossible de trouver l'adresse IP" -ForegroundColor Red
    Write-Host "   ℹ️  Vérifiez votre connexion réseau (Wi-Fi ou Ethernet)" -ForegroundColor Yellow
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 2 : Vérification des règles de pare-feu
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ ÉTAPE 2 : Règles de pare-feu Windows" -ForegroundColor Yellow
Write-Host ""

# Vérifier la règle pour le port 5000 (Backend)
$backendRule = Get-NetFirewallRule -DisplayName "*EOS Backend*" -ErrorAction SilentlyContinue

if ($backendRule) {
    Write-Host "   ✅ Règle pare-feu Backend (Port 5000) : CONFIGURÉE" -ForegroundColor Green
} else {
    Write-Host "   ❌ Règle pare-feu Backend (Port 5000) : NON TROUVÉE" -ForegroundColor Red
    Write-Host "   ℹ️  Pour la créer, exécutez : CREER_REGLES_PAREFEU.ps1" -ForegroundColor Yellow
}

# Vérifier la règle pour le port 5173 (Frontend)
$frontendRule = Get-NetFirewallRule -DisplayName "*EOS Frontend*" -ErrorAction SilentlyContinue

if ($frontendRule) {
    Write-Host "   ✅ Règle pare-feu Frontend (Port 5173) : CONFIGURÉE" -ForegroundColor Green
} else {
    Write-Host "   ❌ Règle pare-feu Frontend (Port 5173) : NON TROUVÉE" -ForegroundColor Red
    Write-Host "   ℹ️  Pour la créer, exécutez : CREER_REGLES_PAREFEU.ps1" -ForegroundColor Yellow
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 3 : Vérification des ports en écoute
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ ÉTAPE 3 : Ports en écoute" -ForegroundColor Yellow
Write-Host ""

# Vérifier si le port 5000 est en écoute (Backend)
$backend = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue

if ($backend) {
    Write-Host "   ✅ Backend (Port 5000) : EN COURS D'EXÉCUTION" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Backend (Port 5000) : NON DÉMARRÉ" -ForegroundColor Yellow
    Write-Host "   ℹ️  Pour le démarrer, exécutez : DEMARRER_EOS_SIMPLE.bat" -ForegroundColor Yellow
}

# Vérifier si le port 5173 est en écoute (Frontend)
$frontend = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue

if ($frontend) {
    Write-Host "   ✅ Frontend (Port 5173) : EN COURS D'EXÉCUTION" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Frontend (Port 5173) : NON DÉMARRÉ" -ForegroundColor Yellow
    Write-Host "   ℹ️  Pour le démarrer, exécutez : DEMARRER_EOS_SIMPLE.bat" -ForegroundColor Yellow
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 4 : Configuration CORS dans le backend
# ═══════════════════════════════════════════════════════════════════════

Write-Host "➤ ÉTAPE 4 : Configuration CORS" -ForegroundColor Yellow
Write-Host ""

$configPath = "D:\EOS\backend\config.py"

if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    
    if ($configContent -match "CORS_ORIGINS") {
        Write-Host "   ✅ Configuration CORS : TROUVÉE" -ForegroundColor Green
        
        # Extraire la ligne CORS_ORIGINS
        $corsLine = ($configContent -split "`n" | Where-Object { $_ -match "CORS_ORIGINS" }) -join "`n"
        Write-Host "   📋 Configuration actuelle :" -ForegroundColor White
        Write-Host "      $corsLine" -ForegroundColor Cyan
    } else {
        Write-Host "   ⚠️  Configuration CORS : NON TROUVÉE" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Fichier config.py non trouvé" -ForegroundColor Red
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════════════
# RÉCAPITULATIF
# ═══════════════════════════════════════════════════════════════════════

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   RÉCAPITULATIF                                           " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($ip) {
    Write-Host "🌐 POUR ACCÉDER DEPUIS UN AUTRE ORDINATEUR :" -ForegroundColor White
    Write-Host ""
    Write-Host "   1. Sur l'autre ordinateur, ouvrez un navigateur" -ForegroundColor White
    Write-Host "   2. Tapez l'adresse suivante :" -ForegroundColor White
    Write-Host ""
    Write-Host "      ┌─────────────────────────────────────────┐" -ForegroundColor Cyan
    Write-Host "      │  http://$($ip.IPAddress):5173            │" -ForegroundColor Cyan
    Write-Host "      └─────────────────────────────────────────┘" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "📝 ACTIONS NÉCESSAIRES :" -ForegroundColor White
Write-Host ""

$actionsNeeded = $false

if (-not $backendRule -or -not $frontendRule) {
    Write-Host "   [ ] Créer les règles de pare-feu :" -ForegroundColor Yellow
    Write-Host "       → Exécutez : .\CREER_REGLES_PAREFEU.ps1" -ForegroundColor Cyan
    Write-Host ""
    $actionsNeeded = $true
}

if (-not $backend -or -not $frontend) {
    Write-Host "   [ ] Démarrer l'application :" -ForegroundColor Yellow
    Write-Host "       → Exécutez : .\DEMARRER_EOS_SIMPLE.bat" -ForegroundColor Cyan
    Write-Host ""
    $actionsNeeded = $true
}

if (-not $actionsNeeded) {
    Write-Host "   ✅ Tout est configuré ! L'accès réseau est prêt." -ForegroundColor Green
    Write-Host ""
}

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

