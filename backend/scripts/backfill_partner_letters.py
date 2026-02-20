#!/usr/bin/env python3
"""
Backfill PARTNER letter fields:
- donnees.elementDemandes
- donnees_enqueteur.elements_retrouves

By default runs in dry-run mode.
Use --apply to persist updates.
"""

import argparse
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask

from models import Client, Donnee, DonneeEnqueteur, db

try:
    from models.partner_models import PartnerCaseRequest
except Exception:
    PartnerCaseRequest = None


DEFAULT_DB_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"


def clean_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return ""
    return text


def has_value(value):
    return bool(clean_text(value))


def normalize_token(value):
    text = clean_text(value)
    if not text:
        return ""
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn"
    )
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def infer_element_demandes_from_recherche(recherche_value):
    token = normalize_token(recherche_value)
    if not token:
        return ""

    markers = {
        "A": ("ADRESSE", "DOMICILE", "ADR"),
        "T": ("TELEPHONE", "TEL", "MOBILE", "PORTABLE"),
        "B": ("BANQUE", "RIB", "IBAN", "COMPTE", "GUICHET"),
        "E": ("EMPLOYEUR", "TRAVAIL", "SOCIETE"),
        "R": ("REVENU", "SALAIRE", "PAIE", "INCOME"),
        "D": ("DECES", "DECEDE", "MORT", "DEATH"),
    }

    if any(normalize_token(marker) in token for marker in markers["D"]):
        return "D"

    letters = []
    for letter in ["A", "T", "B", "E", "R"]:
        if any(normalize_token(marker) in token for marker in markers[letter]):
            letters.append(letter)
    return "".join(letters)


def compute_elements_retrouves_from_enqueteur(de):
    has_adresse = any(
        has_value(getattr(de, field))
        for field in ["adresse1", "adresse2", "adresse3", "adresse4", "code_postal", "ville", "pays_residence"]
    )
    has_telephone = any(
        has_value(getattr(de, field)) for field in ["telephone_personnel", "telephone_chez_employeur"]
    )
    has_banque = any(
        has_value(getattr(de, field))
        for field in ["banque_domiciliation", "libelle_guichet", "titulaire_compte", "code_banque", "code_guichet"]
    )
    has_employeur = any(
        has_value(getattr(de, field))
        for field in [
            "nom_employeur",
            "telephone_employeur",
            "telecopie_employeur",
            "adresse1_employeur",
            "adresse2_employeur",
            "adresse3_employeur",
            "adresse4_employeur",
            "code_postal_employeur",
            "ville_employeur",
            "pays_employeur",
        ]
    )
    has_revenus = any(
        has_value(getattr(de, field))
        for field in [
            "commentaires_revenus",
            "montant_salaire",
            "nature_revenu1",
            "montant_revenu1",
            "nature_revenu2",
            "montant_revenu2",
            "nature_revenu3",
            "montant_revenu3",
        ]
    )
    has_deces = any(
        has_value(getattr(de, field))
        for field in ["date_deces", "numero_acte_deces", "code_insee_deces", "code_postal_deces", "localite_deces"]
    )

    if has_deces:
        return "D"

    letters = []
    if has_adresse:
        letters.append("A")
    if has_telephone:
        letters.append("T")
    if has_banque:
        letters.append("B")
    if has_employeur:
        letters.append("E")
    if has_revenus:
        letters.append("R")
    return "".join(letters)


REQUEST_TO_LETTER = {
    "ADDRESS": "A",
    "PHONE": "T",
    "BANK": "B",
    "EMPLOYER": "E",
    "REVENUE": "R",
    "INCOME": "R",
    "DEATH": "D",
    "DECES": "D",
}


def letters_from_request_codes(codes):
    if not codes:
        return ""
    mapped = []
    for code in codes:
        letter = REQUEST_TO_LETTER.get(clean_text(code).upper())
        if letter:
            mapped.append(letter)
    if "D" in mapped:
        return "D"
    ordered = []
    for letter in ["A", "T", "B", "E", "R"]:
        if letter in mapped:
            ordered.append(letter)
    return "".join(ordered)


