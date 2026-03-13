#!/usr/bin/env python3
"""Generate a data dictionary from the live PostgreSQL schema."""

from __future__ import annotations

import csv
import os
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect


DEFAULT_DATABASE_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
ROOT_DIR = Path(__file__).resolve().parents[2]
CSV_OUTPUT = ROOT_DIR / "documentation_base_de_donnees.csv"
MD_OUTPUT = ROOT_DIR / "documentation_base_de_donnees.md"


TABLE_DESCRIPTIONS = {
    "alembic_version": "Table technique qui memorise la version de migration appliquee.",
    "clients": "Referentiel des clients de l'application EOS.",
    "confirmation_options": "Options de confirmation personnalisees proposees par client.",
    "donnees": "Table centrale des dossiers/enquetes importes depuis les fichiers source.",
    "donnees_enqueteur": "Reponses, corrections et informations terrain saisies par les enqueteurs.",
    "enquete_archive_files": "Fichiers physiques d'archives/export lies a une enquete.",
    "enquete_archives": "Historique logique des exportations d'enquetes.",
    "enquete_facturation": "Montants de facturation client et de remuneration enqueteur par enquete.",
    "enquetes_terminees": "Trace des enquetes confirmees/terminees.",
    "enqueteurs": "Referentiel des enqueteurs utilisateurs du systeme.",
    "export_batches": "Historique des exports groupes contenant plusieurs enquetes.",
    "fichiers": "Fichiers sources importes dans l'application.",
    "import_field_mappings": "Regles de mapping entre colonnes source et champs internes EOS.",
    "import_profiles": "Profils de parametrage d'import par client et type de fichier.",
    "partner_case_requests": "Demandes normalisees detectees par dossier pour le mode PARTNER.",
    "partner_request_keywords": "Mots-cles servant a detecter les demandes PARTNER dans le champ RECHERCHE.",
    "partner_tarif_rules": "Regles tarifaires PARTNER selon la lettre et la combinaison de demandes.",
    "sherlock_donnees": "Donnees importees depuis le format Sherlock, avec source et reponse enqueteur.",
    "tarifs_client": "Tarifs specifiques definis pour chaque client.",
    "tarifs_enqueteur": "Tarifs de remuneration des enqueteurs.",
    "tarifs_eos": "Tarifs factures par EOS au client final.",
}


COMMON_FIELD_DESCRIPTIONS = {
    "id": "Identifiant technique unique de la ligne.",
    "client_id": "Reference vers le client proprietaire de la donnee.",
    "fichier_id": "Reference vers le fichier source importe.",
    "donnee_id": "Reference vers l'enquete ou le dossier dans la table donnees.",
    "donnee_enqueteur_id": "Reference vers la reponse enqueteur liee.",
    "enquete_id": "Reference vers l'enquete concernee.",
    "enqueteurId": "Reference vers l'enqueteur affecte a l'enquete.",
    "enqueteur_id": "Reference vers l'enqueteur concerne.",
    "enquete_originale_id": "Reference vers l'enquete d'origine en cas de contestation.",
    "filename": "Nom du fichier stocke ou exporte.",
    "filepath": "Chemin de stockage du fichier sur disque.",
    "file_size": "Taille du fichier en octets.",
    "created_at": "Date et heure de creation de la ligne.",
    "updated_at": "Date et heure de derniere mise a jour.",
    "date_creation": "Date et heure de creation de la ligne.",
    "date_modification": "Date et heure de derniere modification.",
    "utilisateur": "Utilisateur ayant realise l'action.",
    "nom": "Nom ou libelle principal.",
    "prenom": "Prenom.",
    "email": "Adresse email.",
    "telephone": "Numero de telephone.",
    "code": "Code technique ou metier.",
    "description": "Description textuelle.",
    "montant": "Montant financier associe.",
    "date_debut": "Date de debut de validite.",
    "date_fin": "Date de fin de validite.",
    "actif": "Indique si l'element est actif.",
    "status": "Statut metier de la ligne.",
    "memo": "Commentaire ou justification libre.",
    "request_code": "Code normalise de la demande.",
    "request_key": "Cle composee representant une combinaison de demandes.",
    "amount": "Montant applique par une regle tarifaire.",
    "priority": "Priorite de traitement ou d'evaluation.",
    "pattern": "Mot-cle ou motif de detection.",
    "is_regex": "Indique si le motif est une expression reguliere.",
    "requested": "Indique si la demande a ete explicitement demandee.",
    "found": "Indique si l'information a ete trouvee.",
    "option_text": "Texte de l'option proposee a l'utilisateur.",
    "usage_count": "Nombre d'utilisations de l'option.",
    "confirmed_at": "Date et heure de confirmation.",
    "confirmed_by": "Utilisateur ayant confirme l'enquete.",
    "version_num": "Identifiant de revision Alembic appliquee.",
}


