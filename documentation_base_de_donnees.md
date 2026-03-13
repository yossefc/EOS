# Documentation base de donnees EOS

Genere le 2026-03-13 07:26:39 a partir du schema PostgreSQL courant.

## Resume

- Nombre de tables documentees : 21
- Nombre total de champs documentes : 351
- Fichier tabulaire associe : `documentation_base_de_donnees.csv`

## Tables

| Table | Description | Nb champs |
| --- | --- | ---: |
| `alembic_version` | Table technique qui memorise la version de migration appliquee. | 1 |
| `clients` | Referentiel des clients de l'application EOS. | 6 |
| `confirmation_options` | Options de confirmation personnalisees proposees par client. | 6 |
| `donnees` | Table centrale des dossiers/enquetes importes depuis les fichiers source. | 70 |
| `donnees_enqueteur` | Reponses, corrections et informations terrain saisies par les enqueteurs. | 75 |
| `enquete_archive_files` | Fichiers physiques d'archives/export lies a une enquete. | 9 |
| `enquete_archives` | Historique logique des exportations d'enquetes. | 5 |
| `enquete_facturation` | Montants de facturation client et de remuneration enqueteur par enquete. | 15 |
| `enquetes_terminees` | Trace des enquetes confirmees/terminees. | 4 |
| `enqueteurs` | Referentiel des enqueteurs utilisateurs du systeme. | 7 |
| `export_batches` | Historique des exports groupes contenant plusieurs enquetes. | 9 |
| `fichiers` | Fichiers sources importes dans l'application. | 5 |
| `import_field_mappings` | Regles de mapping entre colonnes source et champs internes EOS. | 11 |
| `import_profiles` | Profils de parametrage d'import par client et type de fichier. | 9 |
| `partner_case_requests` | Demandes normalisees detectees par dossier pour le mode PARTNER. | 9 |
| `partner_request_keywords` | Mots-cles servant a detecter les demandes PARTNER dans le champ RECHERCHE. | 8 |
| `partner_tarif_rules` | Regles tarifaires PARTNER selon la lettre et la combinaison de demandes. | 7 |
| `sherlock_donnees` | Donnees importees depuis le format Sherlock, avec source et reponse enqueteur. | 71 |
| `tarifs_client` | Tarifs specifiques definis pour chaque client. | 8 |
| `tarifs_enqueteur` | Tarifs de remuneration des enqueteurs. | 9 |
| `tarifs_eos` | Tarifs factures par EOS au client final. | 7 |

## alembic_version

Table technique qui memorise la version de migration appliquee.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `version_num` | `VARCHAR(32)` | 32 | PK / NOT NULL | Identifiant de revision Alembic appliquee. |

## clients

Referentiel des clients de l'application EOS.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('clients_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `code` | `VARCHAR(50)` | 50 | NOT NULL / UNIQUE / INDEX | Code unique du client dans EOS. |
| `nom` | `VARCHAR(255)` | 255 | NOT NULL | Nom commercial ou metier du client. |
| `actif` | `BOOLEAN` | - | NOT NULL | Indique si l'element est actif. |
| `date_creation` | `TIMESTAMP` | - | NOT NULL | Date et heure de creation de la ligne. |
| `date_modification` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere modification. |

## confirmation_options

