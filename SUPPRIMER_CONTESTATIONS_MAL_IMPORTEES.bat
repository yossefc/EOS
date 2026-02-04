@echo off
echo ======================================================================
echo Suppression des contestations mal importees
echo ======================================================================
echo.
echo ATTENTION : Ce script va supprimer les contestations avec prenom = URGENT
echo.
pause

set PGPASSWORD=elish26
psql -U postgres -d eos_db -f SUPPRIMER_CONTESTATIONS_MAL_IMPORTEES.sql

pause

