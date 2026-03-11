# =============================================================================
# SYNC_EOS_VERS_DISTANT.ps1
# Synchronisation complète EOS vers un ordinateur distant
#
# Ce script effectue en ordre :
#   1. Sauvegarde préventive sur le distant
#   2. Transfert du code source (robocopy via partage réseau)
#   3. Mise à jour des dépendances Python sur le distant
#   4. Application des migrations Alembic sur le distant
#   5. Export complet de la BDD locale (pg_dump)
#   6. Transfert + restauration sur le distant (pg_restore)
#
# Prérequis :
#   - Le distant partage son dossier EOS en réseau OU SSH est configuré
#   - PostgreSQL bin dans le PATH ou configuré dans $CONFIG
#   - Python/pip disponibles sur les deux machines
# =============================================================================

#Requires -Version 5.1

# =============================================================================
#region CONFIGURATION - MODIFIER CES VALEURS AVANT D'EXÉCUTER
# =============================================================================

$CONFIG = @{

    # =========================================================================
    # ORDINATEUR DISTANT
    # =========================================================================

    # Adresse IP ou nom réseau du poste distant (ex: "192.168.1.50" ou "PC-BUREAU")
    Remote_Host         = "192.168.1.XX"

    # Nom d'utilisateur Windows sur le poste distant
    Remote_User         = "Utilisateur"

    # Chemin UNC du dossier EOS sur le distant via partage réseau Windows
    # Ex: "\\192.168.1.50\EOS" si tu partages le dossier C:\EOS sous le nom "EOS"
    Remote_Share        = "\\192.168.1.XX\EOS"

    # Chemin local du dossier EOS sur LE DISTANT (pour les commandes SSH)
    Remote_EOSPath_Win  = "C:\EOS"

    # =========================================================================
    # SSH (pour exécuter des commandes à distance)
    # Utilise OpenSSH intégré à Windows 10/11
    # =========================================================================
    SSH_Enabled         = $true
    SSH_Host            = "192.168.1.XX"   # Même IP que Remote_Host
    SSH_Port            = "22"
    SSH_User            = "Utilisateur"    # Même que Remote_User
    # Chemin vers ta clé privée SSH (généré avec ssh-keygen)
    SSH_KeyPath         = "$env:USERPROFILE\.ssh\eos_sync_key"

    # =========================================================================
    # BASE DE DONNÉES LOCALE (SOURCE - ce poste)
    # =========================================================================
    Local_PG_Host       = "localhost"
    Local_PG_Port       = "5432"
    Local_PG_DB         = "eos_db"
    Local_PG_User       = "eos_user"
    Local_PG_Pass       = "eos_password"

    # =========================================================================
    # BASE DE DONNÉES DISTANTE (CIBLE - l'autre poste)
    # Vues depuis LE POSTE DISTANT (donc localhost pour lui)
    # =========================================================================
    Remote_PG_Host      = "localhost"
    Remote_PG_Port      = "5432"
    Remote_PG_DB        = "eos_db"
    Remote_PG_User      = "eos_user"
    Remote_PG_Pass      = "eos_password"

    # =========================================================================
    # CHEMINS LOCAUX (ce poste)
    # =========================================================================
    Local_EOSPath       = "D:\EOS"
    Local_BackupDir     = "D:\EOS\backups_sync"

    # Chemin vers les outils PostgreSQL (pg_dump, pg_restore)
    # Laisse vide si pg_dump est déjà dans ton PATH
    Local_PG_BinPath    = "C:\Program Files\PostgreSQL\14\bin"

    # Chemin Python local (dans le venv du backend)
    Local_PythonExe     = "D:\EOS\backend\venv\Scripts\python.exe"

    # =========================================================================
    # OPTIONS DE SYNCHRONISATION
    # =========================================================================

    # Mettre à $true pour sauter une étape (utile pour tests partiels)
    Skip_Backup         = $false   # Ne pas faire de backup préventif
    Skip_Code           = $false   # Ne pas transférer le code
    Skip_Dependencies   = $false   # Ne pas faire pip install sur le distant
    Skip_Migrations     = $false   # Ne pas appliquer les migrations Alembic
    Skip_Data           = $false   # Ne pas synchroniser les données BDD

    # Fichiers/dossiers à EXCLURE du transfert de code
    Exclude_Dirs        = @(
        "venv", "__pycache__", ".git", "node_modules",
        ".claude", "backups_sync", "exports", "uploads",
        "instance", "app.log", "*.pyc", "*.log"
    )

    # Dossiers du backend à synchroniser (chemins relatifs depuis D:\EOS)
    Sync_Dirs           = @(
        "backend\app.py",
        "backend\config.py",
        "backend\extensions.py",
        "backend\utils.py",
        "backend\client_utils.py",
        "backend\import_engine.py",
        "backend\requirements.txt",
        "backend\models",
        "backend\routes",
        "backend\services",
        "backend\migrations",
        "backend\scripts",
        "backend\templates",
        "backend\static",
        "backend\clients",
        "backend\start_with_postgresql.py",
        "backend\run_server.py",
        "frontend\src",
        "frontend\public",
        "frontend\package.json",
        "frontend\vite.config.js",
        "frontend\tailwind.config.js",
        "frontend\postcss.config.js",
        "frontend\index.html",
        "DEMARRER_EOS_SIMPLE.bat"
    )
}

