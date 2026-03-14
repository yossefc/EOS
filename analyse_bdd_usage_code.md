# Analyse base de donnees EOS et usage dans le code

Date d'analyse: 2026-03-14

## Methode

Cette analyse croise 4 sources:

- la base PostgreSQL reelle `eos_db`
- les modeles SQLAlchemy du projet
- les references dans le code backend/frontend
- le taux de remplissage des colonnes via `pg_stats`

Base verifiee:

- `eos_db`: base metier utilisee par l'application
- `postgres`: base systeme standard de PostgreSQL, normale, pas une base metier EOS

Configuration observee:

- [backend/.env](/D:/EOS/backend/.env)
- [backend/config.py](/D:/EOS/backend/config.py)

La connexion applicative pointe vers `eos_db`.

## Reponse a la question `eos_db` vs `postgres`

- `eos_db` contient les tables EOS et les donnees metier.
- `postgres` est la base d'administration livree par PostgreSQL.
- Il est normal d'avoir les deux.
- L'application EOS doit travailler sur `eos_db`, pas sur `postgres`.

## Etat reel des tables

J'ai verifie 20 tables dans `eos_db`.

Volumes observes:

| Table | Lignes | Statut global |
| --- | ---: | --- |
| `alembic_version` | 1 | technique, indispensable |
| `clients` | 3 | actif, indispensable |
| `confirmation_options` | 0 | optionnel, code present |
| `donnees` | 14213 | coeur metier, indispensable |
| `donnees_enqueteur` | 14281 | coeur metier, indispensable |
| `enquete_archive_files` | 0 | fonction archive presente, non alimentee |
| `enquete_facturation` | 14053 | actif, indispensable si facturation utilisee |
| `enquetes_terminees` | 0 | workflow de validation present, non alimente |
| `enqueteurs` | 3 | actif, indispensable |
| `export_batches` | 17 | actif, utilise pour exports/archives |
| `fichiers` | 17 | actif, indispensable |
| `import_field_mappings` | 152 | actif, indispensable pour imports |
| `import_profiles` | 4 | actif, indispensable pour imports |
| `partner_case_requests` | 7 | actif mais tres cible PARTNER |
| `partner_request_keywords` | 5 | actif mais cible PARTNER |
| `partner_tarif_rules` | 9 | actif mais cible PARTNER |
| `sherlock_donnees` | 1 | support specifique Sherlock, tres peu utilise actuellement |
| `tarifs_client` | 6 | actif si tarification client specifique |
| `tarifs_enqueteur` | 12 | actif |
| `tarifs_eos` | 12 | actif |

## Conclusion rapide

### Tables indispensables

- `donnees`
- `donnees_enqueteur`
- `fichiers`
- `clients`
- `enqueteurs`
- `import_profiles`
- `import_field_mappings`
- `tarifs_eos`
- `tarifs_enqueteur`

### Tables importantes selon vos usages

- `enquete_facturation`
- `tarifs_client`
- `export_batches`
- `partner_case_requests`
- `partner_request_keywords`
- `partner_tarif_rules`
- `sherlock_donnees`

### Tables optionnelles ou actuellement peu exploitees

- `confirmation_options`
- `enquete_archive_files`
- `enquetes_terminees`

### Tables techniques a ne pas supprimer

- `alembic_version`

## Analyse par table

## 1. `donnees`

Role:

- table centrale des dossiers/enquetes importes
- pilote l'affectation, l'etat, les exports, les contestations

Usage code:

- massivement utilise dans [backend/app.py](/D:/EOS/backend/app.py)
- utilise pour l'import/export dans [backend/utils.py](/D:/EOS/backend/utils.py)
- utilise dans les routes [backend/routes/validation.py](/D:/EOS/backend/routes/validation.py), [backend/routes/partner_export.py](/D:/EOS/backend/routes/partner_export.py), [backend/routes/tarification.py](/D:/EOS/backend/routes/tarification.py), [backend/routes/enquetes.py](/D:/EOS/backend/routes/enquetes.py)
- fortement consomme par le frontend: [frontend/src/components/DataViewer.jsx](/D:/EOS/frontend/src/components/DataViewer.jsx), [frontend/src/components/UpdateModal.jsx](/D:/EOS/frontend/src/components/UpdateModal.jsx), [frontend/src/components/AssignmentViewer.jsx](/D:/EOS/frontend/src/components/AssignmentViewer.jsx), [frontend/src/components/HistoryModal.jsx](/D:/EOS/frontend/src/components/HistoryModal.jsx), [frontend/src/components/EnqueteExporter.jsx](/D:/EOS/frontend/src/components/EnqueteExporter.jsx)

