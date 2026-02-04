-- ================================================================
-- Script de configuration automatique du client PARTNER
-- À exécuter sur le nouvel ordinateur
-- ================================================================

-- 1. Créer le client PARTNER (s'il n'existe pas)
INSERT INTO clients (id, code, nom, actif, date_creation)
VALUES (11, 'PARTNER', 'PARTNER', true, NOW())
ON CONFLICT (id) DO UPDATE SET
  code = EXCLUDED.code,
  nom = EXCLUDED.nom,
  actif = EXCLUDED.actif;

-- 2. Créer le profil d'import PARTNER Excel
INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
VALUES (11, 'PARTNER Excel Format (EXCEL)', 'EXCEL', 'utf-8', true, NOW())
ON CONFLICT DO NOTHING;

-- 3. Récupérer l'ID du profil PARTNER (pour les mappings)
DO $$
DECLARE
    partner_profile_id INT;
BEGIN
    -- Récupérer l'ID du profil PARTNER
    SELECT id INTO partner_profile_id FROM import_profiles WHERE client_id = 11 AND file_type = 'EXCEL' LIMIT 1;
    
    -- Supprimer les anciens mappings pour ce profil (pour éviter les doublons)
    DELETE FROM import_field_mappings WHERE import_profile_id = partner_profile_id;
    
    -- Créer tous les mappings de colonnes pour PARTNER
    INSERT INTO import_field_mappings (import_profile_id, internal_field, column_name, strip_whitespace, is_required, date_creation)
    VALUES
        -- Champs obligatoires
        (partner_profile_id, 'numeroDossier', 'NUM', true, true, NOW()),
        (partner_profile_id, 'nom', 'NOM', true, true, NOW()),
        
        -- Champs optionnels
        (partner_profile_id, 'prenom', 'PRENOM', true, false, NOW()),
        (partner_profile_id, 'dateNaissance', 'JOUR', true, false, NOW()),
        (partner_profile_id, 'dateNaissance_annee', 'ANNEE NAISSANCE', true, false, NOW()),
        (partner_profile_id, 'dateNaissance_mois', 'MOIS', true, false, NOW()),
        (partner_profile_id, 'lieuNaissance', 'LIEUNAISSANCE', true, false, NOW()),
        (partner_profile_id, 'nomPatronymique', 'NJF', true, false, NOW()),
        (partner_profile_id, 'adresse1', 'ADRESSE', true, false, NOW()),
        (partner_profile_id, 'ville', 'VILLE', true, false, NOW()),
        (partner_profile_id, 'codePostal', 'CP', true, false, NOW()),
        (partner_profile_id, 'telephonePersonnel', 'TEL', true, false, NOW()),
        (partner_profile_id, 'datedenvoie', 'DATE ENVOI', true, false, NOW()),
        (partner_profile_id, 'date_butoir', 'DATE BUTOIR', true, false, NOW()),
        (partner_profile_id, 'date_jour', 'DATE DU JOUR', true, false, NOW()),
        (partner_profile_id, 'recherche', 'RECHERCHE', true, false, NOW()),
        (partner_profile_id, 'instructions', 'INSTRUCTIONS', true, false, NOW()),
        (partner_profile_id, 'motif', 'MOTIF', true, false, NOW()),
        (partner_profile_id, 'tarif_lettre', 'TARIF', true, false, NOW()),
        (partner_profile_id, 'nom_complet', 'NOM', true, false, NOW()),
        -- Mapping pour les contestations
        (partner_profile_id, 'numeroDemandeContestee', 'NUM CONTESTE', true, false, NOW()),
        (partner_profile_id, 'numeroDemandeContestee', 'NUMERO CONTESTE', true, false, NOW()),
        (partner_profile_id, 'numeroDemandeContestee', 'NUM ENQUETE CONTESTEE', true, false, NOW()),
        (partner_profile_id, 'numeroDemandeContestee', 'NUM CONTESTEE', true, false, NOW());
    
    RAISE NOTICE 'Configuration PARTNER terminée ! Profil ID: %', partner_profile_id;
END $$;

-- 4. Vérification
SELECT 
    c.code AS client_code,
    c.nom AS client_nom,
    ip.id AS profile_id,
    ip.name AS profile_name,
    COUNT(ifm.id) AS nb_mappings
FROM clients c
JOIN import_profiles ip ON ip.client_id = c.id
LEFT JOIN import_field_mappings ifm ON ifm.import_profile_id = ip.id
WHERE c.code = 'PARTNER'
GROUP BY c.code, c.nom, ip.id, ip.name;

-- Afficher les mappings créés
SELECT 
    internal_field,
    column_name,
    is_required
FROM import_field_mappings
WHERE import_profile_id = (SELECT id FROM import_profiles WHERE client_id = 11 AND file_type = 'EXCEL' LIMIT 1)
ORDER BY internal_field;

-- ================================================================
-- Fin du script
-- ================================================================