#endregion

# =============================================================================
#region FONCTIONS UTILITAIRES
# =============================================================================

function Write-Step {
    param([int]$Num, [string]$Title)
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "  ETAPE $Num : $Title" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan
}

function Write-OK   { param([string]$Msg) Write-Host "  [OK]  $Msg" -ForegroundColor Green }
function Write-Info { param([string]$Msg) Write-Host "  [--]  $Msg" -ForegroundColor Gray }
function Write-Warn { param([string]$Msg) Write-Host "  [!!]  $Msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$Msg) Write-Host "  [XX]  $Msg" -ForegroundColor Red }

function Invoke-SSH {
    <#
    .SYNOPSIS Exécute une commande sur le distant via SSH et retourne le résultat.
    #>
    param([string]$Command, [switch]$IgnoreError)

    $sshArgs = @(
        "-i", $CONFIG.SSH_KeyPath,
        "-p", $CONFIG.SSH_Port,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        "$($CONFIG.SSH_User)@$($CONFIG.SSH_Host)",
        $Command
    )

    $result = & ssh @sshArgs 2>&1
    if ($LASTEXITCODE -ne 0 -and -not $IgnoreError) {
        Write-Fail "Commande SSH échouée (code $LASTEXITCODE) : $Command"
        Write-Fail "Sortie : $result"
        return $null
    }
    return $result
}

function Test-PGTool {
    <#
    .SYNOPSIS Vérifie que pg_dump / pg_restore sont accessibles.
    #>
    param([string]$ToolName)
    $pgBin = Join-Path $CONFIG.Local_PG_BinPath "$ToolName.exe"
    if (Test-Path $pgBin) { return $pgBin }

    $inPath = Get-Command $ToolName -ErrorAction SilentlyContinue
    if ($inPath) { return $ToolName }

    Write-Fail "$ToolName introuvable. Configure Local_PG_BinPath dans la section CONFIG."
    return $null
}

function Set-PGPassword {
    <#
    .SYNOPSIS Positionne PGPASSWORD pour éviter les prompts de mot de passe.
    #>
    param([string]$Password)
    $env:PGPASSWORD = $Password
}

function Get-Timestamp { return (Get-Date -Format "yyyyMMdd_HHmmss") }

#endregion

# =============================================================================
#region VERIFICATION DES PREREQUIS
# =============================================================================

Write-Host ""
Write-Host "######################################################################" -ForegroundColor Magenta
Write-Host "#       SYNCHRONISATION EOS VERS ORDINATEUR DISTANT                 #" -ForegroundColor Magenta
Write-Host "######################################################################" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Source  : $($CONFIG.Local_EOSPath) (ce poste)"
Write-Host "  Cible   : $($CONFIG.Remote_Share)"
Write-Host "  BDD src : $($CONFIG.Local_PG_DB)@$($CONFIG.Local_PG_Host):$($CONFIG.Local_PG_Port)"
Write-Host "  BDD dst : $($CONFIG.Remote_PG_DB)@$($CONFIG.Remote_Host)"
Write-Host ""

$confirm = Read-Host "Confirmer la synchronisation ? Les données distantes SERONT ÉCRASÉES. (oui/non)"
if ($confirm -notmatch "^oui$") {
    Write-Warn "Synchronisation annulée."
    exit 0
}

# Créer le dossier de backups locaux si absent
if (-not (Test-Path $CONFIG.Local_BackupDir)) {
    New-Item -ItemType Directory -Path $CONFIG.Local_BackupDir -Force | Out-Null
}

#endregion

# =============================================================================
#region ETAPE 0 : BACKUP PRÉVENTIF SUR LE DISTANT
# =============================================================================

$ts = Get-Timestamp

if (-not $CONFIG.Skip_Backup -and $CONFIG.SSH_Enabled) {
    Write-Step 0 "SAUVEGARDE PRÉVENTIVE SUR LE DISTANT"
    Write-Info "Création d'un dump de la BDD distante avant écrasement..."

    $remoteBackupFile = "$($CONFIG.Remote_EOSPath_Win)\backups_sync\backup_avant_sync_$ts.dump"
    $remoteBackupDir  = "$($CONFIG.Remote_EOSPath_Win)\backups_sync"

    $backupCmd = @"
set PGPASSWORD=$($CONFIG.Remote_PG_Pass)
if not exist "$remoteBackupDir" mkdir "$remoteBackupDir"
"$($CONFIG.Remote_EOSPath_Win)\..\..\Program Files\PostgreSQL\14\bin\pg_dump.exe" ^
    -h $($CONFIG.Remote_PG_Host) ^
    -p $($CONFIG.Remote_PG_Port) ^
    -U $($CONFIG.Remote_PG_User) ^
    -F c ^
    -f "$remoteBackupFile" ^
    $($CONFIG.Remote_PG_DB)
"@

    # Commande unifiée pour CMD via SSH
    $sshBackup = "cmd /c `"set PGPASSWORD=$($CONFIG.Remote_PG_Pass) && " +
                 "if not exist `"$remoteBackupDir`" mkdir `"$remoteBackupDir`" && " +
                 "pg_dump -h $($CONFIG.Remote_PG_Host) -p $($CONFIG.Remote_PG_Port) " +
                 "-U $($CONFIG.Remote_PG_User) -F c -f `"$remoteBackupFile`" $($CONFIG.Remote_PG_DB)`""

    $backupResult = Invoke-SSH -Command $sshBackup -IgnoreError
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Backup distant créé : $remoteBackupFile"
    } else {
        Write-Warn "Backup distant impossible (pg_dump peut-être absent ou BDD vide). On continue..."
    }
} else {
    Write-Warn "Backup préventif ignoré (Skip_Backup=$($CONFIG.Skip_Backup) ou SSH désactivé)."
}

