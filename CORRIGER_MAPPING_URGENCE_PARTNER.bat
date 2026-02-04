@echo off
echo ======================================================================
echo Correction du mapping URGENCE PARTNER
echo ======================================================================
echo.
echo PROBLEME : Le champ "urgence" est mappe a la colonne "PRENOM"
echo SOLUTION : Supprimer ce mapping incorrect
echo.
pause

set PGPASSWORD=elish26
psql -U postgres -d eos_db -f CORRIGER_MAPPING_URGENCE_PARTNER.sql

echo.
echo ======================================================================
echo Correction terminee !
echo ======================================================================
echo.
pause

