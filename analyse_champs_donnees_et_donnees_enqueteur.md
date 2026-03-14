# Analyse des champs `donnees` et `donnees_enqueteur`

Date d'analyse: 2026-03-14

## Legende

- `Utilise par le code`
  - `Oui`: references claires dans backend/frontend
  - `Partiel`: supporte par le code mais peu central
  - `Non/Quasi non`: tres peu ou pas de reference utile hors modeles/migrations
- `Rempli en base`
  - `Oui`: taux de remplissage significatif
  - `Partiel`: rempli mais faible
  - `Non`: quasiment vide
- `Recommendation`
  - `Garder`
  - `A revoir`
  - `Dormant`

## Table `donnees`

| Champ | Utilise par le code | Rempli en base | Recommendation |
| --- | --- | --- | --- |
| `id` | Oui | Oui | Garder |
| `client_id` | Oui | Oui | Garder |
| `fichier_id` | Oui | Oui | Garder |
| `enqueteurId` | Oui | Non | Garder |
| `enquete_originale_id` | Oui | Non | Garder |
| `est_contestation` | Oui | Oui | Garder |
| `date_contestation` | Oui | Non | A revoir |
| `motif_contestation_code` | Oui | Non | A revoir |
| `motif_contestation_detail` | Oui | Non | A revoir |
| `historique` | Oui | Non | A revoir |
| `statut_validation` | Oui | Oui | Garder |
| `numeroDossier` | Oui | Oui | Garder |
| `referenceDossier` | Oui | Oui | Garder |
| `numeroInterlocuteur` | Partiel | Oui | A revoir |
| `guidInterlocuteur` | Partiel | Oui | A revoir |
| `typeDemande` | Oui | Oui | Garder |
| `numeroDemande` | Partiel | Partiel | A revoir |
| `numeroDemandeContestee` | Partiel | Partiel | A revoir |
| `numeroDemandeInitiale` | Partiel | Partiel | A revoir |
| `forfaitDemande` | Partiel | Oui | A revoir |
| `dateRetourEspere` | Partiel | Oui | A revoir |
| `qualite` | Oui | Oui | Garder |
| `nom` | Oui | Oui | Garder |
| `prenom` | Oui | Oui | Garder |
| `dateNaissance` | Oui | Oui | Garder |
| `lieuNaissance` | Oui | Oui | Garder |
| `codePostalNaissance` | Partiel | Oui | A revoir |
| `paysNaissance` | Partiel | Oui | A revoir |
| `nomPatronymique` | Oui | Oui | Garder |
| `dateNaissance_maj` | Oui | Non | A revoir |
| `lieuNaissance_maj` | Oui | Non | A revoir |
| `adresse1` | Oui | Oui | Garder |
| `adresse2` | Partiel | Partiel | A revoir |
| `adresse3` | Partiel | Partiel | A revoir |
| `adresse4` | Partiel | Partiel | A revoir |
| `ville` | Oui | Oui | Garder |
| `codePostal` | Oui | Oui | Garder |
| `paysResidence` | Partiel | Partiel | A revoir |
| `telephonePersonnel` | Oui | Oui | Garder |
| `telephoneEmployeur` | Partiel | Partiel | A revoir |
| `telecopieEmployeur` | Partiel | Partiel | A revoir |
| `nomEmployeur` | Partiel | Partiel | A revoir |
| `banqueDomiciliation` | Partiel | Partiel | A revoir |
| `libelleGuichet` | Partiel | Partiel | A revoir |
| `titulaireCompte` | Partiel | Partiel | A revoir |
| `codeBanque` | Partiel | Partiel | A revoir |
| `codeGuichet` | Partiel | Partiel | A revoir |
| `numeroCompte` | Partiel | Partiel | A revoir |
| `ribCompte` | Partiel | Partiel | A revoir |
| `datedenvoie` | Partiel | Oui | A revoir |
| `elementDemandes` | Oui | Partiel | Garder |
| `elementObligatoires` | Partiel | Partiel | A revoir |
| `elementContestes` | Partiel | Partiel | A revoir |
| `codeMotif` | Partiel | Partiel | A revoir |
| `motifDeContestation` | Partiel | Partiel | A revoir |
| `cumulMontantsPrecedents` | Partiel | Non | A revoir |
| `codesociete` | Partiel | Partiel | A revoir |
| `urgence` | Partiel | Partiel | A revoir |
| `commentaire` | Partiel | Partiel | A revoir |
| `date_butoir` | Oui | Oui | Garder |
| `exported` | Oui | Oui | Garder |
| `exported_at` | Oui | Oui | Garder |
| `tarif_lettre` | Oui | Oui | Garder |
| `recherche` | Oui | Oui | Garder |
| `instructions` | Oui | Oui | Garder |
| `date_jour` | Partiel | Non | A revoir |
| `nom_complet` | Oui | Partiel | A revoir |
| `motif` | Oui | Non | A revoir |
| `created_at` | Oui | Oui | Garder |
| `updated_at` | Oui | Oui | Garder |