Verdict:

- indispensable

### Champs `donnees` clairement utilises par le code

- `id`
- `client_id`
- `fichier_id`
- `enqueteurId`
- `numeroDossier`
- `referenceDossier`
- `typeDemande`
- `nom`
- `prenom`
- `dateNaissance`
- `lieuNaissance`
- `date_butoir`
- `statut_validation`
- `exported`
- `exported_at`
- `created_at`
- `updated_at`
- `est_contestation`
- `enquete_originale_id`
- `date_contestation`
- `motif_contestation_code`
- `motif_contestation_detail`
- `historique`
- `tarif_lettre`
- `recherche`
- `instructions`
- `motif`
- `dateNaissance_maj`
- `lieuNaissance_maj`

### Champs `donnees` alimentes dans les donnees et potentiellement utiles

Ces champs ont un taux de remplissage notable, meme si l'usage direct dans le code est plus discret:

- `datedenvoie` 67.6%
- `telephonePersonnel` 66.4%
- `adresse1` 62.0%
- `codePostal` 59.7%
- `ville` 59.6%
- `forfaitDemande` 28.2%
- `guidInterlocuteur` 28.2%
- `numeroInterlocuteur` 28.2%
- `qualite` 27.7%
- `dateRetourEspere` 27.4%
- `codePostalNaissance` 25.9%
- `nomPatronymique` 22.2%

### Champs `donnees` peu exploites ou quasi vides

Peu remplis dans la base actuelle, donc probablement non essentiels dans votre usage courant:

- `paysResidence`
- `adresse2`
- `adresse3`
- `adresse4`
- `codeBanque`
- `codeGuichet`
- `numeroCompte`
- `ribCompte`
- `banqueDomiciliation`
- `libelleGuichet`
- `titulaireCompte`
- `nomEmployeur`
- `telephoneEmployeur`
- `telecopieEmployeur`
- `commentaire`
- `elementDemandes`
- `elementObligatoires`
- `elementContestes`
- `codeMotif`
- `motifDeContestation`
- `date_jour`
- `nom_complet`
- `cumulMontantsPrecedents`

### Champs `donnees` prevus par le code mais actuellement non alimentes

- `enqueteurId`
- `date_contestation`
- `enquete_originale_id`
- `motif_contestation_code`
- `motif_contestation_detail`
- `dateNaissance_maj`
- `lieuNaissance_maj`

Interpretation:

- le code supporte bien les contestations et les mises a jour d'etat civil
- dans vos donnees actuelles, ces fonctions ne semblent pas encore alimentees ou sont tres marginales

## 2. `donnees_enqueteur`

Role:

- stocke les retours terrain, corrections, memos, informations de deces, employeur, banque, facturation annexe

Usage code:

- central dans [backend/app.py](/D:/EOS/backend/app.py)
- central dans [backend/routes/validation.py](/D:/EOS/backend/routes/validation.py)
- central dans [backend/services/tarification_service.py](/D:/EOS/backend/services/tarification_service.py)
- central dans [backend/services/billing_service.py](/D:/EOS/backend/services/billing_service.py)
- central dans [backend/services/partner_export_service.py](/D:/EOS/backend/services/partner_export_service.py)
- central dans [frontend/src/components/UpdateModal.jsx](/D:/EOS/frontend/src/components/UpdateModal.jsx)
- visible dans [frontend/src/components/HistoryModal.jsx](/D:/EOS/frontend/src/components/HistoryModal.jsx), [frontend/src/components/PaiementManager.jsx](/D:/EOS/frontend/src/components/PaiementManager.jsx), [frontend/src/components/EnqueteurDashboard.jsx](/D:/EOS/frontend/src/components/EnqueteurDashboard.jsx)

Verdict:

- indispensable

### Champs `donnees_enqueteur` clairement utilises

