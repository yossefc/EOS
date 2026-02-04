@echo off
echo ======================================================================
echo Test - Tarification des Contestations
echo ======================================================================
echo.
echo Ce script affiche les facturations pour les contestations
echo pour verifier que les tarifs sont bien ajustes.
echo.
pause

set PGPASSWORD=elish26

echo.
echo === 1. Liste des contestations ===
psql -U postgres -d eos_db -c "SELECT d.id, d.\"numeroDossier\", LEFT(d.nom, 20) AS nom, d.est_contestation AS contest, d.enquete_originale_id AS orig_id, de.code_resultat AS code, c.code AS client FROM donnees d LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id LEFT JOIN clients c ON d.client_id = c.id WHERE d.est_contestation = TRUE ORDER BY d.id DESC LIMIT 5;"

echo.
echo === 2. Facturations pour la derniere contestation ===
echo.
psql -U postgres -d eos_db -c "WITH last_contest AS (SELECT id, enquete_originale_id FROM donnees WHERE est_contestation = TRUE ORDER BY id DESC LIMIT 1) SELECT d.id AS donnee_id, d.\"numeroDossier\", d.est_contestation AS contest, de.code_resultat AS code, ef.resultat_enqueteur_montant AS montant_enq, TO_CHAR(ef.created_at, 'YYYY-MM-DD HH24:MI') AS date FROM donnees d LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id LEFT JOIN enquete_facturation ef ON ef.donnee_enqueteur_id = de.id WHERE d.id IN (SELECT id FROM last_contest UNION SELECT enquete_originale_id FROM last_contest WHERE enquete_originale_id IS NOT NULL) ORDER BY d.id, ef.created_at;"

echo.
echo === 3. Total par enqueteur (Client PARTNER) ===
echo.
psql -U postgres -d eos_db -c "SELECT d.\"enqueteurId\", e.nom || ' ' || e.prenom AS enqueteur, COUNT(*) AS nb_facturations, SUM(ef.resultat_enqueteur_montant) AS total FROM enquete_facturation ef JOIN donnees_enqueteur de ON ef.donnee_enqueteur_id = de.id JOIN donnees d ON de.donnee_id = d.id LEFT JOIN enqueteurs e ON d.\"enqueteurId\" = e.id WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER') GROUP BY d.\"enqueteurId\", e.nom, e.prenom ORDER BY total DESC LIMIT 10;"

echo.
echo ======================================================================
echo Test termine !
echo ======================================================================
echo.
echo INTERPRETATION :
echo - Si vous voyez des montants NEGATIFS : C'est NORMAL pour les contestations negatives
echo - Si une enquete originale a 2 lignes (+15.40 et -15.40) : C'est CORRECT
echo - Le total par enqueteur doit refleter la somme algebrique de toutes les facturations
echo.
pause