## Table `donnees_enqueteur`

| Champ | Utilise par le code | Rempli en base | Recommendation |
| --- | --- | --- | --- |
| `id` | Oui | Oui | Garder |
| `client_id` | Oui | Oui | Garder |
| `donnee_id` | Oui | Oui | Garder |
| `code_resultat` | Oui | Oui | Garder |
| `elements_retrouves` | Oui | Partiel | Garder |
| `proximite` | Oui | Partiel | Garder |
| `flag_etat_civil_errone` | Oui | Non | A revoir |
| `date_retour` | Oui | Oui | Garder |
| `qualite_corrigee` | Oui | Non | A revoir |
| `nom_corrige` | Oui | Non | A revoir |
| `prenom_corrige` | Oui | Non | A revoir |
| `nom_patronymique_corrige` | Partiel | Non | Dormant |
| `code_postal_naissance_corrige` | Partiel | Non | Dormant |
| `pays_naissance_corrige` | Partiel | Non | Dormant |
| `type_divergence` | Oui | Non | A revoir |
| `adresse1` | Oui | Oui | Garder |
| `adresse2` | Oui | Oui | Garder |
| `adresse3` | Oui | Oui | Garder |
| `adresse4` | Oui | Partiel | A revoir |
| `code_postal` | Oui | Oui | Garder |
| `ville` | Oui | Oui | Garder |
| `pays_residence` | Oui | Partiel | A revoir |
| `telephone_personnel` | Oui | Oui | Garder |
| `telephone_chez_employeur` | Oui | Partiel | A revoir |
| `nom_employeur` | Oui | Partiel | A revoir |
| `telephone_employeur` | Oui | Partiel | A revoir |
| `telecopie_employeur` | Oui | Partiel | A revoir |
| `adresse1_employeur` | Partiel | Non | Dormant |
| `adresse2_employeur` | Partiel | Non | Dormant |
| `adresse3_employeur` | Partiel | Non | Dormant |
| `adresse4_employeur` | Partiel | Non | Dormant |
| `code_postal_employeur` | Partiel | Non | Dormant |
| `ville_employeur` | Partiel | Non | Dormant |
| `pays_employeur` | Partiel | Non | Dormant |
| `banque_domiciliation` | Oui | Partiel | A revoir |
| `libelle_guichet` | Oui | Non | Dormant |
| `titulaire_compte` | Oui | Non | Dormant |
| `code_banque` | Oui | Partiel | A revoir |
| `code_guichet` | Oui | Partiel | A revoir |
| `date_deces` | Oui | Partiel | A revoir |
| `numero_acte_deces` | Oui | Non | A revoir |
| `code_insee_deces` | Oui | Partiel | A revoir |
| `code_postal_deces` | Oui | Partiel | A revoir |
| `localite_deces` | Oui | Partiel | A revoir |
| `commentaires_revenus` | Partiel | Non | Dormant |
| `montant_salaire` | Partiel | Non | Dormant |
| `periode_versement_salaire` | Partiel | Non | Dormant |
| `frequence_versement_salaire` | Partiel | Non | Dormant |
| `nature_revenu1` | Partiel | Non | Dormant |
| `montant_revenu1` | Partiel | Non | Dormant |
| `periode_versement_revenu1` | Partiel | Non | Dormant |
| `frequence_versement_revenu1` | Partiel | Non | Dormant |
| `nature_revenu2` | Partiel | Non | Dormant |
| `montant_revenu2` | Partiel | Non | Dormant |
| `periode_versement_revenu2` | Partiel | Non | Dormant |
| `frequence_versement_revenu2` | Partiel | Non | Dormant |
| `nature_revenu3` | Partiel | Non | Dormant |
| `montant_revenu3` | Partiel | Non | Dormant |
| `periode_versement_revenu3` | Partiel | Non | Dormant |
| `frequence_versement_revenu3` | Partiel | Non | Dormant |
| `numero_facture` | Oui | Non | A revoir |
| `date_facture` | Oui | Partiel | Garder |
| `montant_facture` | Oui | Oui | Garder |
| `tarif_applique` | Oui | Oui | Garder |
| `cumul_montants_precedents` | Oui | Oui | Garder |
| `reprise_facturation` | Oui | Oui | Garder |
| `remise_eventuelle` | Oui | Oui | Garder |
| `memo1` | Oui | Partiel | Garder |
| `memo2` | Oui | Partiel | A revoir |
| `memo3` | Oui | Partiel | Garder |
| `memo4` | Oui | Non | Dormant |
| `memo5` | Oui | Non | Dormant |
| `notes_personnelles` | Oui | Partiel | Garder |
| `created_at` | Oui | Oui | Garder |
| `updated_at` | Oui | Oui | Garder |