- `id`
- `client_id`
- `donnee_id`
- `code_resultat`
- `elements_retrouves`
- `proximite`
- `flag_etat_civil_errone`
- `date_retour`
- `adresse1`
- `adresse2`
- `adresse3`
- `adresse4`
- `code_postal`
- `ville`
- `pays_residence`
- `telephone_personnel`
- `telephone_chez_employeur`
- `nom_employeur`
- `telephone_employeur`
- `telecopie_employeur`
- `banque_domiciliation`
- `libelle_guichet`
- `titulaire_compte`
- `code_banque`
- `code_guichet`
- `date_deces`
- `numero_acte_deces`
- `code_insee_deces`
- `code_postal_deces`
- `localite_deces`
- `nom_corrige`
- `prenom_corrige`
- `qualite_corrigee`
- `type_divergence`
- `memo1`
- `memo2`
- `memo3`
- `memo4`
- `memo5`
- `notes_personnelles`
- `tarif_applique`
- `numero_facture`
- `date_facture`
- `montant_facture`
- `cumul_montants_precedents`
- `reprise_facturation`
- `remise_eventuelle`

### Champs `donnees_enqueteur` reellement alimentes aujourd'hui

- `code_resultat` 94.5%
- `code_postal` 81.0%
- `ville` 80.9%
- `adresse1` 72.4%
- `montant_facture` 66.7%
- `telephone_personnel` 36.8%
- `date_retour` 28.1%
- `cumul_montants_precedents` 26.7%
- `reprise_facturation` 26.7%
- `remise_eventuelle` 26.7%
- `tarif_applique` 26.7%
- `adresse2` 23.1%
- `adresse3` 19.5%
- `elements_retrouves` 17.7%
- `date_facture` 17.5%
- `proximite` 16.2%
- `notes_personnelles` 11.1%

### Champs `donnees_enqueteur` supportes par le code mais peu alimentes

- `nom_employeur`
- `telephone_chez_employeur`
- `banque_domiciliation`
- `code_banque`
- `code_guichet`
- `date_deces`
- `numero_acte_deces`
- `code_insee_deces`
- `code_postal_deces`
- `localite_deces`
- `memo1`
- `memo2`
- `memo3`

### Champs `donnees_enqueteur` actuellement dormants

Ces colonnes existent mais sont a 0% de remplissage dans la base analysee:

- toutes les adresses employeur
- tous les champs revenus `nature_revenu*`, `montant_revenu*`, `periode_versement_*`, `frequence_versement_*`
- `commentaires_revenus`
- `montant_salaire`
- `nom_patronymique_corrige`
- `code_postal_naissance_corrige`
- `pays_naissance_corrige`
- `memo4`
- `memo5`
- `numero_facture`
- `pays_employeur`
- `ville_employeur`

Interpretation:

- le coeur du workflow se sert surtout du resultat, de l'adresse, du retour, du telephone, des memos simples et de la mini-facturation
- la partie revenus, employeur detaille, corrections etat civil avancées et banque detaillee existe dans le code mais n'est quasiment pas exploitee dans les donnees actuelles

## 3. `enquete_facturation`

Role:

- trace les montants factures au client et les montants dus a l'enqueteur

Usage code:

- fortement utilise dans [backend/routes/tarification.py](/D:/EOS/backend/routes/tarification.py)
- fortement utilise dans [backend/services/tarification_service.py](/D:/EOS/backend/services/tarification_service.py)
- visible dans [frontend/src/components/EarningsViewer.jsx](/D:/EOS/frontend/src/components/EarningsViewer.jsx), [frontend/src/components/PaiementManager.jsx](/D:/EOS/frontend/src/components/PaiementManager.jsx), [frontend/src/components/FinancialReports.jsx](/D:/EOS/frontend/src/components/FinancialReports.jsx)

Verdict:

- indispensable si vous utilisez la facturation et les paiements

### Champs actifs

- `donnee_id`
- `donnee_enqueteur_id`
- `client_id`
- `tarif_eos_code`
- `tarif_eos_montant`
- `resultat_eos_montant`
- `tarif_enqueteur_code`
- `tarif_enqueteur_montant`
- `resultat_enqueteur_montant`
- `paye`
- `created_at`
- `updated_at`

### Champs prevus mais non encore utilises dans les donnees

- `date_paiement`
- `reference_paiement`

Interpretation:

- la facturation est active
- la traçabilite de paiement n'est pas encore renseignee en base dans l'etat actuel

## 4. `fichiers`

Role:

- journal des fichiers importes

Usage code:

