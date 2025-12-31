@echo off
cls

echo ================================================================
echo     Organisation des scripts utilitaires
echo ================================================================
echo.
echo Ce script va ranger tous les scripts de diagnostic et
echo utilitaires dans un dossier separe pour desencombrer
echo le repertoire principal.
echo.
pause
echo.

cd /d D:\EOS

REM Creer le dossier scripts_utilitaires
if not exist "scripts_utilitaires" (
    mkdir scripts_utilitaires
    echo [OK] Dossier scripts_utilitaires cree
) else (
    echo [OK] Dossier scripts_utilitaires existe deja
)
echo.

REM Deplacer les scripts de diagnostic
echo Deplacement des scripts de diagnostic...
move /Y "DIAGNOSTIC_BASE_DONNEES.bat" "scripts_utilitaires\" 2>nul
move /Y "DIAGNOSTIC_BASE_DONNEES.sql" "scripts_utilitaires\" 2>nul
move /Y "CHECK_FRONTEND_ENV.bat" "scripts_utilitaires\" 2>nul
move /Y "CHECK_FRONTEND_SIMPLE.bat" "scripts_utilitaires\" 2>nul
move /Y "CORRIGER_COLONNES_TEXTE.bat" "scripts_utilitaires\" 2>nul
move /Y "CORRIGER_COLONNES_TEXTE.sql" "scripts_utilitaires\" 2>nul
move /Y "CORRIGER_PERMISSIONS.bat" "scripts_utilitaires\" 2>nul
move /Y "CORRIGER_PERMISSIONS.sql" "scripts_utilitaires\" 2>nul
move /Y "CORRIGER_PERMISSIONS_POSTGRES.bat" "scripts_utilitaires\" 2>nul

REM Deplacer les scripts de rebuild frontend
echo Deplacement des scripts frontend...
move /Y "REBUILD_FRONTEND.bat" "scripts_utilitaires\" 2>nul
move /Y "REBUILD_FRONTEND_ROBUSTE.bat" "scripts_utilitaires\" 2>nul
move /Y "REBUILD_FRONTEND_SIMPLE.bat" "scripts_utilitaires\" 2>nul

REM Deplacer les scripts de migration
echo Deplacement des scripts de migration...
move /Y "APPLIQUER_MIGRATIONS_SIMPLE.bat" "scripts_utilitaires\" 2>nul
move /Y "APPLIQUER_MIGRATIONS_PARTNER.bat" "scripts_utilitaires\" 2>nul
move /Y "verifier_migrations.py" "scripts_utilitaires\" 2>nul

REM Deplacer les scripts de configuration
echo Deplacement des scripts de configuration...
move /Y "CONFIGURER_PARTNER.bat" "scripts_utilitaires\" 2>nul
move /Y "CONFIGURER_PARTNER.sql" "scripts_utilitaires\" 2>nul
move /Y "CONFIGURER_TARIFS_PARTNER.bat" "scripts_utilitaires\" 2>nul
move /Y "INSERER_TARIFS_PARTNER.sql" "scripts_utilitaires\" 2>nul
move /Y "INSTALLER_BASE_DONNEES.bat" "scripts_utilitaires\" 2>nul

REM Deplacer les scripts de venv
echo Deplacement des scripts venv...
move /Y "RECREER_VENV.bat" "scripts_utilitaires\" 2>nul
move /Y "RECREER_VENV_SANS_CACHE.bat" "scripts_utilitaires\" 2>nul
move /Y "FORCER_INSTALLATION_DEPS.bat" "scripts_utilitaires\" 2>nul

REM Deplacer les scripts d'export/import
echo Deplacement des scripts export/import...
move /Y "EXPORTER_DONNEES_PARTNER.bat" "scripts_utilitaires\" 2>nul
move /Y "EXPORTER_DONNEES_PARTNER.sql" "scripts_utilitaires\" 2>nul
move /Y "IMPORTER_DONNEES_PARTNER.bat" "scripts_utilitaires\" 2>nul

REM Deplacer les guides et documentation
echo Deplacement de la documentation...
move /Y "GUIDE_*.md" "scripts_utilitaires\" 2>nul
move /Y "CORRECTIF_*.md" "scripts_utilitaires\" 2>nul
move /Y "INSTRUCTIONS_*.txt" "scripts_utilitaires\" 2>nul
move /Y "PROBLEME_RESOLU_LISEZMOI.md" "scripts_utilitaires\" 2>nul
move /Y "SYNCHRONISATION_GIT_TERMINEE.md" "scripts_utilitaires\" 2>nul
move /Y "CHECKLIST_INSTALLATION.md" "scripts_utilitaires\" 2>nul

REM Deplacer les rapports generes
echo Deplacement des rapports...
move /Y "RAPPORT_*.txt" "scripts_utilitaires\" 2>nul
move /Y "*_EXPORT.sql" "scripts_utilitaires\" 2>nul

REM Deplacer les archives de documentation
if exist "archives_documentation" (
    move /Y "archives_documentation" "scripts_utilitaires\" 2>nul
)

echo.
echo ================================================================
echo              Organisation terminee !
echo ================================================================
echo.
echo Tous les scripts utilitaires ont ete deplaces dans :
echo    scripts_utilitaires\
echo.
echo Scripts PRINCIPAUX restes dans le dossier racine :
echo    - DEMARRER_EOS_COMPLET.bat
echo    - DEMARRER_EOS_SIMPLE.bat
echo    - LISEZ-MOI.md
echo    - README.md
echo.
echo Pour acceder aux scripts utilitaires :
echo    cd scripts_utilitaires
echo.
pause

