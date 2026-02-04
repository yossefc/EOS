@echo off
echo ======================================================================
echo Verification des contestations PARTNER
echo ======================================================================
echo.

set PGPASSWORD=elish26
psql -U postgres -d eos_db -f VERIFIER_CONTESTATIONS_PARTNER.sql

pause