- actif dans [backend/app.py](/D:/EOS/backend/app.py)
- actif dans [backend/utils.py](/D:/EOS/backend/utils.py)
- visible dans [frontend/src/components/ImportHandler.jsx](/D:/EOS/frontend/src/components/ImportHandler.jsx), [frontend/src/components/StatsViewer.jsx](/D:/EOS/frontend/src/components/StatsViewer.jsx)

Champs utiles:

- `id`
- `client_id`
- `nom`
- `chemin`
- `date_upload`

Verdict:

- indispensable

## 5. `clients`

Role:

- referentiel multi-client

Usage code:

- massivement utilise pour le filtrage et les import/export
- references dans [backend/client_utils.py](/D:/EOS/backend/client_utils.py), [backend/app.py](/D:/EOS/backend/app.py), [backend/routes/partner_export.py](/D:/EOS/backend/routes/partner_export.py)
- visible partout dans le frontend multi-client

Champs utiles:

- `id`
- `code`
- `nom`
- `actif`
- `date_creation`
- `date_modification`

Verdict:

- indispensable

## 6. `enqueteurs`

Role:

- referentiel des enqueteurs

Usage code:

- utilise pour l'affectation, la validation, l'interface enqueteur et la configuration VPN
- references dans [backend/app.py](/D:/EOS/backend/app.py), [backend/routes/validation.py](/D:/EOS/backend/routes/validation.py), [backend/routes/vpn_download.py](/D:/EOS/backend/routes/vpn_download.py)

Champs utiles:

- `id`
- `nom`
- `prenom`
- `email`
- `telephone`
- `date_creation`
- `vpn_config_generated`

Verdict:

- indispensable

## 7. `import_profiles`

Role:

- definit le type d'import par client

Usage code:

- actif dans [backend/client_utils.py](/D:/EOS/backend/client_utils.py)
- actif dans [backend/import_engine.py](/D:/EOS/backend/import_engine.py)
- utilise dans [backend/app.py](/D:/EOS/backend/app.py)

Champs utiles:

- `client_id`
- `name`
- `file_type`
- `sheet_name`
- `encoding`
- `actif`
- `date_creation`
- `date_modification`

Verdict:

- indispensable

## 8. `import_field_mappings`

Role:

- mappe les colonnes source vers les champs EOS

Usage code:

- central dans [backend/import_engine.py](/D:/EOS/backend/import_engine.py)
- central dans [backend/models/import_config.py](/D:/EOS/backend/models/import_config.py)

Champs utiles:

- `import_profile_id`
- `internal_field`
- `start_pos`
- `length`
- `column_name`
- `column_index`
- `strip_whitespace`
- `default_value`
- `is_required`
- `date_creation`

Verdict:

- indispensable

## 9. `tarifs_eos`

Role:

- tarifs factures par EOS

Usage code:

- actif dans [backend/routes/tarification.py](/D:/EOS/backend/routes/tarification.py)
- actif dans [backend/services/tarification_service.py](/D:/EOS/backend/services/tarification_service.py)
- visible dans [frontend/src/components/TarificationViewer.jsx](/D:/EOS/frontend/src/components/TarificationViewer.jsx)

Champs utiles:

- `code`
- `description`
- `montant`
- `date_debut`
- `date_fin`
- `actif`

Verdict:

- actif

## 10. `tarifs_enqueteur`

Role:

- tarifs de remuneration des enqueteurs

Usage code:

- actif dans [backend/routes/tarification.py](/D:/EOS/backend/routes/tarification.py)
- actif dans [backend/services/tarification_service.py](/D:/EOS/backend/services/tarification_service.py)
- visible dans [frontend/src/components/TarificationViewer.jsx](/D:/EOS/frontend/src/components/TarificationViewer.jsx)

Champs utiles:

- `code`
- `description`
- `montant`
- `enqueteur_id`
- `client_id`
- `date_debut`
- `date_fin`
- `actif`

Verdict:

- actif

## 11. `tarifs_client`

Role:

- tarifs specifiques par client, surtout utile pour PARTNER ou d'autres regles dediees

Usage code:

- actif dans [backend/services/tarification_service.py](/D:/EOS/backend/services/tarification_service.py)
- actif dans [backend/app.py](/D:/EOS/backend/app.py)

Champs utiles:

- `client_id`
- `code_lettre`
- `description`
- `montant`
- `date_debut`
- `date_fin`
- `actif`

Verdict:

- utile si vous maintenez une tarification differenciee par client

