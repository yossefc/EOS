@echo off
echo Configuration du pare-feu Windows pour EOS System...

:: Ajouter la règle pour le port 5000 (Backend)
netsh advfirewall firewall add rule name="EOS Backend (5000)" dir=in action=allow protocol=TCP localport=5000

:: Ajouter la règle pour le port 5173 (Frontend)
netsh advfirewall firewall add rule name="EOS Frontend (5173)" dir=in action=allow protocol=TCP localport=5173

echo.
echo Configuration du pare-feu terminée !
echo Les ports 5000 (Backend) et 5173 (Frontend) sont maintenant ouverts.
echo.
pause
