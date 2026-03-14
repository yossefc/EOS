@echo off
cls

echo ================================================================
echo     Creation de la table tarifs_client et insertion tarifs   
echo ================================================================
echo.
echo Ce script va :
echo   1. Appliquer la migration 008 (creation table tarifs_client)
echo   2. Inserer les tarifs PARTNER par defaut
echo.
pause
echo.

cd /d D:\EOS

echo [1/2] Application de la migration 008...
echo.

set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db

python backend/apply_migrations.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'application de la migration
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Insertion des tarifs PARTNER par defaut...
echo.

psql -U postgres -d eos_db -f INSERER_TARIFS_PARTNER.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors de l'insertion des tarifs
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo          Configuration tarifaire terminee !           
echo ================================================================
echo.
echo La table tarifs_client a ete creee avec les tarifs PARTNER.
echo.
echo IMPORTANT: Verifiez et ajustez les montants selon vos tarifs reels
echo            dans le fichier INSERER_TARIFS_PARTNER.sql
echo.
echo Vous pouvez maintenant redemarrer l'application.
echo.
pause