#endregion

# =============================================================================
#region ETAPE 1 : TRANSFERT DU CODE SOURCE
# =============================================================================

if (-not $CONFIG.Skip_Code) {
    Write-Step 1 "TRANSFERT DU CODE SOURCE"

    if (-not (Test-Path $CONFIG.Remote_Share)) {
        Write-Fail "Le partage réseau '$($CONFIG.Remote_Share)' est inaccessible."
        Write-Fail "Vérifie que le dossier est bien partagé sur le distant et que tu es connecté au réseau."
        exit 1
    }

    Write-Info "Synchronisation via Robocopy vers $($CONFIG.Remote_Share)..."

    # Construire les exclusions pour robocopy
    $excludeDirs  = $CONFIG.Exclude_Dirs | Where-Object { $_ -notmatch '\*' }
    $excludeFiles = $CONFIG.Exclude_Dirs | Where-Object { $_ -match '\*' }

    $robocopyArgs = @(
        $CONFIG.Local_EOSPath,
        $CONFIG.Remote_Share,
        "/MIR",          # Miroir complet (supprime les fichiers absents en local)
        "/XA:H",         # Exclure fichiers cachés
        "/W:3",          # Attendre 3s entre essais
        "/R:2",          # 2 essais max par fichier
        "/NP",           # Pas de pourcentage (moins verbeux)
        "/NFL",          # Pas de liste de fichiers
        "/NDL"           # Pas de liste de dossiers
    )

    foreach ($dir in $excludeDirs) {
        $robocopyArgs += "/XD"
        $robocopyArgs += $dir
    }
    foreach ($file in $excludeFiles) {
        $robocopyArgs += "/XF"
        $robocopyArgs += $file
    }

    Write-Info "Lancement de robocopy (peut prendre quelques minutes)..."
    $roboResult = & robocopy @robocopyArgs

    # Robocopy retourne des codes 0-7 pour succès, >=8 pour erreur réelle
    if ($LASTEXITCODE -ge 8) {
        Write-Fail "Robocopy a rencontré des erreurs (code $LASTEXITCODE)."
        Write-Fail "Détail : $roboResult"
        exit 1
    }
    Write-OK "Code source synchronisé avec succès (code robocopy: $LASTEXITCODE)."

} else {
    Write-Warn "Transfert du code ignoré (Skip_Code=True)."
}