## 12. `partner_request_keywords`

Role:

- dictionnaire de mots-cles pour parser `donnees.recherche`

Usage code:

- actif dans [backend/services/partner_request_parser.py](/D:/EOS/backend/services/partner_request_parser.py)
- actif dans [backend/routes/partner_admin.py](/D:/EOS/backend/routes/partner_admin.py)
- visible dans [frontend/src/components/PartnerKeywordsAdmin.jsx](/D:/EOS/frontend/src/components/PartnerKeywordsAdmin.jsx)

Champs utiles:

- `client_id`
- `request_code`
- `pattern`
- `is_regex`
- `priority`
- `created_at`
- `updated_at`

Verdict:

- utile uniquement pour le mode/client PARTNER

## 13. `partner_case_requests`

Role:

- stocke les demandes normalisees par dossier PARTNER

Usage code:

- cree dans [backend/import_engine.py](/D:/EOS/backend/import_engine.py)
- utilise dans [backend/services/partner_request_calculator.py](/D:/EOS/backend/services/partner_request_calculator.py)
- expose dans [frontend/src/components/PartnerDemandesHeader.jsx](/D:/EOS/frontend/src/components/PartnerDemandesHeader.jsx)

Champs utiles:

- `donnee_id`
- `request_code`
- `requested`
- `found`
- `status`
- `memo`
- `created_at`
- `updated_at`

Etat reel:

- table alimentee
- `memo` est vide actuellement

Verdict:

- utile pour PARTNER uniquement

## 14. `partner_tarif_rules`

Role:

- regles de tarification combinee PARTNER

Usage code:

- actif dans [backend/services/partner_tarif_resolver.py](/D:/EOS/backend/services/partner_tarif_resolver.py)
- actif dans [backend/routes/partner_admin.py](/D:/EOS/backend/routes/partner_admin.py)
- visible dans [frontend/src/components/PartnerTarifsAdmin.jsx](/D:/EOS/frontend/src/components/PartnerTarifsAdmin.jsx)

Champs utiles:

- `client_id`
- `tarif_lettre`
- `request_key`
- `amount`
- `created_at`
- `updated_at`

Verdict:

- utile uniquement pour PARTNER

## 15. `export_batches`

Role:

- trace les exports groupes et les archives d'export

Usage code:

- actif dans [backend/routes/export.py](/D:/EOS/backend/routes/export.py)
- actif dans [backend/services/partner_export_service.py](/D:/EOS/backend/services/partner_export_service.py)
- visible dans [frontend/src/components/ArchivesViewer.jsx](/D:/EOS/frontend/src/components/ArchivesViewer.jsx)

Champs utiles:

- `client_id`
- `filename`
- `filepath`
- `file_size`
- `enquete_count`
- `created_at`
- `utilisateur`
- `enquete_ids`

Verdict:

- utile si vous gardez l'historique des exports

## 16. `enquete_archive_files`

Role:

- stocke le fichier physique associe a une enquete archivee/exportee

Usage code:

- actif dans [backend/routes/archives.py](/D:/EOS/backend/routes/archives.py)
- references utilitaires dans [backend/scripts/reimport_archives.py](/D:/EOS/backend/scripts/reimport_archives.py)

Etat reel:

- 0 ligne

Champs utiles si la fonction archives est exploitee:

- `client_id`
- `enquete_id`
- `filename`
- `filepath`
- `type_export`
- `file_size`
- `created_at`
- `utilisateur`

Verdict:

- fonction existante dans le code
- optionnel dans votre usage actuel

## 17. `enquetes_terminees`

Role:

- garde la trace des enquetes confirmees par un directeur

Usage code:

- actif dans [backend/routes/enquetes.py](/D:/EOS/backend/routes/enquetes.py)
- references dans des scripts de controle

Etat reel:

- 0 ligne

Champs utiles:

- `donnee_id`
- `confirmed_at`
- `confirmed_by`

Verdict:

- workflow present mais non utilise dans les donnees actuelles
- table optionnelle selon votre processus reel

## 18. `confirmation_options`

Role:

- suggestions personnalisees pour le champ de confirmation/proximite

Usage code:

- lu/ecrit dans [backend/app.py](/D:/EOS/backend/app.py)
- utilise dans [frontend/src/components/UpdateModal.jsx](/D:/EOS/frontend/src/components/UpdateModal.jsx)

