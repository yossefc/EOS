-- ===================================================================
-- Script d'insertion des tarifs PARTNER par défaut
-- ===================================================================
-- Ce script insère les tarifs de base pour le client PARTNER
-- À adapter selon les tarifs réels fournis par le client
-- ===================================================================

\echo '╔═══════════════════════════════════════════════════════════╗'
\echo '║  Insertion des tarifs PARTNER par défaut                ║'
\echo '╚═══════════════════════════════════════════════════════════╝'
\echo ''

-- Vérifier que la table existe
\echo '[INFO] Vérification de la table tarifs_client...'
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'tarifs_client'
);

-- Vérifier l'existence du client PARTNER
\echo '[INFO] Vérification du client PARTNER...'
SELECT id, code, nom FROM clients WHERE code = 'PARTNER';

\echo ''
\echo '[1/2] Nettoyage des anciens tarifs PARTNER (si existants)...'
DELETE FROM tarifs_client 
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER');

\echo ''
\echo '[2/2] Insertion des nouveaux tarifs PARTNER...'

-- Insérer les tarifs PARTNER (à adapter selon vos besoins)
INSERT INTO tarifs_client (client_id, code_lettre, description, montant, date_debut, actif)
VALUES 
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'A', 'Tarif A - Base', 50.00, CURRENT_DATE, true),
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'B', 'Tarif B - Intermédiaire', 75.00, CURRENT_DATE, true),
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'C', 'Tarif C - Avancé', 100.00, CURRENT_DATE, true),
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'D', 'Tarif D - Décès', 120.00, CURRENT_DATE, true),
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'E', 'Tarif E - Employeur', 90.00, CURRENT_DATE, true),
    ((SELECT id FROM clients WHERE code = 'PARTNER'), 'T', 'Tarif T - Téléphone', 60.00, CURRENT_DATE, true);

\echo ''
\echo '[INFO] Tarifs insérés :'
SELECT 
    tc.code_lettre,
    tc.description,
    tc.montant || ' €' as montant,
    tc.actif
FROM tarifs_client tc
JOIN clients c ON tc.client_id = c.id
WHERE c.code = 'PARTNER'
ORDER BY tc.code_lettre;

\echo ''
\echo '╔═══════════════════════════════════════════════════════════╗'
\echo '║  ✅ Tarifs PARTNER insérés avec succès !                 ║'
\echo '╚═══════════════════════════════════════════════════════════╝'
\echo ''
\echo 'NOTE: Les montants ci-dessus sont des exemples.'
\echo 'Modifiez le fichier INSERER_TARIFS_PARTNER.sql selon vos tarifs réels.'
\echo ''

