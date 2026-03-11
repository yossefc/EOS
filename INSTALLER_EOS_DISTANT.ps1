# =============================================================================
# INSTALLER_EOS_DISTANT.ps1
# Script d'installation initiale d'EOS sur un ordinateur distant VIERGE
#
# À EXÉCUTER UNE SEULE FOIS sur l'ordinateur distant (ou en SSH depuis le local)
#
# Ce script :
#   1. Crée la structure de dossiers EOS
#   2. Configure le partage réseau Windows
#   3. Crée l'utilisateur et la base de données PostgreSQL
#   4. Configure l'environnement Python (venv)
#   5. Configure SSH pour les synchronisations futures
# =============================================================================

#Requires -RunAsAdministrator

# =============================================================================
#region CONFIGURATION
# =============================================================================

$CONFIG = @{
    EOS_Path         = "C:\EOS"
    PG_BinPath       = "C:\Program Files\PostgreSQL\14\bin"
    PG_SuperUser     = "postgres"
    PG_SuperPass     = "postgres"    # Mot de passe de l'admin postgres
    PG_DB            = "eos_db"
    PG_User          = "eos_user"
    PG_Pass          = "eos_password"
    PG_Port          = "5432"
    Share_Name       = "EOS"         # Nom du partage réseau Windows
    Share_User       = ""            # Laisser vide = tous les utilisateurs du réseau
    Python_Version   = "3.11"        # Version Python requise
}

#endregion

# =============================================================================
#region FONCTIONS
# =============================================================================

function Write-Step { param([int]$N, [string]$T) Write-Host "`n=== ETAPE $N : $T ===" -ForegroundColor Cyan }
function Write-OK   { param([string]$M) Write-Host "  [OK] $M" -ForegroundColor Green }
function Write-Info { param([string]$M) Write-Host "  [--] $M" -ForegroundColor Gray }
function Write-Warn { param([string]$M) Write-Host "  [!!] $M" -ForegroundColor Yellow }
function Write-Fail { param([string]$M) Write-Host "  [XX] $M" -ForegroundColor Red }

function Invoke-PG {
    param([string]$SQL, [string]$DB = "postgres")
    $env:PGPASSWORD = $CONFIG.PG_SuperPass
    $psqlExe = Join-Path $CONFIG.PG_BinPath "psql.exe"
    & $psqlExe -h localhost -p $CONFIG.PG_Port -U $CONFIG.PG_SuperUser -d $DB -c $SQL 2>&1
}

#endregion

Write-Host "`n###### INSTALLATION EOS SUR ORDINATEUR DISTANT ######" -ForegroundColor Magenta

# =============================================================================
Write-Step 1 "CRÉATION DE LA STRUCTURE DE DOSSIERS"
# =============================================================================

$dirs = @(
    $CONFIG.EOS_Path,
    "$($CONFIG.EOS_Path)\backend",
    "$($CONFIG.EOS_Path)\frontend",
    "$($CONFIG.EOS_Path)\backups_sync",
    "$($CONFIG.EOS_Path)\backend\uploads",
    "$($CONFIG.EOS_Path)\backend\exports",
    "$($CONFIG.EOS_Path)\backend\logs"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-OK "Créé : $dir"
    } else {
        Write-Info "Existe déjà : $dir"
    }
}

# =============================================================================
Write-Step 2 "CONFIGURATION DU PARTAGE RÉSEAU WINDOWS"
# =============================================================================

$shareName = $CONFIG.Share_Name
$existingShare = Get-SmbShare -Name $shareName -ErrorAction SilentlyContinue

