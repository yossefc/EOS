@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              🎉  BIENVENUE DANS EOS  🎉                        ║
echo ║                                                                ║
echo ║        Système de Gestion d'Enquêtes                          ║
echo ║        Flask + React + PostgreSQL                             ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │  📖  PREMIÈRE FOIS ?                                           │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo   Ouvre le fichier :  📘 LISEZ-MOI.md
echo.
echo   Il contient tout :
echo     • Installation pas à pas
echo     • Démarrage de l'application
echo     • Solutions aux problèmes courants
echo.
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │  🚀  DÉJÀ INSTALLÉ ?                                           │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo   1. Lance le backend :
echo      👉 Double-clique sur : DEMARRER_EOS_POSTGRESQL.bat
echo.
echo   2. Dans un autre terminal, lance le frontend :
echo      cd frontend
echo      npm run dev
echo.
echo   3. Ouvre ton navigateur :
echo      http://localhost:5173
echo.
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │  🔧  UN PROBLÈME ?                                             │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo   • Import ne marche pas ?
echo     → CORRIGER_BDD.bat
echo     → REINITIALISER_MAPPINGS.bat
echo.
echo   • PostgreSQL non trouvé ?
echo     → 00_ajouter_postgresql_au_path.ps1
echo.
echo   • Backend ne démarre pas ?
echo     → Vérifie que PostgreSQL est lancé
echo     → Utilise DEMARRER_EOS_POSTGRESQL.bat
echo.
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │  📂  FICHIERS IMPORTANTS                                       │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo   📘 LISEZ-MOI.md                   ← ⭐ GUIDE COMPLET
echo   📋 TRANSFERT_AUTRE_ORDINATEUR.txt ← Checklist transfert
echo   📊 STRUCTURE_PROJET.txt           ← Organisation
echo.
echo   🔧 Scripts d'installation :
echo      00_ajouter_postgresql_au_path.ps1
echo      01_configurer_postgresql.bat
echo      02_installer_backend.bat
echo      03_installer_frontend.bat
echo.
echo   ▶️ Script de démarrage :
echo      DEMARRER_EOS_POSTGRESQL.bat
echo.
echo   🛠️ Scripts de dépannage :
echo      CORRIGER_BDD.bat
echo      REINITIALISER_MAPPINGS.bat
echo.
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║   📖  Pour commencer, ouvre :  LISEZ-MOI.md                    ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause


