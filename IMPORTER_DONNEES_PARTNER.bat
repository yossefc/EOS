@echo off
cls

echo ================================================================
echo     IMPORT DES DONNEES PARTNER (Ordinateur CIBLE)         
echo ================================================================
echo.
echo Ce script va importer toutes les donnees PARTNER depuis
echo les fichiers exportes de l'autre ordinateur.
echo.
echo PREREQUIS :
echo   Les 3 fichiers SQL doivent etre dans ce dossier :
echo   - PARTNER_TARIFS_EXPORT.sql
echo   - PARTNER_CONFIRMATION_EXPORT.sql
echo   - PARTNER_TARIF_RULES_EXPORT.sql
echo.
pause
echo.

cd /d D:\EOS

REM Verifier que les fichiers existent
if not exist "PARTNER_TARIFS_EXPORT.sql" (
    echo [ERREUR] Fichier PARTNER_TARIFS_EXPORT.sql introuvable !
    echo.
    echo Copiez d'abord les fichiers SQL depuis l'autre ordinateur.
    echo.
    pause
    exit /b 1
)

if not exist "PARTNER_CONFIRMATION_EXPORT.sql" (
    echo [ERREUR] Fichier PARTNER_CONFIRMATION_EXPORT.sql introuvable !
    pause
    exit /b 1
)

if not exist "PARTNER_TARIF_RULES_EXPORT.sql" (
    echo [ERREUR] Fichier PARTNER_TARIF_RULES_EXPORT.sql introuvable !
    pause
    exit /b 1
)

echo [OK] Tous les fichiers SQL sont presents
echo.

echo [1/3] Import des tarifs PARTNER...
echo.
psql -U postgres -d eos_db -f PARTNER_TARIFS_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des tarifs
    pause
    exit /b 1
)

echo [OK] Tarifs importes
echo.

echo [2/3] Import des options de confirmation...
echo.
psql -U postgres -d eos_db -f PARTNER_CONFIRMATION_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des options
    pause
    exit /b 1
)

echo [OK] Options importees
echo.

echo [3/3] Import des regles tarifaires...
echo.
psql -U postgres -d eos_db -f PARTNER_TARIF_RULES_EXPORT.sql

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'import des regles
    pause
    exit /b 1
)

echo [OK] Regles importees
echo.

echo.
echo ================================================================
echo         IMPORT TERMINE AVEC SUCCES !           
echo ================================================================
echo.
echo Toutes les donnees PARTNER ont ete importees :
echo   - Tarifs
echo   - Options de confirmation
echo   - Regles tarifaires
echo.
echo Vous pouvez maintenant redemarrer l'application.
echo.
pause

