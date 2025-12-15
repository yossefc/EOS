@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║        Étape 2 - Configuration de PostgreSQL pour EOS        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM Paramètres (adapter au besoin)
REM ============================================================================
set "PGUSER=postgres"
set "PGHOST=localhost"
set "EOS_USER=eos_user"
set "EOS_PASSWORD=eos_password"
set "EOS_DB=eos_db"

echo PostgreSQL doit être installé et la commande ^"psql^" disponible dans le PATH.
echo Si un mot de passe est demandé, entrez celui du compte %PGUSER%.
echo.

REM Vérifier que psql est disponible
where psql >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR : La commande ^"psql^" n'a pas été trouvée.
    echo  - Vérifiez que PostgreSQL est installé.
    echo  - Exécutez d'abord: .\00_ajouter_postgresql_au_path.ps1
    echo  - Ou ajoutez manuellement le dossier ^"bin^" de PostgreSQL au PATH.
    echo.
    pause
    exit /b 1
)

REM 1) Créer l'utilisateur EOS (si nécessaire)
echo ► Création de l'utilisateur %EOS_USER% ...
psql -h %PGHOST% -U %PGUSER% -c "CREATE USER %EOS_USER% WITH PASSWORD '%EOS_PASSWORD%';" 2>nul
if errorlevel 1 (
    echo    ℹ️  L'utilisateur existe peut-être déjà, on continue.
) else (
    echo    ✅ Utilisateur %EOS_USER% créé.
)
echo.

REM 2) Créer la base EOS (si nécessaire)
echo ► Création de la base %EOS_DB% ...
psql -h %PGHOST% -U %PGUSER% -c "CREATE DATABASE %EOS_DB% OWNER %EOS_USER%;" 2>nul
if errorlevel 1 (
    echo    ℹ️  La base existe peut-être déjà, on continue.
) else (
    echo    ✅ Base %EOS_DB% créée.
)
echo.

REM 3) Donner les privilèges
echo ► Attribution des privilèges ...
psql -h %PGHOST% -U %PGUSER% -d %EOS_DB% -c "GRANT ALL PRIVILEGES ON DATABASE %EOS_DB% TO %EOS_USER%;" 1>nul
psql -h %PGHOST% -U %PGUSER% -d %EOS_DB% -c "GRANT ALL ON SCHEMA public TO %EOS_USER%;" 1>nul
echo    ✅ Droits accordés à %EOS_USER% sur %EOS_DB%.
echo.

echo ╔════════════════════════════════════════════════════════════════╗
echo ║   ✅ Étape 2 terminée : PostgreSQL est configuré pour EOS     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo  Détails :
echo    - Utilisateur : %EOS_USER%
echo    - Base       : %EOS_DB%
echo.
pause



