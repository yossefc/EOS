@echo off
echo Testing EOS System...

:: Test du backend
echo Testing Backend...
curl -s http://192.168.150.107:5000/enqueteurs
if %errorlevel% equ 0 (
    echo Backend OK
) else (
    echo Backend not responding
)

:: Test du frontend
echo.
echo Testing Frontend...
curl -s http://192.168.150.107:5173
if %errorlevel% equ 0 (
    echo Frontend OK
) else (
    echo Frontend not responding
)

:: Test de la connexion VPN
echo.
echo Testing VPN Connection...
ping -n 1 192.168.150.107
if %errorlevel% equ 0 (
    echo VPN Connection OK
) else (
    echo VPN Connection Failed
)

echo.
echo Test completed!
pause