if ($existingShare) {
    Write-Info "Partage '$shareName' existe déjà."
} else {
    try {
        New-SmbShare -Name $shareName `
                     -Path $CONFIG.EOS_Path `
                     -FullAccess "Tout le monde" `
                     -Description "Dossier EOS (accès synchronisation)" | Out-Null
        Write-OK "Partage réseau créé : \\$(hostname)\$shareName -> $($CONFIG.EOS_Path)"
    } catch {
        Write-Fail "Impossible de créer le partage : $_"
        Write-Info "Crée-le manuellement : clic droit sur $($CONFIG.EOS_Path) > Propriétés > Partage"
    }
}

# Autoriser le partage dans le pare-feu Windows
netsh advfirewall firewall set rule group="Partage de fichiers et d'imprimantes" new enable=yes | Out-Null
Write-OK "Règle pare-feu pour le partage de fichiers activée."

# =============================================================================
Write-Step 3 "CRÉATION DE LA BASE DE DONNÉES POSTGRESQL"
# =============================================================================

$psqlExe = Join-Path $CONFIG.PG_BinPath "psql.exe"
if (-not (Test-Path $psqlExe)) {
    Write-Fail "psql.exe introuvable dans $($CONFIG.PG_BinPath)"
    Write-Fail "Installe PostgreSQL 14 depuis https://www.postgresql.org/download/windows/"
    exit 1
}

# Créer l'utilisateur PostgreSQL
Write-Info "Création de l'utilisateur PostgreSQL '$($CONFIG.PG_User)'..."
Invoke-PG "DO `$`$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='$($CONFIG.PG_User)') THEN CREATE ROLE $($CONFIG.PG_User) WITH LOGIN PASSWORD '$($CONFIG.PG_Pass)'; END IF; END `$`$;"
Write-OK "Utilisateur '$($CONFIG.PG_User)' prêt."

# Créer la base de données
Write-Info "Création de la base '$($CONFIG.PG_DB)'..."
$env:PGPASSWORD = $CONFIG.PG_SuperPass
$dbExists = & $psqlExe -h localhost -p $CONFIG.PG_Port -U $CONFIG.PG_SuperUser -tAc "SELECT 1 FROM pg_database WHERE datname='$($CONFIG.PG_DB)'" 2>&1

if ($dbExists -eq "1") {
    Write-Info "La base '$($CONFIG.PG_DB)' existe déjà."
} else {
    Invoke-PG "CREATE DATABASE $($CONFIG.PG_DB) OWNER $($CONFIG.PG_User) ENCODING 'UTF8' LC_COLLATE='French_France.1252' LC_CTYPE='French_France.1252';"
    Write-OK "Base '$($CONFIG.PG_DB)' créée."
}

# Droits complets
Invoke-PG "GRANT ALL PRIVILEGES ON DATABASE $($CONFIG.PG_DB) TO $($CONFIG.PG_User);"
Write-OK "Droits accordés à $($CONFIG.PG_User) sur $($CONFIG.PG_DB)."

# =============================================================================
Write-Step 4 "CONFIGURATION PYTHON (ENVIRONNEMENT VIRTUEL)"
# =============================================================================

$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExe) {
    Write-Fail "Python introuvable dans le PATH."
    Write-Fail "Installe Python 3.11+ depuis https://www.python.org/downloads/"
    Write-Fail "Coche bien 'Add Python to PATH' pendant l'installation."
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Info "Python trouvé : $pythonVersion"

$venvPath = "$($CONFIG.EOS_Path)\backend\venv"
if (-not (Test-Path "$venvPath\Scripts\python.exe")) {
    Write-Info "Création du venv dans $venvPath..."
    python -m venv $venvPath
    Write-OK "Environnement virtuel créé."
} else {
    Write-Info "Venv déjà présent."
}

# Mise à jour de pip
Write-Info "Mise à jour de pip..."
& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip --quiet
Write-OK "pip à jour."

# =============================================================================
Write-Step 5 "CONFIGURATION SSH (pour les synchronisations futures)"
# =============================================================================

$opensshFeature = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($opensshFeature.State -eq "Installed") {
    Write-Info "OpenSSH Server déjà installé."
} else {
    Write-Info "Installation d'OpenSSH Server..."
    try {
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
        Write-OK "OpenSSH Server installé."
    } catch {
        Write-Warn "Impossible d'installer OpenSSH automatiquement : $_"
        Write-Warn "Installe-le manuellement : Paramètres > Applications > Fonctionnalités facultatives > OpenSSH Server"
    }
}

# Démarrer et activer le service SSH
try {
    Start-Service sshd -ErrorAction Stop
    Set-Service -Name sshd -StartupType Automatic
    Write-OK "Service SSH (sshd) démarré et configuré en démarrage automatique."
} catch {
    Write-Warn "Impossible de démarrer sshd : $_"
}

# Autoriser SSH dans le pare-feu
try {
    $existingRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if (-not $existingRule) {
        New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" `
                            -DisplayName "OpenSSH Server (TCP-In)" `
                            -Direction Inbound -Protocol TCP `
                            -LocalPort 22 -Action Allow | Out-Null
        Write-OK "Règle pare-feu SSH (port 22) créée."
    } else {
        Write-Info "Règle pare-feu SSH déjà présente."
    }
} catch {
    Write-Warn "Impossible de créer la règle pare-feu SSH : $_"
}

# Afficher l'IP pour la configuration du poste source
$ipAddresses = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" }).IPAddress
Write-Host ""
Write-Host "  ================================================================" -ForegroundColor Yellow
Write-Host "  INFORMATION IMPORTANTE - à noter sur le POSTE SOURCE :" -ForegroundColor Yellow
Write-Host "  ================================================================" -ForegroundColor Yellow
Write-Host "  Adresse(s) IP de ce poste :" -ForegroundColor Yellow
foreach ($ip in $ipAddresses) {
    Write-Host "    -> $ip" -ForegroundColor White
}
Write-Host "  Partage réseau : \\$(hostname)\$($CONFIG.Share_Name)" -ForegroundColor White
Write-Host "  Utilisateur SSH : $env:USERNAME" -ForegroundColor White
Write-Host "  ================================================================" -ForegroundColor Yellow

# =============================================================================
Write-Step 6 "FICHIER .ENV DU BACKEND"
# =============================================================================

$envFile = "$($CONFIG.EOS_Path)\backend\.env"
if (-not (Test-Path $envFile)) {
    $envContent = @"
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql+psycopg2://$($CONFIG.PG_User):$($CONFIG.PG_Pass)@localhost:$($CONFIG.PG_Port)/$($CONFIG.PG_DB)
SECRET_KEY=$(New-Guid)
"@
    Set-Content -Path $envFile -Value $envContent -Encoding UTF8
    Write-OK "Fichier .env créé : $envFile"
} else {
    Write-Info ".env déjà présent (non écrasé)."
}

Write-Host ""
Write-Host "######################################################################" -ForegroundColor Green
Write-Host "#           INSTALLATION DISTANTE TERMINÉE                          #" -ForegroundColor Green
Write-Host "######################################################################" -ForegroundColor Green
Write-Host ""
Write-OK "Le poste distant est prêt à recevoir des synchronisations."
Write-Info "Prochaine étape : génère et copie ta clé SSH depuis le POSTE SOURCE"
Write-Info "  (voir le guide GUIDE_CONFIGURATION_SYNC.md)"
Write-Host ""
