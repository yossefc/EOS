@echo off
:: Vérifie si le script est exécuté en tant qu'administrateur
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Déjà en mode administrateur, exécution du script...
    call open_firewall.bat
) else (
    echo Demande des privilèges administrateur...
    powershell -Command "Start-Process -FilePath '%~dp0open_firewall.bat' -Verb RunAs"
)
