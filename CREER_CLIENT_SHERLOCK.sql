-- ===================================================================
-- CRÉATION MANUELLE DU CLIENT SHERLOCK (RG_SHERLOCK)
-- ===================================================================
-- Ce script crée le client Sherlock avec tous ses mappings
-- Sans avoir à synchroniser depuis un autre ordinateur
-- ===================================================================

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  CRÉATION DU CLIENT SHERLOCK                              ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''

-- ===================================================================
-- 1. CRÉER LE CLIENT
-- ===================================================================

\echo '[1/3] Création du client Sherlock...'
\echo ''

INSERT INTO clients (code, nom, actif, date_creation)
VALUES ('RG_SHERLOCK', 'RG Sherlock', true, NOW())
ON CONFLICT (code) DO UPDATE SET
  nom = EXCLUDED.nom,
  actif = EXCLUDED.actif;

\echo '✅ Client Sherlock créé/mis à jour'
\echo ''

-- ===================================================================
-- 2. CRÉER LE PROFIL D'IMPORT
-- ===================================================================

\echo '[2/3] Création du profil d''import...'
\echo ''

DO $$
DECLARE
    client_id_val INT;
    profile_id_val INT;
BEGIN
    -- Récupérer l'ID du client
    SELECT id INTO client_id_val FROM clients WHERE code = 'RG_SHERLOCK';
    
    -- Créer le profil d'import
    INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
    VALUES (client_id_val, 'Sherlock Import Standard', 'EXCEL', 'utf-8', true, NOW())
    ON CONFLICT DO NOTHING;
    
    -- Désactiver l'ancien profil EXCEL_VERTICAL s'il existe
    UPDATE import_profiles 
    SET actif = false 
    WHERE client_id = client_id_val AND file_type = 'EXCEL_VERTICAL';
    
    RAISE NOTICE '✅ Profil d''import créé';
END $$;

\echo ''

-- ===================================================================
-- 3. CRÉER LES MAPPINGS DE COLONNES
-- ===================================================================

\echo '[3/3] Création des mappings de colonnes...'
\echo ''

DO $$
DECLARE
    profile_id_val INT;
