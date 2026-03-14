@echo off
REM Script ultra-simple qui ne peut PAS se fermer
cls

echo.
echo ================================================================
echo    DIAGNOSTIC FRONTEND ULTRA-SIMPLE
echo ================================================================
echo.
echo Ce script va verifier votre environnement etape par etape.
echo Il ne se fermera JAMAIS automatiquement.
echo.
pause
echo.

REM ============================================================
REM ETAPE 1 : Ou sommes-nous ?
REM ============================================================
echo [ETAPE 1/5] Repertoire actuel
echo.
cd
echo.
pause
echo.

REM ============================================================
REM ETAPE 2 : Le dossier frontend existe-t-il ?
REM ============================================================
echo [ETAPE 2/5] Verification du dossier frontend
echo.

if exist frontend (
    echo [OK] Le dossier frontend existe !
    echo.
    dir frontend /w
) else (
    echo [ERREUR] Le dossier frontend N'EXISTE PAS !
    echo.
    echo Contenu du repertoire actuel :
    echo.
    dir /w
    echo.
    echo VOUS ETES DANS LE MAUVAIS REPERTOIRE !
    echo.
    echo Faites : cd /d D:\EOS
    echo Ou : cd /d/eos
)
echo.
pause
echo.

REM ============================================================
REM ETAPE 3 : Node.js est-il installe ?
REM ============================================================
echo [ETAPE 3/5] Verification de Node.js
echo.

where node
if errorlevel 1 (
    echo.
    echo [ERREUR] Node.js N'EST PAS INSTALLE !
    echo.
    echo Telechargez-le depuis : https://nodejs.org/
    echo Choisissez la version LTS.
    echo.
) else (
    echo.
    node --version
    echo [OK] Node.js est installe
)
echo.
pause
echo.

REM ============================================================
REM ETAPE 4 : npm est-il installe ?
REM ============================================================
echo [ETAPE 4/5] Verification de npm
echo.

where npm
if errorlevel 1 (
    echo.
    echo [ERREUR] npm N'EST PAS INSTALLE !
    echo npm est normalement installe avec Node.js
    echo.
) else (
    echo.
    npm --version
    echo [OK] npm est installe
)
echo.
pause
echo.

REM ============================================================
REM ETAPE 5 : package.json existe-t-il ?
REM ============================================================
echo [ETAPE 5/5] Verification de package.json
echo.

if exist frontend\package.json (
    echo [OK] frontend\package.json existe
    echo.
    echo Contenu du dossier frontend/src :
    if exist frontend\src (
        dir frontend\src /w
    ) else (
        echo [WARNING] frontend\src n'existe pas !
    )
) else (
    echo [ERREUR] frontend\package.json N'EXISTE PAS !
)
echo.
pause
echo.

REM ============================================================
REM RESUME
REM ============================================================
echo ================================================================
echo                         RESUME
echo ================================================================
echo.

if exist frontend (
    echo [1] Dossier frontend : OK
) else (
    echo [1] Dossier frontend : MANQUANT !!!
)

where node >nul 2>&1
if errorlevel 1 (
    echo [2] Node.js : MANQUANT !!!
) else (
    echo [2] Node.js : OK
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [3] npm : MANQUANT !!!
) else (
    echo [3] npm : OK
)

if exist frontend\package.json (
    echo [4] package.json : OK
) else (
    echo [4] package.json : MANQUANT !!!
)

echo.
echo ================================================================
echo.

if exist frontend (
    where node >nul 2>&1
    if not errorlevel 1 (
        where npm >nul 2>&1
        if not errorlevel 1 (
            if exist frontend\package.json (
                echo TOUT EST OK ! Vous pouvez builder le frontend.
                echo.
                echo Utilisez : REBUILD_FRONTEND_SIMPLE.bat
                goto :fin_ok
            )
        )
    )
)

echo IL Y A DES PROBLEMES !
echo Regardez les erreurs ci-dessus.
echo.

:fin_ok
pause