## Resume simple

### Dans `donnees`, les champs a garder sans hesiter

- identifiants et liaisons: `id`, `client_id`, `fichier_id`
- coeur dossier: `numeroDossier`, `referenceDossier`, `typeDemande`, `nom`, `prenom`, `dateNaissance`
- workflow: `enqueteurId`, `statut_validation`, `date_butoir`, `exported`, `exported_at`
- logique PARTNER/export: `tarif_lettre`, `recherche`, `instructions`
- contestation/support: `est_contestation`, `enquete_originale_id`
- audit: `created_at`, `updated_at`

### Dans `donnees_enqueteur`, les champs a garder sans hesiter

- coeur resultat: `donnee_id`, `code_resultat`, `elements_retrouves`, `proximite`, `date_retour`
- adresse: `adresse1`, `adresse2`, `adresse3`, `code_postal`, `ville`
- contact: `telephone_personnel`
- facturation: `montant_facture`, `tarif_applique`, `cumul_montants_precedents`, `reprise_facturation`, `remise_eventuelle`, `date_facture`
- memos utiles: `memo1`, `memo3`, `notes_personnelles`
- audit: `created_at`, `updated_at`

### Champs probablement dormants aujourd'hui

Dans `donnees`:

- peu de vrais candidats totalement dormants, mais plusieurs champs sont faibles et a revoir plutot qu'a supprimer

Dans `donnees_enqueteur`:

- bloc adresses employeur detaillees
- bloc revenus complet
- `memo4`
- `memo5`
- `nom_patronymique_corrige`
- `code_postal_naissance_corrige`
- `pays_naissance_corrige`
- `libelle_guichet`
- `titulaire_compte`

## Prudence

Un champ `Dormant` ne veut pas dire `supprimable tout de suite`.

Avant suppression, il faut verifier:

- s'il apparait dans des exports clients
- s'il sert dans des imports historiques
- s'il est attendu par un utilisateur metier meme rarement
- s'il est requis par un script manuel hors application