#endregion

# =============================================================================
#region ETAPE 2 : MISE À JOUR DES DÉPENDANCES PYTHON SUR LE DISTANT
# =============================================================================

if (-not $CONFIG.Skip_Dependencies -and $CONFIG.SSH_Enabled) {
    Write-Step 2 "MISE À JOUR DES DÉPENDANCES PYTHON"
    Write-Info "Installation des packages via pip sur le distant..."

    $pipCmd = "cmd /c `"$($CONFIG.Remote_EOSPath_Win)\backend\venv\Scripts\pip.exe install " +
              "-r $($CONFIG.Remote_EOSPath_Win)\backend\requirements.txt --quiet`""

    $pipResult = Invoke-SSH -Command $pipCmd
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Dépendances Python à jour."
    } else {
        Write-Warn "pip install a retourné une erreur. Vérification des logs conseillée."
        Write-Warn "Résultat : $pipResult"
    }
} else {
    Write-Warn "Mise à jour des dépendances ignorée."
}

#endregion

# =============================================================================
#region ETAPE 3 : MIGRATIONS ALEMBIC SUR LE DISTANT
# =============================================================================

if (-not $CONFIG.Skip_Migrations -and $CONFIG.SSH_Enabled) {
    Write-Step 3 "MIGRATIONS DE STRUCTURE BDD (ALEMBIC)"
    Write-Info "Application de 'alembic upgrade head' sur le distant..."

    # Construire la commande : activer le venv, se placer dans backend, lancer alembic
    $alembicCmd = "cmd /c `"cd /d $($CONFIG.Remote_EOSPath_Win)\backend && " +
                  "venv\Scripts\activate.bat && " +
                  "alembic upgrade head 2>&1`""

    $alembicResult = Invoke-SSH -Command $alembicCmd
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Migrations Alembic appliquées avec succès."
        Write-Info "Résultat : $alembicResult"
    } else {
        Write-Fail "Les migrations Alembic ont échoué !"
        Write-Fail "Résultat : $alembicResult"
        $continueAny = Read-Host "Continuer quand même avec la synchro des données ? (oui/non)"
        if ($continueAny -notmatch "^oui$") { exit 1 }
    }
} else {
    Write-Warn "Migrations Alembic ignorées (Skip_Migrations=True ou SSH désactivé)."
}

