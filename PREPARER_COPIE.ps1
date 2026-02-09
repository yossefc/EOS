# Script PowerShell pour préparer les fichiers à copier vers l'autre PC
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 PRÉPARATION DES FICHIERS POUR L'AUTRE ORDINATEUR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Créer le dossier de destination
$destination = "D:\EOS\FICHIERS_CORRIGES_SHERLOCK"
Write-Host "Création du dossier: $destination" -ForegroundColor Yellow

if (Test-Path $destination) {
    Remove-Item -Path $destination -Recurse -Force
}
New-Item -ItemType Directory -Path $destination -Force | Out-Null

Write-Host "✅ Dossier créé" -ForegroundColor Green
Write-Host ""

# Liste des fichiers à copier
$files = @(
    @{
        Source = "D:\EOS\backend\import_engine.py"
        Dest = "$destination\import_engine.py"
        Description = "Normalisation accents pour l'import"
    },
    @{
        Source = "D:\EOS\backend\models\import_config.py"
        Dest = "$destination\import_config.py"
        Description = "Normalisation dans extract_value"
    },
    @{
        Source = "D:\EOS\backend\app.py"
        Dest = "$destination\app.py"
        Description = "Formatage dates/codes pour l'export"
    }
)

# Copier les fichiers
Write-Host "📄 Copie des fichiers corrigés:" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $files) {
    if (Test-Path $file.Source) {
        Copy-Item -Path $file.Source -Destination $file.Dest -Force
        Write-Host "✅ $($file.Source | Split-Path -Leaf)" -ForegroundColor Green
        Write-Host "   → $($file.Description)" -ForegroundColor Gray
    } else {
        Write-Host "❌ MANQUANT: $($file.Source)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📋 INSTRUCTIONS POUR L'AUTRE ORDINATEUR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Créer un fichier d'instructions
$instructions = @"
============================================================
📦 INSTRUCTIONS - Installation sur l'autre ordinateur
============================================================

1️⃣ COPIER CE DOSSIER sur l'autre ordinateur
   → Copiez tout le dossier: FICHIERS_CORRIGES_SHERLOCK

2️⃣ SUR L'AUTRE ORDINATEUR:

   a) ARRÊTER Flask (Ctrl+C dans le terminal)
   
   b) REMPLACER les fichiers:
      
      Copiez: import_engine.py
           → D:\EOS\backend\import_engine.py
      
      Copiez: import_config.py
           → D:\EOS\backend\models\import_config.py
      
      Copiez: app.py
           → D:\EOS\backend\app.py
   
   c) REDÉMARRER Flask:
      cd D:\EOS\backend
      python app.py
   
   d) VÉRIFIER que tout est OK:
      cd D:\EOS\backend
      python DIAGNOSTIC_COMPLET.py
   
   e) SUPPRIMER l'ancien fichier Sherlock dans l'interface web
   
   f) RÉIMPORTER le fichier Sherlock
   
   g) TESTER l'export

3️⃣ VÉRIFICATION FINALE:

   Les champs avec accents doivent être remplis:
   ✅ RéférenceInterne
   ✅ EC-Civilité
   ✅ EC-Prénom
   ✅ EC-Localité Naissance
   
   Les dates doivent être au format JJ/MM/AAAA:
   ✅ 07/02/1975 (pas 1975-02-07 00:00:00)
   
   Les codes ne doivent pas avoir de .0:
   ✅ 88100 (pas 88100.0)

============================================================
⚠️ IMPORTANT: REDÉMARRER Flask après avoir copié les fichiers!
============================================================
"@

$instructions | Out-File -FilePath "$destination\INSTRUCTIONS.txt" -Encoding UTF8

Write-Host ""
Write-Host "✅ Dossier prêt: $destination" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Yellow
Write-Host "   1. Copiez le dossier FICHIERS_CORRIGES_SHERLOCK" -ForegroundColor White
Write-Host "   2. Mettez-le sur USB ou partagez via réseau" -ForegroundColor White
Write-Host "   3. Sur l'autre PC: Lisez INSTRUCTIONS.txt" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Ouvrir l'explorateur sur le dossier
Write-Host "Ouverture de l'explorateur..." -ForegroundColor Yellow
Start-Process explorer.exe -ArgumentList $destination

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