BEGIN
    -- Récupérer l'ID du profil
    SELECT ip.id INTO profile_id_val 
    FROM import_profiles ip
    JOIN clients c ON ip.client_id = c.id
    WHERE c.code = 'RG_SHERLOCK' AND ip.file_type = 'EXCEL'
    LIMIT 1;
    
    -- Supprimer les anciens mappings
    DELETE FROM import_field_mappings WHERE import_profile_id = profile_id_val;
    
    -- Créer tous les mappings
    INSERT INTO import_field_mappings (import_profile_id, column_name, internal_field, is_required, strip_whitespace, date_creation)
    VALUES
        -- Champ obligatoire
        (profile_id_val, 'DossierId', 'dossier_id', true, true, NOW()),
        
        -- Informations de base
        (profile_id_val, 'RéférenceInterne', 'reference_interne', false, true, NOW()),
        (profile_id_val, 'Demande', 'demande', false, true, NOW()),
        
        -- État civil
        (profile_id_val, 'EC-Civilité', 'ec_civilite', false, true, NOW()),
        (profile_id_val, 'EC-Prénom', 'ec_prenom', false, true, NOW()),
        (profile_id_val, 'EC-Prénom2', 'ec_prenom2', false, true, NOW()),
        (profile_id_val, 'EC-Prénom3', 'ec_prenom3', false, true, NOW()),
        (profile_id_val, 'EC-Prénom4', 'ec_prenom4', false, true, NOW()),
        (profile_id_val, 'EC-Nom Usage', 'ec_nom_usage', false, true, NOW()),
        (profile_id_val, 'EC-Nom Naissance', 'ec_nom_naissance', false, true, NOW()),
        (profile_id_val, 'EC-Date Naissance', 'ec_date_naissance', false, true, NOW()),
        (profile_id_val, 'Naissance CP', 'naissance_cp', false, true, NOW()),
        (profile_id_val, 'EC-Localité Naissance', 'ec_localite_naissance', false, true, NOW()),
        (profile_id_val, 'Naissance INSEE', 'naissance_insee', false, true, NOW()),
        (profile_id_val, 'EC-Pays Naissance', 'ec_pays_naissance', false, true, NOW()),
        
        -- Commentaire
        (profile_id_val, 'Client-Commentaire', 'client_commentaire', false, true, NOW()),
        
        -- Adresse
        (profile_id_val, 'AD-L1', 'ad_l1', false, true, NOW()),
        (profile_id_val, 'AD-L2', 'ad_l2', false, true, NOW()),
        (profile_id_val, 'AD-L3', 'ad_l3', false, true, NOW()),
        (profile_id_val, 'AD-L4 Numéro', 'ad_l4_numero', false, true, NOW()),
        (profile_id_val, 'AD-L4 Type', 'ad_l4_type', false, true, NOW()),
        (profile_id_val, 'AD-L4 Voie', 'ad_l4_voie', false, true, NOW()),
        (profile_id_val, 'AD-L5', 'ad_l5', false, true, NOW()),
        (profile_id_val, 'AD-L6 Cedex', 'ad_l6_cedex', false, true, NOW()),
        (profile_id_val, 'AD-L6 CP', 'ad_l6_cp', false, true, NOW()),
        (profile_id_val, 'AD-L6 INSEE', 'ad_l6_insee', false, true, NOW()),
        (profile_id_val, 'AD-L6 Localité', 'ad_l6_localite', false, true, NOW()),
        (profile_id_val, 'AD-L7 Pays', 'ad_l7_pays', false, true, NOW()),
        (profile_id_val, 'AD-Téléphone', 'ad_telephone', false, true, NOW()),
        (profile_id_val, 'AD-TéléphonePro', 'ad_telephone_pro', false, true, NOW()),
        (profile_id_val, 'AD-TéléphoneMobile', 'ad_telephone_mobile', false, true, NOW()),
        (profile_id_val, 'AD-Email', 'ad_email', false, true, NOW()),
        
        -- Tarifs
        (profile_id_val, 'Tarif A', 'tarif_a', false, true, NOW()),
        (profile_id_val, 'Tarif AT', 'tarif_at', false, true, NOW()),
        (profile_id_val, 'Tarif DCD', 'tarif_dcd', false, true, NOW()),
        
        -- Résultats
        (profile_id_val, 'Résultat', 'resultat', false, true, NOW()),
        (profile_id_val, 'Montant HT', 'montant_ht', false, true, NOW()),
        
        -- Réponses État civil
        (profile_id_val, 'Rép-EC-Civilité', 'rep_ec_civilite', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Prénom', 'rep_ec_prenom', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Prénom2', 'rep_ec_prenom2', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Prénom3', 'rep_ec_prenom3', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Prénom4', 'rep_ec_prenom4', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Nom Usage', 'rep_ec_nom_usage', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Nom Naissance', 'rep_ec_nom_naissance', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Date Naissance', 'rep_ec_date_naissance', false, true, NOW()),
        (profile_id_val, 'Rép-Naissance CP', 'rep_naissance_cp', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Localité Naissance', 'rep_ec_localite_naissance', false, true, NOW()),
        (profile_id_val, 'Rép-Naissance INSEE', 'rep_naissance_insee', false, true, NOW()),
        (profile_id_val, 'Rép-EC-Pays Naissance', 'rep_ec_pays_naissance', false, true, NOW()),
        
        -- Réponses Décès
        (profile_id_val, 'Rép-DCD-Date', 'rep_dcd_date', false, true, NOW()),
        (profile_id_val, 'Rép-DCD-Numéro_Acte', 'rep_dcd_numero_acte', false, true, NOW()),
        (profile_id_val, 'Rép-DCD-Localité', 'rep_dcd_localite', false, true, NOW()),
        (profile_id_val, 'Rép-DCD-CP', 'rep_dcd_cp', false, true, NOW()),
        (profile_id_val, 'Rép-DCD-INSEE', 'rep_dcd_insee', false, true, NOW()),
        (profile_id_val, 'Rép-DCD-Pays', 'rep_dcd_pays', false, true, NOW()),
        
        -- Réponses Adresse
        (profile_id_val, 'Rép-AD-L1', 'rep_ad_l1', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L2', 'rep_ad_l2', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L3', 'rep_ad_l3', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L4 Numéro', 'rep_ad_l4_numero', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L4 Type', 'rep_ad_l4_type', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L4 Voie', 'rep_ad_l4_voie', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L5', 'rep_ad_l5', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L6 Cedex', 'rep_ad_l6_cedex', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L6 CP', 'rep_ad_l6_cp', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L6 INSEE', 'rep_ad_l6_insee', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L6 Localité', 'rep_ad_l6_localite', false, true, NOW()),
        (profile_id_val, 'Rép-AD-L7 Pays', 'rep_ad_l7_pays', false, true, NOW()),
        (profile_id_val, 'Rép-AD-Téléphone', 'rep_ad_telephone', false, true, NOW());
    
    RAISE NOTICE '✅ % mappings créés', (SELECT COUNT(*) FROM import_field_mappings WHERE import_profile_id = profile_id_val);
END $$;

\echo ''

-- ===================================================================
-- 4. VÉRIFICATION
-- ===================================================================

\echo '════════════════════════════════════════════════════════════'
\echo '   VÉRIFICATION                                             '
\echo '════════════════════════════════════════════════════════════'
\echo ''

\echo 'Client créé :'
SELECT id, code, nom, actif FROM clients WHERE code = 'RG_SHERLOCK';

\echo ''
\echo 'Profil d''import :'
SELECT ip.id, ip.name, ip.file_type, ip.actif
FROM import_profiles ip
JOIN clients c ON ip.client_id = c.id
WHERE c.code = 'RG_SHERLOCK';

\echo ''
\echo 'Nombre de mappings :'
SELECT COUNT(*) AS nb_mappings
FROM import_field_mappings ifm
JOIN import_profiles ip ON ifm.import_profile_id = ip.id
JOIN clients c ON ip.client_id = c.id
WHERE c.code = 'RG_SHERLOCK';

\echo ''
\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  ✅ CLIENT SHERLOCK CRÉÉ AVEC SUCCÈS !                    ║'
\echo '╚════════════════════════════════════════════════════════════╝'
\echo ''
\echo 'Le client Sherlock est maintenant disponible dans l''application.'
\echo 'Redémarrez l''application pour voir les changements.'
\echo ''