Options de confirmation personnalisees proposees par client.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('confirmation_options_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / UNIQUE composite / INDEX | Reference vers le client proprietaire de la donnee. |
| `option_text` | `VARCHAR(255)` | 255 | NOT NULL / UNIQUE composite / INDEX composite | Texte de l'option proposee a l'utilisateur. |
| `usage_count` | `INTEGER` | - | NULL autorise | Nombre d'utilisations de l'option. |
| `created_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere mise a jour. |

## donnees

Table centrale des dossiers/enquetes importes depuis les fichiers source.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('donnees_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `fichier_id` | `INTEGER` | - | FK -> fichiers.id / NOT NULL / INDEX | Reference vers le fichier source importe. |
| `enqueteurId` | `INTEGER` | - | FK -> enqueteurs.id / NULL autorise / INDEX | Reference vers l'enqueteur affecte a l'enquete. |
| `enquete_originale_id` | `INTEGER` | - | FK -> donnees.id / NULL autorise | Reference vers l'enquete d'origine en cas de contestation. |
| `est_contestation` | `BOOLEAN` | - | NOT NULL | Indique si le dossier est une contestation. |
| `date_contestation` | `DATE` | - | NULL autorise | Date de creation ou reception de la contestation. |
| `motif_contestation_code` | `VARCHAR(16)` | 16 | NULL autorise | Code normalise du motif de contestation. |
| `motif_contestation_detail` | `VARCHAR(255)` | 255 | NULL autorise | Detail libre du motif de contestation. |
| `historique` | `TEXT` | - | NULL autorise | Historique JSON des evenements sur le dossier. |
| `statut_validation` | `VARCHAR(20)` | 20 | NOT NULL / INDEX | Statut courant du dossier dans le workflow de validation. |
| `numeroDossier` | `VARCHAR(10)` | 10 | NULL autorise / INDEX | Numero de dossier principal transmis par la source. |
| `referenceDossier` | `VARCHAR(15)` | 15 | NULL autorise | Reference complementaire du dossier. |
| `numeroInterlocuteur` | `VARCHAR(12)` | 12 | NULL autorise | Numero de l'interlocuteur cote source. |
| `guidInterlocuteur` | `VARCHAR(36)` | 36 | NULL autorise | Identifiant GUID de l'interlocuteur. |
| `typeDemande` | `VARCHAR(3)` | 3 | NULL autorise / INDEX | Type de demande metier code sur 3 caracteres. |
| `numeroDemande` | `VARCHAR(11)` | 11 | NULL autorise | Numero de demande principal. |
| `numeroDemandeContestee` | `VARCHAR(11)` | 11 | NULL autorise | Numero de demande contestee, si applicable. |
| `numeroDemandeInitiale` | `VARCHAR(11)` | 11 | NULL autorise | Numero de la demande initiale. |
| `forfaitDemande` | `VARCHAR(16)` | 16 | NULL autorise | Code ou libelle du forfait de demande. |
| `dateRetourEspere` | `DATE` | - | NULL autorise | Date de retour attendue pour l'enquete. |
| `qualite` | `VARCHAR(10)` | 10 | NULL autorise | Civilite ou qualite declaree de la personne. |
| `nom` | `VARCHAR(255)` | 255 | NULL autorise / INDEX | Nom ou libelle principal. |
| `prenom` | `VARCHAR(255)` | 255 | NULL autorise | Prenom. |
| `dateNaissance` | `DATE` | - | NULL autorise | Date de naissance declaree. |
| `lieuNaissance` | `VARCHAR(255)` | 255 | NULL autorise | Lieu de naissance declare. |
| `codePostalNaissance` | `VARCHAR(255)` | 255 | NULL autorise | Code postal du lieu de naissance. |
| `paysNaissance` | `VARCHAR(255)` | 255 | NULL autorise | Pays de naissance. |
| `nomPatronymique` | `VARCHAR(255)` | 255 | NULL autorise | Nom patronymique ou nom de naissance. |
| `adresse1` | `VARCHAR(255)` | 255 | NULL autorise | Adresse ligne 1. |
| `adresse2` | `VARCHAR(255)` | 255 | NULL autorise | Adresse ligne 2. |
| `adresse3` | `VARCHAR(255)` | 255 | NULL autorise | Adresse ligne 3. |
| `adresse4` | `VARCHAR(255)` | 255 | NULL autorise | Adresse ligne 4. |
| `ville` | `VARCHAR(50)` | 50 | NULL autorise | Ville de residence. |
| `codePostal` | `VARCHAR(255)` | 255 | NULL autorise | Code postal de residence. |
| `paysResidence` | `VARCHAR(255)` | 255 | NULL autorise | Pays de residence. |
| `telephonePersonnel` | `VARCHAR(255)` | 255 | NULL autorise | Telephone personnel declare. |
| `telephoneEmployeur` | `VARCHAR(255)` | 255 | NULL autorise | Telephone de l'employeur. |
| `telecopieEmployeur` | `VARCHAR(15)` | 15 | NULL autorise | Fax de l'employeur. |
| `nomEmployeur` | `VARCHAR(255)` | 255 | NULL autorise | Nom de l'employeur. |
| `banqueDomiciliation` | `VARCHAR(255)` | 255 | NULL autorise | Banque de domiciliation. |
| `libelleGuichet` | `VARCHAR(255)` | 255 | NULL autorise | Libelle du guichet bancaire. |
| `titulaireCompte` | `VARCHAR(255)` | 255 | NULL autorise | Titulaire du compte bancaire. |
| `codeBanque` | `VARCHAR(255)` | 255 | NULL autorise | Code banque. |
| `codeGuichet` | `VARCHAR(255)` | 255 | NULL autorise | Code guichet. |
| `numeroCompte` | `VARCHAR(255)` | 255 | NULL autorise | Numero de compte bancaire. |
| `ribCompte` | `VARCHAR(255)` | 255 | NULL autorise | Cle ou suffixe RIB. |
| `datedenvoie` | `DATE` | - | NULL autorise | Date d'envoi du dossier par la source. |
| `elementDemandes` | `VARCHAR(255)` | 255 | NULL autorise | Codes des elements demandes. |
| `elementObligatoires` | `VARCHAR(255)` | 255 | NULL autorise | Codes des elements obligatoires. |
| `elementContestes` | `VARCHAR(255)` | 255 | NULL autorise | Codes des elements contestes. |
| `codeMotif` | `VARCHAR(16)` | 16 | NULL autorise | Code du motif metier. |
| `motifDeContestation` | `VARCHAR(1000)` | 1000 | NULL autorise | Motif textuel de contestation. |
| `cumulMontantsPrecedents` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Cumul des montants precedemment factures. |
| `codesociete` | `VARCHAR(2)` | 2 | NULL autorise | Code societe ou entite source. |
| `urgence` | `VARCHAR(1)` | 1 | NULL autorise | Indicateur d'urgence. |
| `commentaire` | `VARCHAR(2000)` | 2000 | NULL autorise | Commentaire libre associe au dossier. |
| `date_butoir` | `DATE` | - | NULL autorise / INDEX | Date limite de traitement. |
| `exported` | `BOOLEAN` | - | NOT NULL | Indique si l'enquete a deja ete exportee. |
| `exported_at` | `TIMESTAMP` | - | NULL autorise | Date et heure du dernier export. |
| `created_at` | `TIMESTAMP` | - | NULL autorise / INDEX | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere mise a jour. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |
| `tarif_lettre` | `VARCHAR(10)` | 10 | NULL autorise | Code tarifaire lettre applique au dossier. |
| `recherche` | `VARCHAR(255)` | 255 | NULL autorise | Texte des recherches ou informations demandees. |
| `date_jour` | `DATE` | - | NULL autorise | Date du jour reportee sur certains dossiers. |
| `nom_complet` | `VARCHAR(255)` | 255 | NULL autorise | Nom complet consolide. |
| `motif` | `VARCHAR(500)` | 500 | NULL autorise | Motif libre complementaire. |
| `instructions` | `TEXT` | - | NULL autorise | Instructions specifiques pour le traitement du dossier. |
| `dateNaissance_maj` | `DATE` | - | NULL autorise / INDEX | Date de naissance mise a jour. |
| `lieuNaissance_maj` | `VARCHAR(50)` | 50 | NULL autorise | Lieu de naissance mis a jour. |

## donnees_enqueteur

Reponses, corrections et informations terrain saisies par les enqueteurs.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('donnees_enqueteur_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `donnee_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL | Reference vers l'enquete ou le dossier dans la table donnees. |
| `code_resultat` | `VARCHAR(1)` | 1 | NULL autorise | Code resultat saisi par l'enqueteur. |
| `elements_retrouves` | `VARCHAR(255)` | 255 | NULL autorise | Codes des elements retrouves par l'enqueteur. |
| `flag_etat_civil_errone` | `VARCHAR(1)` | 1 | NULL autorise | Marqueur signalant un etat civil errone. |
| `date_retour` | `DATE` | - | NULL autorise | Date de retour de l'enquete. |
| `qualite_corrigee` | `VARCHAR(10)` | 10 | NULL autorise | Qualite ou civilite corrigee. |
| `nom_corrige` | `VARCHAR(30)` | 30 | NULL autorise | Nom corrige. |
| `prenom_corrige` | `VARCHAR(20)` | 20 | NULL autorise | Prenom corrige. |
| `nom_patronymique_corrige` | `VARCHAR(30)` | 30 | NULL autorise | Nom patronymique corrige. |
| `code_postal_naissance_corrige` | `VARCHAR(10)` | 10 | NULL autorise | Code postal de naissance corrige. |
| `pays_naissance_corrige` | `VARCHAR(32)` | 32 | NULL autorise | Pays de naissance corrige. |
| `type_divergence` | `VARCHAR(20)` | 20 | NULL autorise | Type de divergence constate sur l'etat civil. |
| `adresse1` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a adresse1. |
| `adresse2` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a adresse2. |
| `adresse3` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a adresse3. |
| `adresse4` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a adresse4. |
| `code_postal` | `VARCHAR(10)` | 10 | NULL autorise | Code lie a postal. |
| `ville` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a ville. |
| `pays_residence` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a pays residence. |
| `telephone_personnel` | `VARCHAR(15)` | 15 | NULL autorise | Champ correspondant a telephone personnel. |
| `telephone_chez_employeur` | `VARCHAR(15)` | 15 | NULL autorise | Telephone joignable via l'employeur. |
| `nom_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Information employeur - nom. |
| `telephone_employeur` | `VARCHAR(15)` | 15 | NULL autorise | Information employeur - telephone. |
| `telecopie_employeur` | `VARCHAR(15)` | 15 | NULL autorise | Information employeur - telecopie. |
| `adresse1_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Ligne d'adresse employeur - adresse1. |
| `adresse2_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Ligne d'adresse employeur - adresse2. |
| `adresse3_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Ligne d'adresse employeur - adresse3. |
| `adresse4_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Ligne d'adresse employeur - adresse4. |
| `code_postal_employeur` | `VARCHAR(10)` | 10 | NULL autorise | Information employeur - code postal. |
| `ville_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Information employeur - ville. |
| `pays_employeur` | `VARCHAR(32)` | 32 | NULL autorise | Information employeur - pays. |
| `banque_domiciliation` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a banque domiciliation. |
| `libelle_guichet` | `VARCHAR(30)` | 30 | NULL autorise | Champ correspondant a libelle guichet. |
| `titulaire_compte` | `VARCHAR(32)` | 32 | NULL autorise | Champ correspondant a titulaire compte. |
| `code_banque` | `VARCHAR(5)` | 5 | NULL autorise | Code lie a banque. |
| `code_guichet` | `VARCHAR(5)` | 5 | NULL autorise | Code lie a guichet. |
| `date_deces` | `DATE` | - | NULL autorise | Date de deces constatee. |
| `numero_acte_deces` | `VARCHAR(10)` | 10 | NULL autorise | Numero d'acte de deces. |
| `code_insee_deces` | `VARCHAR(5)` | 5 | NULL autorise | Code INSEE du lieu de deces. |
| `code_postal_deces` | `VARCHAR(10)` | 10 | NULL autorise | Code postal du lieu de deces. |
| `localite_deces` | `VARCHAR(32)` | 32 | NULL autorise | Localite du deces. |
| `commentaires_revenus` | `VARCHAR(128)` | 128 | NULL autorise | Commentaires libres sur les revenus. |
| `montant_salaire` | `NUMERIC(10, 2)` | 10,2 | NULL autorise | Montant du salaire identifie. |
| `periode_versement_salaire` | `INTEGER` | - | NULL autorise | Periode ou jour de versement du salaire. |
| `frequence_versement_salaire` | `VARCHAR(2)` | 2 | NULL autorise | Frequence de versement du salaire. |
| `nature_revenu1` | `VARCHAR(30)` | 30 | NULL autorise | Nature du revenu 1. |
| `montant_revenu1` | `NUMERIC(10, 2)` | 10,2 | NULL autorise | Montant du revenu 1. |
| `periode_versement_revenu1` | `INTEGER` | - | NULL autorise | Periode de versement du revenu 1. |
| `frequence_versement_revenu1` | `VARCHAR(2)` | 2 | NULL autorise | Frequence de versement du revenu 1. |
| `nature_revenu2` | `VARCHAR(30)` | 30 | NULL autorise | Nature du revenu 2. |
| `montant_revenu2` | `NUMERIC(10, 2)` | 10,2 | NULL autorise | Montant du revenu 2. |
| `periode_versement_revenu2` | `INTEGER` | - | NULL autorise | Periode de versement du revenu 2. |
| `frequence_versement_revenu2` | `VARCHAR(2)` | 2 | NULL autorise | Frequence de versement du revenu 2. |
| `nature_revenu3` | `VARCHAR(30)` | 30 | NULL autorise | Nature du revenu 3. |
| `montant_revenu3` | `NUMERIC(10, 2)` | 10,2 | NULL autorise | Montant du revenu 3. |
| `periode_versement_revenu3` | `INTEGER` | - | NULL autorise | Periode de versement du revenu 3. |
| `frequence_versement_revenu3` | `VARCHAR(2)` | 2 | NULL autorise | Frequence de versement du revenu 3. |
| `numero_facture` | `VARCHAR(9)` | 9 | NULL autorise | Numero de facture. |
| `date_facture` | `DATE` | - | NULL autorise | Date de facture. |
| `montant_facture` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant de facture. |
| `tarif_applique` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Tarif applique a la facturation. |
| `cumul_montants_precedents` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Cumul des montants precedemment factures. |
| `reprise_facturation` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant de reprise de facturation. |
| `remise_eventuelle` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant de remise eventuelle. |
| `memo1` | `VARCHAR(64)` | 64 | NULL autorise | Memo court 1. |
| `memo2` | `VARCHAR(64)` | 64 | NULL autorise | Memo court 2. |
| `memo3` | `VARCHAR(64)` | 64 | NULL autorise | Memo court 3. |
| `memo4` | `VARCHAR(64)` | 64 | NULL autorise | Memo court 4. |
| `memo5` | `VARCHAR(1000)` | 1000 | NULL autorise | Memo long 5. |
| `notes_personnelles` | `TEXT` | - | NULL autorise | Notes personnelles de l'enqueteur. |
| `created_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere mise a jour. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |
| `proximite` | `TEXT` | - | NULL autorise | Valeur de confirmation ou proximite selectionnee. |

## enquete_archive_files

Fichiers physiques d'archives/export lies a une enquete.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('enquete_archive_files_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `enquete_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL / UNIQUE / INDEX | Reference vers l'enquete concernee. |
| `filename` | `VARCHAR(255)` | 255 | NOT NULL | Nom du fichier stocke ou exporte. |
| `filepath` | `VARCHAR(500)` | 500 | NOT NULL | Chemin de stockage du fichier sur disque. |
| `type_export` | `VARCHAR(20)` | 20 | NOT NULL | Type de fichier exporte. |
| `file_size` | `INTEGER` | - | NULL autorise | Taille du fichier en octets. |
| `created_at` | `TIMESTAMP` | - | NOT NULL | Date et heure de creation de la ligne. |
| `utilisateur` | `VARCHAR(100)` | 100 | NULL autorise | Utilisateur ayant realise l'action. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |

## enquete_archives

Historique logique des exportations d'enquetes.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('enquete_archives_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `enquete_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL | Reference vers l'enquete concernee. |
| `date_export` | `TIMESTAMP` | - | NOT NULL | Date et heure de l'export. |
| `nom_fichier` | `VARCHAR(255)` | 255 | NULL autorise | Nom du fichier exporte. |
| `utilisateur` | `VARCHAR(100)` | 100 | NULL autorise | Utilisateur ayant realise l'action. |

## enquete_facturation

Montants de facturation client et de remuneration enqueteur par enquete.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('enquete_facturation_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `donnee_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL / UNIQUE composite / INDEX composite | Reference vers l'enquete ou le dossier dans la table donnees. |
| `donnee_enqueteur_id` | `INTEGER` | - | FK -> donnees_enqueteur.id / NOT NULL / UNIQUE composite / INDEX composite | Reference vers la reponse enqueteur liee. |
| `tarif_eos_code` | `VARCHAR(100)` | 100 | NULL autorise | Code tarif EOS retenu pour la facturation client. |
| `tarif_eos_montant` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant de base du tarif EOS. |
| `resultat_eos_montant` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant EOS final apres ajustement. |
| `tarif_enqueteur_code` | `VARCHAR(100)` | 100 | NULL autorise | Code tarif enqueteur retenu. |
| `tarif_enqueteur_montant` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant de base du tarif enqueteur. |
| `resultat_enqueteur_montant` | `NUMERIC(8, 2)` | 8,2 | NULL autorise | Montant final verse a l'enqueteur. |
| `paye` | `BOOLEAN` | - | NOT NULL | Indique si le paiement a ete effectue. |
| `date_paiement` | `DATE` | - | NULL autorise | Date de paiement de l'enqueteur. |
| `reference_paiement` | `VARCHAR(50)` | 50 | NULL autorise | Reference du paiement. |
| `created_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere mise a jour. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |

## enquetes_terminees

Trace des enquetes confirmees/terminees.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('enquetes_terminees_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `donnee_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL | Reference vers l'enquete ou le dossier dans la table donnees. |
| `confirmed_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de confirmation. |
| `confirmed_by` | `VARCHAR(100)` | 100 | NOT NULL | Utilisateur ayant confirme l'enquete. |

## enqueteurs

Referentiel des enqueteurs utilisateurs du systeme.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('enqueteurs_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `nom` | `VARCHAR(100)` | 100 | NOT NULL | Nom ou libelle principal. |
| `prenom` | `VARCHAR(100)` | 100 | NOT NULL | Prenom. |
| `email` | `VARCHAR(120)` | 120 | NOT NULL / UNIQUE / INDEX | Adresse email. |
| `telephone` | `VARCHAR(20)` | 20 | NULL autorise | Numero de telephone. |
| `date_creation` | `TIMESTAMP` | - | NULL autorise | Date et heure de creation de la ligne. |
| `vpn_config_generated` | `BOOLEAN` | - | NULL autorise | Champ correspondant a VPN config generated. |

## export_batches

Historique des exports groupes contenant plusieurs enquetes.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('export_batches_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `filename` | `VARCHAR(255)` | 255 | NOT NULL | Nom du fichier stocke ou exporte. |
| `filepath` | `VARCHAR(500)` | 500 | NOT NULL | Chemin de stockage du fichier sur disque. |
| `file_size` | `INTEGER` | - | NULL autorise | Taille du fichier en octets. |
| `enquete_count` | `INTEGER` | - | NOT NULL | Nombre d'enquetes incluses dans le batch. |
| `created_at` | `TIMESTAMP` | - | NOT NULL | Date et heure de creation de la ligne. |
| `utilisateur` | `VARCHAR(100)` | 100 | NULL autorise | Utilisateur ayant realise l'action. |
| `enquete_ids` | `TEXT` | - | NULL autorise | Liste des identifiants d'enquetes incluses. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |

## fichiers

Fichiers sources importes dans l'application.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('fichiers_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `nom` | `VARCHAR(255)` | 255 | NOT NULL | Nom du fichier importe. |
| `chemin` | `VARCHAR(500)` | 500 | NULL autorise | Chemin d'origine ou de stockage du fichier. |
| `date_upload` | `TIMESTAMP` | - | NULL autorise | Date et heure d'import du fichier. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |

## import_field_mappings

Regles de mapping entre colonnes source et champs internes EOS.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('import_field_mappings_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `import_profile_id` | `INTEGER` | - | FK -> import_profiles.id / NOT NULL / INDEX | Reference vers le profil d'import. |
| `internal_field` | `VARCHAR(100)` | 100 | NOT NULL / INDEX | Nom du champ interne cible dans EOS. |
| `start_pos` | `INTEGER` | - | NULL autorise | Position de debut dans un fichier texte fixe. |
| `length` | `INTEGER` | - | NULL autorise | Longueur a extraire dans un fichier texte fixe. |
| `column_name` | `VARCHAR(255)` | 255 | NULL autorise | Nom de colonne attendu dans un fichier Excel. |
| `column_index` | `INTEGER` | - | NULL autorise | Index de colonne alternatif dans un fichier Excel. |
| `strip_whitespace` | `BOOLEAN` | - | NULL autorise | Indique si les espaces doivent etre supprimes. |
| `default_value` | `VARCHAR(255)` | 255 | NULL autorise | Valeur par defaut si la source est vide. |
| `is_required` | `BOOLEAN` | - | NULL autorise | Indique si le champ est obligatoire. |
| `date_creation` | `TIMESTAMP` | - | NOT NULL | Date et heure de creation de la ligne. |

## import_profiles

Profils de parametrage d'import par client et type de fichier.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('import_profiles_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |
| `name` | `VARCHAR(255)` | 255 | NOT NULL | Nom du profil d'import. |
| `file_type` | `VARCHAR(50)` | 50 | NOT NULL | Type de fichier supporte par le profil. |
| `sheet_name` | `VARCHAR(255)` | 255 | NULL autorise | Nom de feuille Excel a lire. |
| `encoding` | `VARCHAR(50)` | 50 | NULL autorise | Encodage du fichier source. |
| `actif` | `BOOLEAN` | - | NOT NULL | Indique si l'element est actif. |
| `date_creation` | `TIMESTAMP` | - | NOT NULL | Date et heure de creation de la ligne. |
| `date_modification` | `TIMESTAMP` | - | NULL autorise | Date et heure de derniere modification. |

## partner_case_requests

Demandes normalisees detectees par dossier pour le mode PARTNER.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('partner_case_requests_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `donnee_id` | `INTEGER` | - | FK -> donnees.id / NOT NULL / UNIQUE composite / INDEX | Reference vers l'enquete ou le dossier dans la table donnees. |
| `request_code` | `VARCHAR(20)` | 20 | NOT NULL / UNIQUE composite / INDEX composite | Code normalise de la demande. |
| `requested` | `BOOLEAN` | - | NULL autorise / DEFAULT true | Indique que la demande figure dans RECHERCHE. |
| `found` | `BOOLEAN` | - | NULL autorise / DEFAULT false | Indique que la demande a ete satisfaite. |
| `status` | `VARCHAR(10)` | 10 | NULL autorise / INDEX | Statut metier de la ligne. |
| `memo` | `TEXT` | - | NULL autorise | Commentaire ou justification libre. |
| `created_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de derniere mise a jour. |

## partner_request_keywords

Mots-cles servant a detecter les demandes PARTNER dans le champ RECHERCHE.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('partner_request_keywords_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |
| `request_code` | `VARCHAR(20)` | 20 | NOT NULL / INDEX | Code normalise de la demande. |
| `pattern` | `VARCHAR(100)` | 100 | NOT NULL | Mot-cle a rechercher dans RECHERCHE. |
| `is_regex` | `BOOLEAN` | - | NULL autorise / DEFAULT false | Indique si le motif est une expression reguliere. |
| `priority` | `INTEGER` | - | NULL autorise / DEFAULT 0 | Priorite de traitement ou d'evaluation. |
| `created_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de derniere mise a jour. |

## partner_tarif_rules

Regles tarifaires PARTNER selon la lettre et la combinaison de demandes.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('partner_tarif_rules_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / UNIQUE composite / INDEX composite | Reference vers le client proprietaire de la donnee. |
| `tarif_lettre` | `VARCHAR(5)` | 5 | NOT NULL / UNIQUE composite / INDEX composite | Lettre tarifaire de reference. |
| `request_key` | `VARCHAR(100)` | 100 | NOT NULL / UNIQUE composite / INDEX composite | Cle composee representant une combinaison de demandes. |
| `amount` | `NUMERIC(10, 2)` | 10,2 | NOT NULL | Montant applique par une regle tarifaire. |
| `created_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de creation de la ligne. |
| `updated_at` | `TIMESTAMP` | - | NULL autorise / DEFAULT now() | Date et heure de derniere mise a jour. |

## sherlock_donnees

Donnees importees depuis le format Sherlock, avec source et reponse enqueteur.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('sherlock_donnees_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `fichier_id` | `INTEGER` | - | FK -> fichiers.id / NULL autorise | Reference vers le fichier source importe. |
| `created_at` | `TIMESTAMP` | - | NULL autorise | Date et heure de creation de la ligne. |
| `dossier_id` | `VARCHAR(50)` | 50 | NULL autorise | Identifiant dossier venant de Sherlock. |
| `reference_interne` | `VARCHAR(50)` | 50 | NULL autorise | Reference interne du dossier. |
| `demande` | `VARCHAR(100)` | 100 | NULL autorise | Nature de la demande source. |
| `ec_civilite` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - civilite. |
| `ec_prenom` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - prenom. |
| `ec_prenom2` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - prenom2. |
| `ec_prenom3` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - prenom3. |
| `ec_prenom4` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - prenom4. |
| `ec_nom_usage` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - nom usage. |
| `ec_nom_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - nom naissance. |
| `ec_date_naissance` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source etat civil - date naissance. |
| `naissance_cp` | `VARCHAR(20)` | 20 | NULL autorise | Champ correspondant a naissance CP. |
| `ec_localite_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - localite naissance. |
| `naissance_insee` | `VARCHAR(20)` | 20 | NULL autorise | Champ correspondant a naissance INSEE. |
| `ec_pays_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source etat civil - pays naissance. |
| `client_commentaire` | `TEXT` | - | NULL autorise | Commentaire fourni par le client dans Sherlock. |
| `ad_l1` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l1. |
| `ad_l2` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l2. |
| `ad_l3` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l3. |
| `ad_l4_numero` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - l4 numero. |
| `ad_l4_type` | `VARCHAR(50)` | 50 | NULL autorise | Donnee source adresse/contact - l4 type. |
| `ad_l4_voie` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l4 voie. |
| `ad_l5` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l5. |
| `ad_l6_cedex` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - l6 cedex. |
| `ad_l6_cp` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - l6 CP. |
| `ad_l6_insee` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - l6 INSEE. |
| `ad_l6_localite` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l6 localite. |
| `ad_l7_pays` | `VARCHAR(100)` | 100 | NULL autorise | Donnee source adresse/contact - l7 pays. |
| `ad_telephone` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - telephone. |
| `ad_telephone_pro` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - telephone pro. |
| `ad_telephone_mobile` | `VARCHAR(20)` | 20 | NULL autorise | Donnee source adresse/contact - telephone mobile. |
| `ad_email` | `VARCHAR(255)` | 255 | NULL autorise | Donnee source adresse/contact - email. |
| `tarif_a` | `VARCHAR(50)` | 50 | NULL autorise | Valeur tarifaire A recopiee depuis Sherlock. |
| `tarif_at` | `VARCHAR(50)` | 50 | NULL autorise | Valeur tarifaire AT recopiee depuis Sherlock. |
| `tarif_dcd` | `VARCHAR(50)` | 50 | NULL autorise | Valeur tarifaire DCD recopiee depuis Sherlock. |
| `resultat` | `VARCHAR(50)` | 50 | NULL autorise | Resultat retourne pour le dossier Sherlock. |
| `montant_ht` | `DOUBLE PRECISION` | 53 | NULL autorise | Montant hors taxes calcule ou importe. |
| `rep_ec_civilite` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - civilite. |
| `rep_ec_prenom` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - prenom. |
| `rep_ec_prenom2` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - prenom2. |
| `rep_ec_prenom3` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - prenom3. |
| `rep_ec_prenom4` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - prenom4. |
| `rep_ec_nom_usage` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - nom usage. |
| `rep_ec_nom_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - nom naissance. |
| `rep_ec_date_naissance` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - etat civil - date naissance. |
| `rep_naissance_cp` | `VARCHAR(20)` | 20 | NULL autorise | Champ correspondant a rep naissance CP. |
| `rep_ec_localite_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - localite naissance. |
| `rep_naissance_insee` | `VARCHAR(20)` | 20 | NULL autorise | Champ correspondant a rep naissance INSEE. |
| `rep_ec_pays_naissance` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - etat civil - pays naissance. |
| `rep_dcd_date` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - deces - date. |
| `rep_dcd_numero_acte` | `VARCHAR(50)` | 50 | NULL autorise | Reponse enqueteur - deces - numero acte. |
| `rep_dcd_localite` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - deces - localite. |
| `rep_dcd_cp` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - deces - CP. |
| `rep_dcd_insee` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - deces - INSEE. |
| `rep_dcd_pays` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - deces - pays. |
| `rep_ad_l1` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l1. |
| `rep_ad_l2` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l2. |
| `rep_ad_l3` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l3. |
| `rep_ad_l4_numero` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - adresse/contact - l4 numero. |
| `rep_ad_l4_type` | `VARCHAR(50)` | 50 | NULL autorise | Reponse enqueteur - adresse/contact - l4 type. |
| `rep_ad_l4_voie` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l4 voie. |
| `rep_ad_l5` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l5. |
| `rep_ad_l6_cedex` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - adresse/contact - l6 cedex. |
| `rep_ad_l6_cp` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - adresse/contact - l6 CP. |
| `rep_ad_l6_insee` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - adresse/contact - l6 INSEE. |
| `rep_ad_l6_localite` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l6 localite. |
| `rep_ad_l7_pays` | `VARCHAR(100)` | 100 | NULL autorise | Reponse enqueteur - adresse/contact - l7 pays. |
| `rep_ad_telephone` | `VARCHAR(20)` | 20 | NULL autorise | Reponse enqueteur - adresse/contact - telephone. |

## tarifs_client

Tarifs specifiques definis pour chaque client.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('tarifs_client_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NOT NULL / INDEX | Reference vers le client proprietaire de la donnee. |
| `code_lettre` | `VARCHAR(10)` | 10 | NOT NULL | Code lettre du tarif client. |
| `description` | `VARCHAR(100)` | 100 | NULL autorise | Description textuelle. |
| `montant` | `NUMERIC(8, 2)` | 8,2 | NOT NULL | Montant financier associe. |
| `date_debut` | `DATE` | - | NOT NULL | Date de debut de validite. |
| `date_fin` | `DATE` | - | NULL autorise | Date de fin de validite. |
| `actif` | `BOOLEAN` | - | NULL autorise | Indique si l'element est actif. |

## tarifs_enqueteur

Tarifs de remuneration des enqueteurs.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('tarifs_enqueteur_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `code` | `VARCHAR(10)` | 10 | NOT NULL | Code du tarif enqueteur. |
| `description` | `VARCHAR(100)` | 100 | NULL autorise | Description textuelle. |
| `montant` | `NUMERIC(8, 2)` | 8,2 | NOT NULL | Montant financier associe. |
| `enqueteur_id` | `INTEGER` | - | FK -> enqueteurs.id / NULL autorise | Reference vers l'enqueteur concerne. |
| `date_debut` | `DATE` | - | NOT NULL | Date de debut de validite. |
| `date_fin` | `DATE` | - | NULL autorise | Date de fin de validite. |
| `actif` | `BOOLEAN` | - | NULL autorise | Indique si l'element est actif. |
| `client_id` | `INTEGER` | - | FK -> clients.id / NULL autorise / INDEX | Reference vers le client proprietaire de la donnee. |

## tarifs_eos

Tarifs factures par EOS au client final.

| Champ | Type SQL | Grandeur | Caracteristiques | Explication |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | - | PK / NOT NULL / DEFAULT nextval('tarifs_eos_id_seq'::regclass) | Identifiant technique unique de la ligne. |
| `code` | `VARCHAR(10)` | 10 | NOT NULL / UNIQUE / INDEX | Code du tarif EOS. |
| `description` | `VARCHAR(100)` | 100 | NULL autorise | Description textuelle. |
| `montant` | `NUMERIC(8, 2)` | 8,2 | NOT NULL | Montant financier associe. |
| `date_debut` | `DATE` | - | NOT NULL | Date de debut de validite. |
| `date_fin` | `DATE` | - | NULL autorise | Date de fin de validite. |
| `actif` | `BOOLEAN` | - | NULL autorise | Indique si l'element est actif. |
