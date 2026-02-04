@echo off
echo ======================================================================
echo Verification des mappings PARTNER
echo ======================================================================
echo.

set PGPASSWORD=elish26
psql -U postgres -d eos_db -f VERIFIER_MAPPINGS_PARTNER.sql

pause