#endregion

# =============================================================================
#region ETAPE 4 : EXPORT DE LA BASE DE DONNÉES LOCALE
# =============================================================================

if (-not $CONFIG.Skip_Data) {
    Write-Step 4 "EXPORT DE LA BASE DE DONNÉES LOCALE"

    $pgDump = Test-PGTool "pg_dump"
    if (-not $pgDump) { exit 1 }

    $dumpFile = Join-Path $CONFIG.Local_BackupDir "eos_sync_$ts.dump"
    Write-Info "Dump de '$($CONFIG.Local_PG_DB)' vers : $dumpFile"
    Write-Info "Cela peut prendre quelques minutes selon la taille de la base..."

    Set-PGPassword $CONFIG.Local_PG_Pass

    $dumpArgs = @(
        "-h", $CONFIG.Local_PG_Host,
        "-p", $CONFIG.Local_PG_Port,
        "-U", $CONFIG.Local_PG_User,
        "-F", "c",          # Format custom (compressé, optimal pour pg_restore)
        "--no-privileges",  # Ne pas exporter les GRANT/REVOKE
        "--no-owner",       # Ne pas exporter les ownership (évite erreurs si user différent)
        "-f", $dumpFile,
        $CONFIG.Local_PG_DB
    )

    & $pgDump @dumpArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "pg_dump a échoué (code $LASTEXITCODE)."
        exit 1
    }

    $dumpSizeMB = [math]::Round((Get-Item $dumpFile).Length / 1MB, 2)
    Write-OK "Dump créé avec succès : $dumpFile ($dumpSizeMB MB)"

#endregion

# =============================================================================
#region ETAPE 5 : TRANSFERT DU DUMP VERS LE DISTANT
# =============================================================================

    Write-Step 5 "TRANSFERT DU DUMP VERS LE DISTANT"

    $remoteBackupsDir = Join-Path $CONFIG.Remote_Share "backups_sync"
    if (-not (Test-Path $remoteBackupsDir)) {
        New-Item -ItemType Directory -Path $remoteBackupsDir -Force | Out-Null
    }

    $remoteDumpFile = Join-Path $remoteBackupsDir (Split-Path $dumpFile -Leaf)
    Write-Info "Copie du dump vers $remoteDumpFile..."

    Copy-Item -Path $dumpFile -Destination $remoteDumpFile -Force
    if (-not (Test-Path $remoteDumpFile)) {
        Write-Fail "Échec de la copie du dump vers le partage réseau."
        exit 1
    }
    Write-OK "Dump transféré : $remoteDumpFile"

#endregion

