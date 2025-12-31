@echo off
REM ============================================================================
REM Script d'installation et de configuration de la base de données EOS
REM ============================================================================
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║     Installation de la base de données EOS - PostgreSQL      ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Vérifier que PostgreSQL est installé
echo [1/5] Vérification de PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERREUR : PostgreSQL n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer PostgreSQL depuis : https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)
echo ✓ PostgreSQL trouvé

REM Vérifier que Python est installé
echo.
echo [2/5] Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERREUR : Python n'est pas installé ou pas dans le PATH
    echo.
    pause
    exit /b 1
)
echo ✓ Python trouvé

REM Demander les informations de connexion PostgreSQL
echo.
echo [3/5] Configuration de la connexion PostgreSQL
echo.
set /p POSTGRES_USER="Nom d'utilisateur PostgreSQL [postgres] : " || set POSTGRES_USER=postgres
set /p POSTGRES_PASS="Mot de passe PostgreSQL : "
set /p DB_NAME="Nom de la base de données [eos_db] : " || set DB_NAME=eos_db

REM Construire l'URL de connexion
set DATABASE_URL=postgresql+psycopg2://%POSTGRES_USER%:%POSTGRES_PASS%@localhost:5432/%DB_NAME%

echo.
echo URL de connexion : postgresql+psycopg2://%POSTGRES_USER%:***@localhost:5432/%DB_NAME%
echo.

REM Créer la base de données si elle n'existe pas
echo [4/5] Création de la base de données (si nécessaire)...
echo.

REM Vérifier si la base existe
psql -U %POSTGRES_USER% -lqt | findstr /C:"%DB_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Base de données '%DB_NAME%' n'existe pas, création...
    echo CREATE DATABASE %DB_NAME%; | psql -U %POSTGRES_USER%
    if errorlevel 1 (
        echo.
        echo ❌ ERREUR : Impossible de créer la base de données
        echo Vérifiez vos identifiants PostgreSQL
        echo.
        pause
        exit /b 1
    )
    echo ✓ Base de données '%DB_NAME%' créée
) else (
    echo ✓ Base de données '%DB_NAME%' existe déjà
)

REM Appliquer les migrations
echo.
echo [5/5] Application des migrations Alembic...
echo.

REM Définir DATABASE_URL pour ce processus
set DATABASE_URL=%DATABASE_URL%

REM Exécuter le script de migration
python backend/apply_migrations.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR : Les migrations ont échoué
    echo.
    echo Vérifiez les logs ci-dessus pour plus de détails
    echo.
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                  ✅ Installation terminée !                   ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Pour démarrer l'application, vous devez définir DATABASE_URL :
echo.
echo   PowerShell :
echo   $env:DATABASE_URL="%DATABASE_URL%"
echo.
echo   Git Bash :
echo   export DATABASE_URL="%DATABASE_URL%"
echo.
echo Puis lancez : python backend/app.py
echo.
echo Ou utilisez : DEMARRER_EOS_COMPLET.bat
echo.
pause

