@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Installation complète des améliorations PARTNER           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Définir DATABASE_URL
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
echo ✓ DATABASE_URL définie

REM Activer l'environnement virtuel
echo.
echo ► Activation de l'environnement virtuel...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR : Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo ✓ Environnement virtuel activé

REM Étape 1 : Ajouter la colonne instructions
echo.
echo ════════════════════════════════════════════════════════════════
echo   ÉTAPE 1/2 : Ajout de la colonne 'instructions'
echo ════════════════════════════════════════════════════════════════
python backend\ajouter_instructions_partner.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de l'ajout de la colonne
    pause
    exit /b 1
)

REM Étape 2 : Mettre à jour les mappings
echo.
echo ════════════════════════════════════════════════════════════════
echo   ÉTAPE 2/2 : Mise à jour des mappings d'import
echo ════════════════════════════════════════════════════════════════
python backend\scripts\add_instructions_mapping.py
if errorlevel 1 (
    echo.
    echo ❌ ERREUR lors de la mise à jour des mappings
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         ✅ Installation PARTNER terminée avec succès !         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Les améliorations suivantes ont été installées :
echo   ✓ Champ INSTRUCTIONS ajouté à la base de données
echo   ✓ Mapping INSTRUCTIONS ajouté au profil d'import PARTNER
echo   ✓ Affichage de RECHERCHE dans le header de mise à jour
echo   ✓ Affichage de INSTRUCTIONS en haut de la mise à jour
echo   ✓ Onglet Naissance pour PARTNER
echo   ✓ Suppression des validations bloquantes pour PARTNER
echo   ✓ Saisie libre des éléments retrouvés pour PARTNER
echo.
echo ⚠️  N'oubliez pas de redémarrer le frontend (npm run dev) pour voir les changements !
echo.
pause


