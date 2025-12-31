@echo off
cls

echo ================================================================
echo        Appliquer les migrations manquantes (PARTNER)         
echo ================================================================
echo.
echo Ce script va ajouter les colonnes PARTNER manquantes a la table donnees
echo.
echo Colonnes ajoutees :
echo   - tarif_lettre (code lettre du tarif)
echo   - recherche (texte de recherche PARTNER)
echo   - instructions (instructions particulieres)
echo   - date_jour (date du jour)
echo   - nom_complet (nom complet formate)
echo   - motif (motif de la demande)
echo.
pause
echo.

cd /d D:\EOS

echo [1/2] Verification de la connexion PostgreSQL...
echo.

REM Definir DATABASE_URL (a adapter selon votre configuration)
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db

echo DATABASE_URL defini : %DATABASE_URL%
echo.

echo [2/2] Application des migrations...
echo.

python backend/apply_migrations.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'application des migrations
    echo.
    echo Verifiez que :
    echo   1. PostgreSQL est demarre
    echo   2. Le mot de passe dans DATABASE_URL est correct
    echo   3. La base de donnees eos_db existe
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              Migrations appliquees avec succes !           
echo ================================================================
echo.
echo Les colonnes PARTNER ont ete ajoutees a la table donnees.
echo Vous pouvez maintenant redemarrer l'application.
echo.
pause