def build_partner_requests_maps(client_id):
    requested_map = defaultdict(set)
    found_map = defaultdict(set)

    if PartnerCaseRequest is None:
        return requested_map, found_map

    rows = (
        db.session.query(
            PartnerCaseRequest.donnee_id,
            PartnerCaseRequest.request_code,
            PartnerCaseRequest.requested,
            PartnerCaseRequest.found,
            PartnerCaseRequest.status,
        )
        .join(Donnee, Donnee.id == PartnerCaseRequest.donnee_id)
        .filter(Donnee.client_id == client_id)
        .all()
    )

    for donnee_id, request_code, requested, found, status in rows:
        code = clean_text(request_code).upper()
        if not code:
            continue
        if requested:
            requested_map[donnee_id].add(code)
        if found or clean_text(status).upper() == "POS":
            found_map[donnee_id].add(code)

    return requested_map, found_map


def run_backfill(client_code="PARTNER", apply=False, limit=0):
    client = Client.query.filter_by(code=client_code).first()
    if not client:
        raise RuntimeError(f"Client {client_code} introuvable")

    print(f"Client: {client.code} (id={client.id})")
    print(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")

    requested_map, found_map = build_partner_requests_maps(client.id)

    donnee_updates = 0
    de_updates = 0
    scanned_donnees = 0
    scanned_de = 0
    donnee_sources = Counter()
    de_sources = Counter()
    original_cache = {}

    donnees_query = Donnee.query.filter(Donnee.client_id == client.id).order_by(Donnee.id.asc())
    if limit and limit > 0:
        donnees_query = donnees_query.limit(limit)

    for donnee in donnees_query:
        scanned_donnees += 1
        if has_value(donnee.elementDemandes):
            continue

        inferred = ""
        source = ""

        if donnee.est_contestation and donnee.enquete_originale_id:
            original = original_cache.get(donnee.enquete_originale_id)
            if original is None:
                original = db.session.get(Donnee, donnee.enquete_originale_id)
                original_cache[donnee.enquete_originale_id] = original
            if original:
                inferred = clean_text(original.elementDemandes)
                source = "linked_original"

        if not inferred:
            inferred = infer_element_demandes_from_recherche(donnee.recherche)
            source = "recherche"

        if not inferred:
            inferred = letters_from_request_codes(requested_map.get(donnee.id, set()))
            source = "partner_requests"

        if inferred:
            donnee.elementDemandes = inferred[:10]
            donnee_updates += 1
            donnee_sources[source] += 1

    de_query = (
        DonneeEnqueteur.query.join(Donnee, Donnee.id == DonneeEnqueteur.donnee_id)
        .filter(Donnee.client_id == client.id)
        .order_by(DonneeEnqueteur.id.asc())
    )
    if limit and limit > 0:
        de_query = de_query.limit(limit)

    for de in de_query:
        scanned_de += 1
        if has_value(de.elements_retrouves):
            continue

        inferred = compute_elements_retrouves_from_enqueteur(de)
        source = "enqueteur_fields"
        if not inferred:
            inferred = letters_from_request_codes(found_map.get(de.donnee_id, set()))
            source = "partner_requests"

        if inferred:
            de.elements_retrouves = inferred[:10]
            de_updates += 1
            de_sources[source] += 1

    total_updates = donnee_updates + de_updates
    if apply:
        db.session.commit()
    else:
        db.session.rollback()

    print("")
    print("Resume:")
    print(f"- Donnees scannees: {scanned_donnees}")
    print(f"- DonneesEnqueteur scannees: {scanned_de}")
    print(f"- elementDemandes remplis: {donnee_updates} ({dict(donnee_sources)})")
    print(f"- elements_retrouves remplis: {de_updates} ({dict(de_sources)})")
    print(f"- Total updates: {total_updates}")


def main():
    parser = argparse.ArgumentParser(description="Backfill PARTNER letters in DB")
    parser.add_argument("--client-code", default="PARTNER", help="Client code to process (default: PARTNER)")
    parser.add_argument("--apply", action="store_true", help="Persist updates")
    parser.add_argument("--limit", type=int, default=0, help="Optional max rows per table")
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
    os.environ["DATABASE_URL"] = db_url

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        run_backfill(client_code=args.client_code, apply=args.apply, limit=args.limit)


if __name__ == "__main__":
    main()
