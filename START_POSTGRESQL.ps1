# Script de démarrage EOS avec PostgreSQL
# Double-cliquer pour lancer l'application

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          APPLICATION EOS - PostgreSQL Mode              ║" -ForegroundColor Cyan
Write-Host "║                 (SQLite désactivé)                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ Configuration PostgreSQL" -ForegroundColor Green
Write-Host "  Base de données : eos_db@localhost:5432" -ForegroundColor Gray
Write-Host "  SQLite : Désactivé (PostgreSQL uniquement)" -ForegroundColor Yellow
Write-Host ""

Write-Host "🚀 Démarrage du serveur Flask..." -ForegroundColor Yellow
Write-Host ""

# Solution ultra-simple : aller à D:\EOS directement
cd D:\EOS\backend

# Lancer l'application
python start_with_postgresql.py

# Si l'application se ferme
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
