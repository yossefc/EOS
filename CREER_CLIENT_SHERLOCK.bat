@echo off
cls

echo ================================================================
echo     CREATION DU CLIENT SHERLOCK (Sans synchronisation)         
echo ================================================================
echo.
echo Ce script va creer le client Sherlock manuellement
echo dans votre base de donnees, sans avoir a synchroniser
echo depuis un autre ordinateur.
echo.
echo Le script va creer :
echo   - Le client RG_SHERLOCK
echo   - Le profil d'import EXCEL
echo   - Tous les mappings de colonnes (70+ mappings)
echo.
pause
echo.

cd /d D:\EOS

echo [INFO] Execution du script SQL...
echo.

psql -U postgres -d eos_db -f CREER_CLIENT_SHERLOCK.sql

if errorlevel 1 (
    echo.
    echo [ERREUR] Une erreur s'est produite lors de la creation du client.
    echo.
    echo Verifiez que :
    echo   1. PostgreSQL est demarre
    echo   2. La base de donnees eos_db existe
    echo   3. Vous avez les droits necessaires
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo         CLIENT SHERLOCK CREE AVEC SUCCES !           
echo ================================================================
echo.
echo Le client Sherlock est maintenant disponible.
echo.
echo PROCHAINE ETAPE :
echo ================
echo 1. Redemarrez l'application : DEMARRER_EOS_SIMPLE.bat
echo.
echo 2. Le client "RG Sherlock" devrait apparaitre dans la liste
echo.
echo 3. Vous pouvez importer des fichiers Excel Sherlock
echo.
pause
