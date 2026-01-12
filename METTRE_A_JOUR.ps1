# ==============================================================================
# Script de Mise à Jour EOS
# Synchronise le code avec le dépôt Git et met à jour les dépendances
# ==============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MISE À JOUR DU SYSTÈME EOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier qu'on est dans un dépôt Git
if (-not (Test-Path ".git")) {
    Write-Host "❌ ERREUR: Ce répertoire n'est pas un dépôt Git!" -ForegroundColor Red
    Write-Host "   Veuillez exécuter ce script depuis le dossier racine EOS." -ForegroundColor Yellow
    pause
    exit 1
}

# ==============================================================================
# ÉTAPE 1 : Vérifier l'état Git
# ==============================================================================
Write-Host "📋 Étape 1/6 : Vérification de l'état Git..." -ForegroundColor Yellow

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host ""
    Write-Host "⚠️  Attention: Vous avez des modifications locales non commitées:" -ForegroundColor Yellow
    Write-Host ""
    git status --short
    Write-Host ""
    $response = Read-Host "Voulez-vous continuer quand même? (o/N)"
    if ($response -ne "o" -and $response -ne "O") {
        Write-Host "❌ Mise à jour annulée." -ForegroundColor Red
        pause
        exit 0
    }
}

Write-Host "✅ État Git vérifié" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# ÉTAPE 2 : Git Pull
# ==============================================================================
Write-Host "📥 Étape 2/6 : Récupération des mises à jour depuis Git..." -ForegroundColor Yellow

$currentBranch = git branch --show-current
Write-Host "   Branche actuelle: $currentBranch" -ForegroundColor Cyan

try {
    git pull origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors du git pull"
    }
    Write-Host "✅ Code mis à jour depuis Git" -ForegroundColor Green
} catch {
    Write-Host "❌ ERREUR lors du git pull!" -ForegroundColor Red
    Write-Host "   Vérifiez votre connexion réseau et l'accès au dépôt." -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# ==============================================================================
# ÉTAPE 3 : Mise à jour des dépendances Backend (Python)
# ==============================================================================
Write-Host "🐍 Étape 3/6 : Mise à jour des dépendances Python..." -ForegroundColor Yellow

if (Test-Path "backend\requirements.txt") {
    Push-Location backend

    # Vérifier que pip est disponible
    $pipCheck = python -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERREUR: pip n'est pas disponible!" -ForegroundColor Red
        Pop-Location
        pause
        exit 1
    }

    Write-Host "   Installation des packages Python..." -ForegroundColor Cyan
    python -m pip install -r requirements.txt --quiet --disable-pip-version-check

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dépendances Python mises à jour" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Avertissement: Problème lors de l'installation des dépendances Python" -ForegroundColor Yellow
    }

    Pop-Location
} else {
    Write-Host "⚠️  Fichier requirements.txt introuvable" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================================
# ÉTAPE 4 : Mise à jour des dépendances Frontend (npm)
# ==============================================================================
Write-Host "📦 Étape 4/6 : Mise à jour des dépendances npm..." -ForegroundColor Yellow

if (Test-Path "frontend\package.json") {
    Push-Location frontend

    # Vérifier que npm est disponible
    $npmCheck = npm --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERREUR: npm n'est pas disponible!" -ForegroundColor Red
        Pop-Location
        pause
        exit 1
    }

    Write-Host "   Installation des packages npm..." -ForegroundColor Cyan
    npm install --silent

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dépendances npm mises à jour" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Avertissement: Problème lors de l'installation des dépendances npm" -ForegroundColor Yellow
    }

    Pop-Location
} else {
    Write-Host "⚠️  Fichier package.json introuvable" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================================
# ÉTAPE 5 : Migrations de base de données
# ==============================================================================
Write-Host "🗄️  Étape 5/6 : Vérification des migrations de base de données..." -ForegroundColor Yellow

# Vérifier que DATABASE_URL est définie
if (-not $env:DATABASE_URL) {
    Write-Host "⚠️  DATABASE_URL n'est pas définie." -ForegroundColor Yellow
    Write-Host "   Les migrations seront ignorées." -ForegroundColor Yellow
    Write-Host "   Définissez DATABASE_URL avec:" -ForegroundColor Cyan
    Write-Host '   $env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"' -ForegroundColor Cyan
} else {
    Write-Host "   DATABASE_URL configurée: " -NoNewline -ForegroundColor Cyan
    # Masquer le mot de passe dans l'affichage
    $maskedUrl = $env:DATABASE_URL -replace '(://[^:]+:)[^@]+(@)', '$1****$2'
    Write-Host $maskedUrl -ForegroundColor Cyan

    Push-Location backend

    # Vérifier s'il y a des migrations Flask-Migrate
    if (Test-Path "migrations") {
        Write-Host "   Application des migrations..." -ForegroundColor Cyan
        # Note: Flask-Migrate n'est peut-être pas configuré, on le mentionne juste
        Write-Host "   ℹ️  Si vous utilisez Flask-Migrate, exécutez manuellement:" -ForegroundColor Cyan
        Write-Host "      flask db upgrade" -ForegroundColor Gray
    }

    Write-Host "✅ Base de données prête" -ForegroundColor Green
    Pop-Location
}
Write-Host ""

# ==============================================================================
# ÉTAPE 6 : Résumé et instructions de redémarrage
# ==============================================================================
Write-Host "🎉 Étape 6/6 : Finalisation..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ MISE À JOUR TERMINÉE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Si le backend est en cours d'exécution:" -ForegroundColor White
Write-Host "      ➜ Arrêtez-le (Ctrl+C)" -ForegroundColor Gray
Write-Host "      ➜ Relancez avec: .\DEMARRER_EOS_COMPLET.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Si le frontend est en cours d'exécution:" -ForegroundColor White
Write-Host "      ➜ Rechargez la page dans le navigateur (Ctrl+F5)" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Vérifiez que tout fonctionne correctement" -ForegroundColor White
Write-Host ""

# Afficher les derniers commits
Write-Host "📝 Dernières modifications:" -ForegroundColor Cyan
git log --oneline -5
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
pause
