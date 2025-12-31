@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        Appliquer les migrations manquantes (PARTNER)         ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Ce script va ajouter les colonnes PARTNER manquantes à la table donnees
echo.
echo Colonnes ajoutées :
echo   - tarif_lettre (code lettre du tarif)
echo   - recherche (texte de recherche PARTNER)
echo   - instructions (instructions particulières)
echo   - date_jour (date du jour)
echo   - nom_complet (nom complet formaté)
echo   - motif (motif de la demande)
echo.
pause
echo.

cd /d D:\EOS

echo [1/2] Vérification de la connexion PostgreSQL...
echo.

REM Définir DATABASE_URL (à adapter selon votre configuration)
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db

echo DATABASE_URL défini : %DATABASE_URL%
echo.

echo [2/2] Application des migrations...
echo.

python backend/apply_migrations.py

if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de l'application des migrations
    echo.
    echo Vérifiez que :
    echo   1. PostgreSQL est démarré
    echo   2. Le mot de passe dans DATABASE_URL est correct
    echo   3. La base de données eos_db existe
    echo.
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║              ✅ Migrations appliquées avec succès !           ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Les colonnes PARTNER ont été ajoutées à la table donnees.
echo Vous pouvez maintenant redémarrer l'application.
echo.
pause