TABLE_FIELD_DESCRIPTIONS = {
    "clients": {
        "code": "Code unique du client dans EOS.",
        "nom": "Nom commercial ou metier du client.",
    },
    "fichiers": {
        "nom": "Nom du fichier importe.",
        "chemin": "Chemin d'origine ou de stockage du fichier.",
        "date_upload": "Date et heure d'import du fichier.",
    },
    "donnees": {
        "est_contestation": "Indique si le dossier est une contestation.",
        "date_contestation": "Date de creation ou reception de la contestation.",
        "motif_contestation_code": "Code normalise du motif de contestation.",
        "motif_contestation_detail": "Detail libre du motif de contestation.",
        "historique": "Historique JSON des evenements sur le dossier.",
        "statut_validation": "Statut courant du dossier dans le workflow de validation.",
        "numeroDossier": "Numero de dossier principal transmis par la source.",
        "referenceDossier": "Reference complementaire du dossier.",
        "numeroInterlocuteur": "Numero de l'interlocuteur cote source.",
        "guidInterlocuteur": "Identifiant GUID de l'interlocuteur.",
        "typeDemande": "Type de demande metier code sur 3 caracteres.",
        "numeroDemande": "Numero de demande principal.",
        "numeroDemandeContestee": "Numero de demande contestee, si applicable.",
        "numeroDemandeInitiale": "Numero de la demande initiale.",
        "forfaitDemande": "Code ou libelle du forfait de demande.",
        "dateRetourEspere": "Date de retour attendue pour l'enquete.",
        "qualite": "Civilite ou qualite declaree de la personne.",
        "dateNaissance": "Date de naissance declaree.",
        "lieuNaissance": "Lieu de naissance declare.",
        "codePostalNaissance": "Code postal du lieu de naissance.",
        "paysNaissance": "Pays de naissance.",
        "nomPatronymique": "Nom patronymique ou nom de naissance.",
        "dateNaissance_maj": "Date de naissance mise a jour.",
        "lieuNaissance_maj": "Lieu de naissance mis a jour.",
        "adresse1": "Adresse ligne 1.",
        "adresse2": "Adresse ligne 2.",
        "adresse3": "Adresse ligne 3.",
        "adresse4": "Adresse ligne 4.",
        "ville": "Ville de residence.",
        "codePostal": "Code postal de residence.",
        "paysResidence": "Pays de residence.",
        "telephonePersonnel": "Telephone personnel declare.",
        "telephoneEmployeur": "Telephone de l'employeur.",
        "telecopieEmployeur": "Fax de l'employeur.",
        "nomEmployeur": "Nom de l'employeur.",
        "banqueDomiciliation": "Banque de domiciliation.",
        "libelleGuichet": "Libelle du guichet bancaire.",
        "titulaireCompte": "Titulaire du compte bancaire.",
        "codeBanque": "Code banque.",
        "codeGuichet": "Code guichet.",
        "numeroCompte": "Numero de compte bancaire.",
        "ribCompte": "Cle ou suffixe RIB.",
        "datedenvoie": "Date d'envoi du dossier par la source.",
        "elementDemandes": "Codes des elements demandes.",
        "elementObligatoires": "Codes des elements obligatoires.",
        "elementContestes": "Codes des elements contestes.",
        "codeMotif": "Code du motif metier.",
        "motifDeContestation": "Motif textuel de contestation.",
        "cumulMontantsPrecedents": "Cumul des montants precedemment factures.",
        "codesociete": "Code societe ou entite source.",
        "urgence": "Indicateur d'urgence.",
        "commentaire": "Commentaire libre associe au dossier.",
        "date_butoir": "Date limite de traitement.",
        "exported": "Indique si l'enquete a deja ete exportee.",
        "exported_at": "Date et heure du dernier export.",
        "tarif_lettre": "Code tarifaire lettre applique au dossier.",
        "recherche": "Texte des recherches ou informations demandees.",
        "date_jour": "Date du jour reportee sur certains dossiers.",
        "nom_complet": "Nom complet consolide.",
        "motif": "Motif libre complementaire.",
        "instructions": "Instructions specifiques pour le traitement du dossier.",
    },
    "donnees_enqueteur": {
        "code_resultat": "Code resultat saisi par l'enqueteur.",
        "elements_retrouves": "Codes des elements retrouves par l'enqueteur.",
        "proximite": "Valeur de confirmation ou proximite selectionnee.",
        "flag_etat_civil_errone": "Marqueur signalant un etat civil errone.",
        "date_retour": "Date de retour de l'enquete.",
        "qualite_corrigee": "Qualite ou civilite corrigee.",
        "nom_corrige": "Nom corrige.",
        "prenom_corrige": "Prenom corrige.",
        "nom_patronymique_corrige": "Nom patronymique corrige.",
        "code_postal_naissance_corrige": "Code postal de naissance corrige.",
        "pays_naissance_corrige": "Pays de naissance corrige.",
        "type_divergence": "Type de divergence constate sur l'etat civil.",
        "telephone_chez_employeur": "Telephone joignable via l'employeur.",
        "date_deces": "Date de deces constatee.",
        "numero_acte_deces": "Numero d'acte de deces.",
        "code_insee_deces": "Code INSEE du lieu de deces.",
        "code_postal_deces": "Code postal du lieu de deces.",
        "localite_deces": "Localite du deces.",
        "commentaires_revenus": "Commentaires libres sur les revenus.",
        "montant_salaire": "Montant du salaire identifie.",
        "periode_versement_salaire": "Periode ou jour de versement du salaire.",
        "frequence_versement_salaire": "Frequence de versement du salaire.",
        "numero_facture": "Numero de facture.",
        "date_facture": "Date de facture.",
        "montant_facture": "Montant de facture.",
        "tarif_applique": "Tarif applique a la facturation.",
        "cumul_montants_precedents": "Cumul des montants precedemment factures.",
        "reprise_facturation": "Montant de reprise de facturation.",
        "remise_eventuelle": "Montant de remise eventuelle.",
        "memo1": "Memo court 1.",
        "memo2": "Memo court 2.",
        "memo3": "Memo court 3.",
        "memo4": "Memo court 4.",
        "memo5": "Memo long 5.",
        "notes_personnelles": "Notes personnelles de l'enqueteur.",
    },
    "enquete_archive_files": {
        "type_export": "Type de fichier exporte.",
    },
    "enquete_archives": {
        "date_export": "Date et heure de l'export.",
        "nom_fichier": "Nom du fichier exporte.",
    },
    "enquete_facturation": {
        "tarif_eos_code": "Code tarif EOS retenu pour la facturation client.",
        "tarif_eos_montant": "Montant de base du tarif EOS.",
        "resultat_eos_montant": "Montant EOS final apres ajustement.",
        "tarif_enqueteur_code": "Code tarif enqueteur retenu.",
        "tarif_enqueteur_montant": "Montant de base du tarif enqueteur.",
        "resultat_enqueteur_montant": "Montant final verse a l'enqueteur.",
        "paye": "Indique si le paiement a ete effectue.",
        "date_paiement": "Date de paiement de l'enqueteur.",
        "reference_paiement": "Reference du paiement.",
    },
    "export_batches": {
        "enquete_count": "Nombre d'enquetes incluses dans le batch.",
        "enquete_ids": "Liste des identifiants d'enquetes incluses.",
    },
    "import_profiles": {
        "name": "Nom du profil d'import.",
        "file_type": "Type de fichier supporte par le profil.",
        "sheet_name": "Nom de feuille Excel a lire.",
        "encoding": "Encodage du fichier source.",
    },
    "import_field_mappings": {
        "import_profile_id": "Reference vers le profil d'import.",
        "internal_field": "Nom du champ interne cible dans EOS.",
        "start_pos": "Position de debut dans un fichier texte fixe.",
        "length": "Longueur a extraire dans un fichier texte fixe.",
        "column_name": "Nom de colonne attendu dans un fichier Excel.",
        "column_index": "Index de colonne alternatif dans un fichier Excel.",
        "strip_whitespace": "Indique si les espaces doivent etre supprimes.",
        "default_value": "Valeur par defaut si la source est vide.",
        "is_required": "Indique si le champ est obligatoire.",
    },
    "partner_case_requests": {
        "requested": "Indique que la demande figure dans RECHERCHE.",
        "found": "Indique que la demande a ete satisfaite.",
    },
    "partner_request_keywords": {
        "pattern": "Mot-cle a rechercher dans RECHERCHE.",
    },
    "partner_tarif_rules": {
        "tarif_lettre": "Lettre tarifaire de reference.",
    },
    "sherlock_donnees": {
        "dossier_id": "Identifiant dossier venant de Sherlock.",
        "reference_interne": "Reference interne du dossier.",
        "demande": "Nature de la demande source.",
        "client_commentaire": "Commentaire fourni par le client dans Sherlock.",
        "tarif_a": "Valeur tarifaire A recopiee depuis Sherlock.",
        "tarif_at": "Valeur tarifaire AT recopiee depuis Sherlock.",
        "tarif_dcd": "Valeur tarifaire DCD recopiee depuis Sherlock.",
        "resultat": "Resultat retourne pour le dossier Sherlock.",
        "montant_ht": "Montant hors taxes calcule ou importe.",
    },
    "tarifs_client": {
        "code_lettre": "Code lettre du tarif client.",
    },
    "tarifs_enqueteur": {
        "code": "Code du tarif enqueteur.",
    },
    "tarifs_eos": {
        "code": "Code du tarif EOS.",
    },
}