Point particulier:

- le code contient aussi un commentaire indiquant que la table peut etre absente selon certaines migrations
- dans votre base actuelle, elle existe mais elle est vide

Champs utiles:

- `client_id`
- `option_text`
- `usage_count`
- `created_at`
- `updated_at`

Verdict:

- option de confort, non indispensable au coeur metier

## 19. `sherlock_donnees`

Role:

- stockage specifique du format/import Sherlock

Usage code:

- utilise dans [backend/app.py](/D:/EOS/backend/app.py)
- mappe vers le frontend pour consultation/export

Etat reel:

- 1 ligne seulement

Verdict:

- support specialise
- pas central a votre usage actuel

## 20. `alembic_version`

Role:

- memorise la version de migration

Usage code:

- technique, par Alembic

Verdict:

- ne jamais supprimer si vous gardez les migrations

## Champs les plus utiles aujourd'hui

Si je dois reduire aux champs qui servent vraiment a faire tourner votre application au quotidien, ce sont surtout ceux-ci.

### Noyau dossier

- `donnees.id`
- `donnees.client_id`
- `donnees.fichier_id`
- `donnees.numeroDossier`
- `donnees.referenceDossier`
- `donnees.typeDemande`
- `donnees.nom`
- `donnees.prenom`
- `donnees.dateNaissance`
- `donnees.date_butoir`
- `donnees.statut_validation`
- `donnees.exported`
- `donnees.enqueteurId`
- `donnees.tarif_lettre`
- `donnees.recherche`

### Noyau retour enqueteur

- `donnees_enqueteur.donnee_id`
- `donnees_enqueteur.code_resultat`
- `donnees_enqueteur.elements_retrouves`
- `donnees_enqueteur.proximite`
- `donnees_enqueteur.date_retour`
- `donnees_enqueteur.adresse1`
- `donnees_enqueteur.code_postal`
- `donnees_enqueteur.ville`
- `donnees_enqueteur.telephone_personnel`
- `donnees_enqueteur.memo1`
- `donnees_enqueteur.memo2`
- `donnees_enqueteur.memo3`
- `donnees_enqueteur.notes_personnelles`

### Noyau facturation

- `enquete_facturation.donnee_id`
- `enquete_facturation.client_id`
- `enquete_facturation.tarif_eos_code`
- `enquete_facturation.resultat_eos_montant`
- `enquete_facturation.tarif_enqueteur_code`
- `enquete_facturation.resultat_enqueteur_montant`
- `enquete_facturation.paye`

## Champs probablement supprimables uniquement avec prudence

Je ne recommande pas de suppression immediate sans audit fonctionnel complementaire. En revanche, ces groupes paraissent candidats a simplification si vous voulez alleger la base et l'interface:

- bloc revenus de `donnees_enqueteur`
- bloc adresse employeur detaillee de `donnees_enqueteur`
- bloc bancaire detaille peu alimente de `donnees` et `donnees_enqueteur`
- bloc `sherlock_donnees` si le flux Sherlock est abandonne
- `confirmation_options` si vous n'utilisez pas les suggestions de proximite
- `enquete_archive_files` si vous n'utilisez pas le stockage de fichiers d'archives
- `enquetes_terminees` si vous ne passez jamais par la validation directeur

## Attention importante

- la documentation generee [documentation_base_de_donnees.md](/D:/EOS/documentation_base_de_donnees.md) mentionne `enquete_archives`, mais cette table n'existe pas dans la base reelle analysee
- le schema reel contient 20 tables, pas 21
- certaines tables sont possedees par `postgres` et d'autres par `eos_user`, signe que plusieurs comptes ont execute des scripts; ce n'est pas forcement grave, mais il faut surveiller les droits

## Synthese finale

- `eos_db` est la seule base metier EOS; `postgres` est normale et systeme.
- votre application s'appuie surtout sur `donnees`, `donnees_enqueteur`, `fichiers`, `clients`, `enqueteurs`, `imports` et `tarification`.
- les fonctions PARTNER sont bien presentes et partiellement alimentees.
- plusieurs champs existent pour des cas avances, mais beaucoup sont vides ou peu utilises dans vos donnees actuelles.
- les tables `confirmation_options`, `enquete_archive_files` et `enquetes_terminees` ne sont pas mortes dans le code, mais elles ne sont pas vraiment exploitees dans l'etat actuel de la base.

