@echo off
echo Correction des permissions PostgreSQL pour les tables PARTNER...
echo.

psql -U postgres -d eos_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;"
psql -U postgres -d eos_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;"

echo.
echo [OK] Permissions accordees !
echo.
pause