ABBREVIATIONS = {
    "id": "ID",
    "guid": "GUID",
    "cp": "CP",
    "ht": "HT",
    "eos": "EOS",
    "at": "AT",
    "dcd": "DCD",
    "json": "JSON",
    "regex": "regex",
    "rib": "RIB",
    "insee": "INSEE",
    "vpn": "VPN",
}


def split_identifier(name: str) -> list[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    text = text.replace("_", " ")
    parts = [part for part in text.split() if part]
    return parts


def humanize(name: str) -> str:
    words = []
    for part in split_identifier(name):
        lowered = part.lower()
        words.append(ABBREVIATIONS.get(lowered, lowered))
    return " ".join(words)


def describe_field(table_name: str, field_name: str) -> str:
    table_specific = TABLE_FIELD_DESCRIPTIONS.get(table_name, {})
    if field_name in table_specific:
        return table_specific[field_name]
    if field_name in COMMON_FIELD_DESCRIPTIONS:
        return COMMON_FIELD_DESCRIPTIONS[field_name]

    if field_name.startswith("rep_ec_"):
        return f"Reponse enqueteur - etat civil - {humanize(field_name[7:])}."
    if field_name.startswith("rep_ad_"):
        return f"Reponse enqueteur - adresse/contact - {humanize(field_name[7:])}."
    if field_name.startswith("rep_dcd_"):
        return f"Reponse enqueteur - deces - {humanize(field_name[8:])}."
    if field_name.startswith("ec_"):
        return f"Donnee source etat civil - {humanize(field_name[3:])}."
    if field_name.startswith("ad_"):
        return f"Donnee source adresse/contact - {humanize(field_name[3:])}."
    if field_name.startswith("nature_revenu"):
        return f"Nature du revenu {field_name[-1]}."
    if field_name.startswith("montant_revenu"):
        return f"Montant du revenu {field_name[-1]}."
    if field_name.startswith("periode_versement_revenu"):
        return f"Periode de versement du revenu {field_name[-1]}."
    if field_name.startswith("frequence_versement_revenu"):
        return f"Frequence de versement du revenu {field_name[-1]}."
    if field_name.startswith("adresse") and field_name.endswith("_employeur"):
        suffix = field_name.replace("_employeur", "")
        return f"Ligne d'adresse employeur - {humanize(suffix)}."
    if field_name.endswith("_employeur"):
        return f"Information employeur - {humanize(field_name[:-10])}."
    if field_name.endswith("_corrige") or field_name.endswith("_corrigee"):
        base = re.sub(r"_corrigee?$", "", field_name)
        return f"Valeur corrigee pour {humanize(base)}."
    if field_name.endswith("_maj"):
        return f"Valeur mise a jour pour {humanize(field_name[:-4])}."
    if field_name.startswith("date_"):
        return f"Date liee a {humanize(field_name[5:])}."
    if field_name.startswith("numero_"):
        return f"Numero lie a {humanize(field_name[7:])}."
    if field_name.startswith("code_"):
        return f"Code lie a {humanize(field_name[5:])}."
    if field_name.startswith("montant_"):
        return f"Montant lie a {humanize(field_name[8:])}."
    if field_name.startswith("tarif_"):
        return f"Information tarifaire - {humanize(field_name[6:])}."
    if field_name.startswith("date"):
        return f"Date de {humanize(field_name[4:])}."
    if field_name.startswith("numero"):
        return f"Numero de {humanize(field_name[6:])}."
    if field_name.startswith("code"):
        return f"Code de {humanize(field_name[4:])}."

    return f"Champ correspondant a {humanize(field_name)}."


def table_description(table_name: str) -> str:
    return TABLE_DESCRIPTIONS.get(table_name, f"Table metier ou technique nommee {table_name}.")


def format_type(column_type: object) -> str:
    return re.sub(r"\s+", " ", str(column_type).upper())


def format_size(column_type: object) -> str:
    length = getattr(column_type, "length", None)
    precision = getattr(column_type, "precision", None)
    scale = getattr(column_type, "scale", None)

    if length:
        return str(length)
    if precision is not None:
        if scale is not None:
            return f"{precision},{scale}"
        return str(precision)
    return "-"


def build_metadata(inspector, table_name: str) -> dict:
    pk_columns = set(inspector.get_pk_constraint(table_name).get("constrained_columns") or [])

    fk_map = {}
    for fk in inspector.get_foreign_keys(table_name):
        referred_table = fk.get("referred_table")
        referred_columns = fk.get("referred_columns") or []
        constrained_columns = fk.get("constrained_columns") or []
        for idx, column_name in enumerate(constrained_columns):
            target_column = referred_columns[idx] if idx < len(referred_columns) else "id"
            fk_map[column_name] = f"{referred_table}.{target_column}"

    unique_single = set()
    unique_composite = set()
    for unique in inspector.get_unique_constraints(table_name):
        columns = unique.get("column_names") or []
        if len(columns) == 1:
            unique_single.add(columns[0])
        elif len(columns) > 1:
            unique_composite.update(columns)

    indexed_single = set()
    indexed_composite = set()
    for index in inspector.get_indexes(table_name):
        columns = index.get("column_names") or []
        is_unique_index = bool(index.get("unique"))

        if is_unique_index:
            if len(columns) == 1:
                unique_single.add(columns[0])
            elif len(columns) > 1:
                unique_composite.update(columns)

        if len(columns) == 1:
            indexed_single.add(columns[0])
        elif len(columns) > 1:
            indexed_composite.update(columns)

    return {
        "pk_columns": pk_columns,
        "fk_map": fk_map,
        "unique_single": unique_single,
        "unique_composite": unique_composite,
        "indexed_single": indexed_single,
        "indexed_composite": indexed_composite,
    }


def characteristics_for(column: dict, metadata: dict) -> tuple[str, str, str, str, str]:
    name = column["name"]
    details = []

    pk = "oui" if name in metadata["pk_columns"] else "non"
    fk = metadata["fk_map"].get(name, "")

    if pk == "oui":
        details.append("PK")
    if fk:
        details.append(f"FK -> {fk}")

    nullable = "oui" if column.get("nullable", True) else "non"
    details.append("NULL autorise" if nullable == "oui" else "NOT NULL")

    if name in metadata["unique_single"]:
        unique = "oui"
        details.append("UNIQUE")
    elif name in metadata["unique_composite"]:
        unique = "composite"
        details.append("UNIQUE composite")
    else:
        unique = "non"

    default = column.get("default")
    default_text = str(default) if default is not None else ""
    if default_text:
        details.append(f"DEFAULT {default_text}")

    if name in metadata["indexed_single"]:
        details.append("INDEX")
        indexed = "oui"
    elif name in metadata["indexed_composite"]:
        details.append("INDEX composite")
        indexed = "composite"
    else:
        indexed = "non"

    return " | ".join(details), pk, fk, unique, indexed


def collect_rows():
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = create_engine(database_url)
    inspector = inspect(engine)

    rows = []
    table_summaries = []
    table_names = sorted(inspector.get_table_names())

    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        metadata = build_metadata(inspector, table_name)
        table_desc = table_description(table_name)
        table_summaries.append(
            {
                "table_name": table_name,
                "table_description": table_desc,
                "column_count": len(columns),
            }
        )

        for column in columns:
            characteristics, pk, fk, unique, indexed = characteristics_for(column, metadata)
            rows.append(
                {
                    "table_name": table_name,
                    "table_description": table_desc,
                    "field_name": column["name"],
                    "field_description": describe_field(table_name, column["name"]),
                    "sql_type": format_type(column["type"]),
                    "size": format_size(column["type"]),
                    "nullable": "oui" if column.get("nullable", True) else "non",
                    "primary_key": pk,
                    "foreign_key": fk,
                    "unique": unique,
                    "indexed": indexed,
                    "default": "" if column.get("default") is None else str(column["default"]),
                    "characteristics": characteristics,
                }
            )

    return table_summaries, rows


def write_csv(rows: list[dict]) -> None:
    fieldnames = [
        "table_name",
        "table_description",
        "field_name",
        "field_description",
        "sql_type",
        "size",
        "nullable",
        "primary_key",
        "foreign_key",
        "unique",
        "indexed",
        "default",
        "characteristics",
    ]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(table_summaries: list[dict], rows: list[dict]) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Documentation base de donnees EOS",
        "",
        f"Genere le {generated_at} a partir du schema PostgreSQL courant.",
        "",
        "## Resume",
        "",
        f"- Nombre de tables documentees : {len(table_summaries)}",
        f"- Nombre total de champs documentes : {len(rows)}",
        f"- Fichier tabulaire associe : `{CSV_OUTPUT.name}`",
        "",
        "## Tables",
        "",
        "| Table | Description | Nb champs |",
        "| --- | --- | ---: |",
    ]

    for summary in table_summaries:
        lines.append(
            f"| `{summary['table_name']}` | {summary['table_description']} | {summary['column_count']} |"
        )

    for summary in table_summaries:
        table_rows = [row for row in rows if row["table_name"] == summary["table_name"]]
        lines.extend(
            [
                "",
                f"## {summary['table_name']}",
                "",
                summary["table_description"],
                "",
                "| Champ | Type SQL | Grandeur | Caracteristiques | Explication |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in table_rows:
            explanation = row["field_description"].replace("\n", " ").replace("|", "/")
            characteristics = row["characteristics"].replace("|", "/")
            lines.append(
                f"| `{row['field_name']}` | `{row['sql_type']}` | {row['size']} | {characteristics} | {explanation} |"
            )

    MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    table_summaries, rows = collect_rows()
    write_csv(rows)
    write_markdown(table_summaries, rows)
    print(f"CSV genere : {CSV_OUTPUT}")
    print(f"Markdown genere : {MD_OUTPUT}")
    print(f"Tables : {len(table_summaries)}")
    print(f"Champs : {len(rows)}")


if __name__ == "__main__":
    main()