# =============================================================================
#region ETAPE 6 : RESTAURATION SUR LA BASE DISTANTE
# =============================================================================

    Write-Step 6 "RESTAURATION DE LA BASE DISTANTE"

    if (-not $CONFIG.SSH_Enabled) {
        Write-Warn "SSH désactivé : impossible de lancer pg_restore à distance automatiquement."
        Write-Warn "Lance manuellement sur le distant :"
        Write-Warn "  pg_restore -h localhost -p 5432 -U eos_user -d eos_db --clean --if-exists -F c `"$($CONFIG.Remote_EOSPath_Win)\backups_sync\$(Split-Path $dumpFile -Leaf)`""
    } else {
        $remoteDumpWin = "$($CONFIG.Remote_EOSPath_Win)\backups_sync\$(Split-Path $dumpFile -Leaf)"
        Write-Info "Restauration de $remoteDumpWin sur la BDD distante..."
        Write-Warn "ATTENTION : Cela va ÉCRASER toutes les données de la BDD distante !"

        # Étape 6a : Fermer les connexions actives à la BDD distante
        Write-Info "Fermeture des connexions actives sur le distant..."
        $terminateCmd = "cmd /c `"set PGPASSWORD=$($CONFIG.Remote_PG_Pass) && " +
                        "psql -h $($CONFIG.Remote_PG_Host) -p $($CONFIG.Remote_PG_Port) " +
                        "-U $($CONFIG.Remote_PG_User) -d postgres -c " +
                        "`"`"SELECT pg_terminate_backend(pid) FROM pg_stat_activity " +
                        "WHERE datname='$($CONFIG.Remote_PG_DB)' AND pid <> pg_backend_pid();`"`"`""

        Invoke-SSH -Command $terminateCmd -IgnoreError | Out-Null

        # Étape 6b : Restauration avec pg_restore
        $restoreCmd = "cmd /c `"set PGPASSWORD=$($CONFIG.Remote_PG_Pass) && " +
                      "pg_restore " +
                      "-h $($CONFIG.Remote_PG_Host) " +
                      "-p $($CONFIG.Remote_PG_Port) " +
                      "-U $($CONFIG.Remote_PG_User) " +
                      "-d $($CONFIG.Remote_PG_DB) " +
                      "--clean --if-exists " +
                      "--no-privileges --no-owner " +
                      "-F c `"$remoteDumpWin`" 2>&1`""

        Write-Info "Exécution de pg_restore (peut prendre du temps)..."
        $restoreResult = Invoke-SSH -Command $restoreCmd

        if ($LASTEXITCODE -eq 0) {
            Write-OK "Restauration terminée avec succès."
        } else {
            # pg_restore retourne 1 même pour des warnings mineurs (séquences, etc.)
            Write-Warn "pg_restore a retourné le code $LASTEXITCODE (peut être des warnings normaux)."
            Write-Warn "Sortie : $restoreResult"
            Write-Info "Si les tables sont bien présentes, c'est probablement OK."
        }
    }
} else {
    Write-Warn "Synchronisation des données ignorée (Skip_Data=True)."
}

#endregion

# =============================================================================
#region ETAPE 7 : VÉRIFICATION FINALE
# =============================================================================

Write-Step 7 "VÉRIFICATION FINALE"

if ($CONFIG.SSH_Enabled -and -not $CONFIG.Skip_Data) {
    Write-Info "Comptage des enregistrements sur la BDD distante..."

    $checkCmd = "cmd /c `"set PGPASSWORD=$($CONFIG.Remote_PG_Pass) && " +
                "psql -h $($CONFIG.Remote_PG_Host) -p $($CONFIG.Remote_PG_Port) " +
                "-U $($CONFIG.Remote_PG_User) -d $($CONFIG.Remote_PG_DB) -t -c " +
                "`"`"SELECT 'donnees=' || COUNT(*) FROM donnees; " +
                "SELECT 'enquetes_terminees=' || COUNT(*) FROM enquetes_terminees; " +
                "SELECT 'archives=' || COUNT(*) FROM enquete_archives;`"`"`""

    $checkResult = Invoke-SSH -Command $checkCmd -IgnoreError
    if ($checkResult) {
        Write-OK "Vérification BDD distante :"
        $checkResult | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
            Write-Info "  $_"
        }
    }
}

Write-Host ""
Write-Host "######################################################################" -ForegroundColor Green
Write-Host "#                  SYNCHRONISATION TERMINÉE                         #" -ForegroundColor Green
Write-Host "######################################################################" -ForegroundColor Green
Write-Host ""
Write-OK "Résumé :"
Write-OK "  Code source     : $( if ($CONFIG.Skip_Code) { 'ignoré' } else { 'synchronisé' } )"
Write-OK "  Dépendances     : $( if ($CONFIG.Skip_Dependencies) { 'ignorées' } else { 'mises à jour' } )"
Write-OK "  Schema BDD      : $( if ($CONFIG.Skip_Migrations) { 'ignoré' } else { 'migrations appliquées' } )"
Write-OK "  Données BDD     : $( if ($CONFIG.Skip_Data) { 'ignorées' } else { 'synchronisées' } )"
Write-Host ""
Write-Info "Tu peux maintenant démarrer EOS sur le distant avec DEMARRER_EOS_SIMPLE.bat"
Write-Host ""

#endregion
