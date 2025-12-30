#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden Test - Export "Réponses EOS"

Compare une ligne générée avec la ligne exemple fournie.
Ce test garantit que le formatage est EXACTEMENT conforme à l'exemple réel.
"""

import pytest
import datetime
from unittest.mock import Mock
from routes.export import generate_eos_export_line

# ===== LIGNE EXEMPLE (GOLDEN MASTER) =====
EXAMPLE_LINE = "8293043   50839992349001 D-8293043   a924673a-fd45-4b7f-a88a-af41f95afa01ENQ                                 LDM             27/12/2025M         CUMBO                         CYRIL               14/07/1976MARSEILLE                                         13        FRANCE                                                        24/12/2025PA                   31/12/2025   24.00   24.00    0.00       0       0                                                                                                                                   112 ALLEE VAL FLEURI BOULOURIS                                  83700     ST RAPHAEL                      FRANCE                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               "


def test_golden_line_length():
    """Vérifie que la ligne exemple fait exactement 2618 caractères (sans CRLF)"""
    assert len(EXAMPLE_LINE) == 2618, f"Ligne exemple devrait faire 2618 chars, mais fait {len(EXAMPLE_LINE)}"


def test_generate_line_vs_golden():
    """
    Golden Test: Compare ligne générée vs ligne exemple.

    Crée un mock Donnee/DonneeEnqueteur à partir de la ligne exemple,
    génère une nouvelle ligne, et vérifie l'égalité EXACTE.
    """
    # ===== PARSER LA LIGNE EXEMPLE =====
    pos = 0

    # Fonction helper pour extraire un champ
    def extract(width):
        nonlocal pos
        value = EXAMPLE_LINE[pos:pos+width]
        pos += width
        return value.strip()  # Strip pour obtenir la valeur sans padding

    # Extraire les champs (même ordre que dans generate_eos_export_line)
    numeroDossier = extract(10)  # "8293043"
    referenceDossier = extract(15)  # "50839992349001"
    numeroInterlocuteur = extract(12)  # "D-8293043"
    guidInterlocuteur = extract(36)  # "a924673a-fd45-4b7f-a88a-af41f95afa01"
    typeDemande = extract(3)  # "ENQ"
    numeroDemande = extract(11)  # vide
    numeroDemandeContestee = extract(11)  # vide
    numeroDemandeInitiale = extract(11)  # vide
    forfaitDemande = extract(16)  # "LDM"
    dateRetourEspere_str = extract(10)  # "27/12/2025"

    qualite = extract(10)  # "M"
    nom = extract(30)  # "CUMBO"
    prenom = extract(20)  # "CYRIL"
    dateNaissance_str = extract(10)  # "14/07/1976"
    lieuNaissance = extract(50)  # "MARSEILLE"
    codePostalNaissance = extract(10)  # "13"
    paysNaissance = extract(32)  # "FRANCE"
    nomPatronymique = extract(30)  # vide

    dateRetour_str = extract(10)  # "24/12/2025"
    codeResultat = extract(1)  # "P"
    elementsRetrouves = extract(10)  # "A"
    flagEtatCivilErrone = extract(1)  # vide

    numeroFacture = extract(9)  # vide
    dateFacture_str = extract(10)  # "31/12/2025"
    montantFacture_str = extract(8)  # "   24.00"
    tarifApplique_str = extract(8)  # "   24.00"
    cumulMontantsPrecedents_str = extract(8)  # "    0.00"
    repriseFacturation_str = extract(8)  # "       0"
    remiseEventuelle_str = extract(8)  # "       0"

    # Décès (67) - tous vides dans l'exemple
    pos += 67

    # Adresse (202)
    adresse1 = extract(32)  # "112 ALLEE VAL FLEURI BOULOURIS"
    adresse2 = extract(32)  # vide
    adresse3 = extract(32)  # vide
    adresse4 = extract(32)  # vide
    codePostal = extract(10)  # "83700"
    ville = extract(32)  # "ST RAPHAEL"
    paysResidence = extract(32)  # "FRANCE"

    # Téléphones (30) - vides
    pos += 30

    # Employeur (264) - tous vides
    pos += 264

    # Banque (117) - tous vides
    pos += 117

    # Revenus (274) - tous vides
    pos += 274

    # Mémos (1256) - tous vides
    pos += 1256

    # ===== CRÉER MOCKS AVEC CES VALEURS =====
    donnee = Mock()
    donnee.id = 1
    donnee.numeroDossier = numeroDossier
    donnee.referenceDossier = referenceDossier
    donnee.numeroInterlocuteur = numeroInterlocuteur
    donnee.guidInterlocuteur = guidInterlocuteur
    donnee.typeDemande = typeDemande
    donnee.numeroDemande = numeroDemande or " "  # Au moins un espace pour validation
    donnee.forfaitDemande = forfaitDemande
    donnee.dateRetourEspere = datetime.datetime.strptime(dateRetourEspere_str, '%d/%m/%Y').date()

    donnee.qualite = qualite
    donnee.nom = nom
    donnee.prenom = prenom
    donnee.dateNaissance = datetime.datetime.strptime(dateNaissance_str, '%d/%m/%Y').date()
    donnee.lieuNaissance = lieuNaissance
    donnee.codePostalNaissance = codePostalNaissance
    donnee.paysNaissance = paysNaissance
    donnee.nomPatronymique = nomPatronymique or ""

    donnee_enqueteur = Mock()
    donnee_enqueteur.code_resultat = codeResultat
    donnee_enqueteur.elements_retrouves = elementsRetrouves

    # Pas de corrections (utilise valeurs d)
    donnee_enqueteur.qualite_corrigee = None
    donnee_enqueteur.nom_corrige = None
    donnee_enqueteur.prenom_corrige = None
    donnee_enqueteur.code_postal_naissance_corrige = None
    donnee_enqueteur.pays_naissance_corrige = None
    donnee_enqueteur.nom_patronymique_corrige = None

    # Date retour
    donnee_enqueteur.date_retour = datetime.datetime.strptime(dateRetour_str, '%d/%m/%Y').date()

    # Flag état civil
    donnee_enqueteur.flag_etat_civil_errone = flagEtatCivilErrone or None

    # Facturation
    donnee_enqueteur.numero_facture = numeroFacture or None
    donnee_enqueteur.date_facture = datetime.datetime.strptime(dateFacture_str, '%d/%m/%Y').date() if dateFacture_str.strip() else None
    donnee_enqueteur.montant_facture = float(montantFacture_str.strip()) if montantFacture_str.strip() else None
    donnee_enqueteur.tarif_applique = float(tarifApplique_str.strip()) if tarifApplique_str.strip() else None
    donnee_enqueteur.cumul_montants_precedents = float(cumulMontantsPrecedents_str.strip()) if cumulMontantsPrecedents_str.strip() else None
    donnee_enqueteur.reprise_facturation = float(repriseFacturation_str.strip()) if repriseFacturation_str.strip() and repriseFacturation_str.strip() != '0' else None
    donnee_enqueteur.remise_eventuelle = float(remiseEventuelle_str.strip()) if remiseEventuelle_str.strip() and remiseEventuelle_str.strip() != '0' else None

    # Décès - tous None
    donnee_enqueteur.date_deces = None
    donnee_enqueteur.numero_acte_deces = None
    donnee_enqueteur.code_insee_deces = None
    donnee_enqueteur.code_postal_deces = None
    donnee_enqueteur.localite_deces = None

    # Adresse
    donnee_enqueteur.adresse1 = adresse1
    donnee_enqueteur.adresse2 = adresse2 or None
    donnee_enqueteur.adresse3 = adresse3 or None
    donnee_enqueteur.adresse4 = adresse4 or None
    donnee_enqueteur.code_postal = codePostal
    donnee_enqueteur.ville = ville
    donnee_enqueteur.pays_residence = paysResidence

    # Téléphones - None
    donnee_enqueteur.telephone_personnel = None
    donnee_enqueteur.telephone_chez_employeur = None

    # Employeur - tous None
    donnee_enqueteur.nom_employeur = None
    donnee_enqueteur.telephone_employeur = None
    donnee_enqueteur.telecopie_employeur = None
    donnee_enqueteur.adresse1_employeur = None
    donnee_enqueteur.adresse2_employeur = None
    donnee_enqueteur.adresse3_employeur = None
    donnee_enqueteur.adresse4_employeur = None
    donnee_enqueteur.code_postal_employeur = None
    donnee_enqueteur.ville_employeur = None
    donnee_enqueteur.pays_employeur = None

    # Banque - tous None
    donnee_enqueteur.banque_domiciliation = None
    donnee_enqueteur.libelle_guichet = None
    donnee_enqueteur.titulaire_compte = None
    donnee_enqueteur.code_banque = None
    donnee_enqueteur.code_guichet = None

    # Revenus - tous None
    donnee_enqueteur.commentaires_revenus = None
    donnee_enqueteur.montant_salaire = None
    donnee_enqueteur.periode_versement_salaire = None
    donnee_enqueteur.frequence_versement_salaire = None
    donnee_enqueteur.nature_revenu1 = None
    donnee_enqueteur.montant_revenu1 = None
    donnee_enqueteur.periode_versement_revenu1 = None
    donnee_enqueteur.frequence_versement_revenu1 = None
    donnee_enqueteur.nature_revenu2 = None
    donnee_enqueteur.montant_revenu2 = None
    donnee_enqueteur.periode_versement_revenu2 = None
    donnee_enqueteur.frequence_versement_revenu2 = None
    donnee_enqueteur.nature_revenu3 = None
    donnee_enqueteur.montant_revenu3 = None
    donnee_enqueteur.periode_versement_revenu3 = None
    donnee_enqueteur.frequence_versement_revenu3 = None

    # Mémos - tous None
    donnee_enqueteur.memo1 = None
    donnee_enqueteur.memo2 = None
    donnee_enqueteur.memo3 = None
    donnee_enqueteur.memo4 = None
    donnee_enqueteur.memo5 = None

    # ===== GÉNÉRER LA LIGNE =====
    generated_line_with_crlf = generate_eos_export_line(donnee, donnee_enqueteur, None, None)

    assert generated_line_with_crlf is not None, "generate_eos_export_line a retourné None"

    # Retirer le CRLF pour comparer
    generated_line = generated_line_with_crlf.rstrip('\r\n')

    # ===== COMPARAISON STRICTE =====
    assert len(generated_line) == 2618, f"Ligne générée fait {len(generated_line)} chars au lieu de 2618"

    # Comparaison caractère par caractère pour debug facile
    if generated_line != EXAMPLE_LINE:
        for i, (expected, actual) in enumerate(zip(EXAMPLE_LINE, generated_line)):
            if expected != actual:
                print(f"\n❌ DIFFÉRENCE à position {i}:")
                print(f"  Attendu: {repr(expected)}")
                print(f"  Obtenu:  {repr(actual)}")
                print(f"  Contexte attendu: {repr(EXAMPLE_LINE[max(0,i-20):i+20])}")
                print(f"  Contexte obtenu:  {repr(generated_line[max(0,i-20):i+20])}")
                break

        # Afficher aussi les différences par blocs
        print(f"\n📊 Comparaison par blocs de 100 chars:")
        for start in range(0, 2618, 100):
            end = min(start + 100, 2618)
            expected_block = EXAMPLE_LINE[start:end]
            actual_block = generated_line[start:end]
            if expected_block != actual_block:
                print(f"\n  [{start:4d}-{end:4d}]:")
                print(f"    Attendu: {repr(expected_block)}")
                print(f"    Obtenu:  {repr(actual_block)}")

    # Assertion finale
    assert generated_line == EXAMPLE_LINE, "La ligne générée ne correspond PAS exactement à la ligne exemple"

    print("\n✅ GOLDEN TEST RÉUSSI : La ligne générée correspond EXACTEMENT à la ligne exemple !")


def test_montant_formatting():
    """Test que les montants sont formatés correctement (8 et 10 chars)"""
    from routes.export import format_montant_8, format_montant_10

    # Test montant_8 (facturation)
    assert format_montant_8(24.00) == "   24.00", f"format_montant_8(24.00) devrait être '   24.00', obtenu {repr(format_montant_8(24.00))}"
    assert format_montant_8(0.00) == "    0.00", f"format_montant_8(0.00) devrait être '    0.00', obtenu {repr(format_montant_8(0.00))}"
    assert format_montant_8(None) == "    0.00", f"format_montant_8(None) devrait être '    0.00', obtenu {repr(format_montant_8(None))}"
    assert format_montant_8(-10.50) == "  -10.50", f"format_montant_8(-10.50) devrait être '  -10.50', obtenu {repr(format_montant_8(-10.50))}"
    assert len(format_montant_8(123456.78)) == 8, "format_montant_8 doit toujours retourner 8 chars"

    # Test montant_10 (revenus/salaire)
    assert format_montant_10(123456.78) == " 123456.78", f"format_montant_10(123456.78) devrait être ' 123456.78', obtenu {repr(format_montant_10(123456.78))}"
    assert format_montant_10(0.00) == "      0.00", f"format_montant_10(0.00) devrait être '      0.00', obtenu {repr(format_montant_10(0.00))}"
    assert format_montant_10(None) == "      0.00", f"format_montant_10(None) devrait être '      0.00', obtenu {repr(format_montant_10(None))}"
    assert len(format_montant_10(12345678.99)) == 10, "format_montant_10 doit toujours retourner 10 chars"

    print("\n✅ FORMATAGE MONTANTS CONFORME")


if __name__ == '__main__':
    # Lancer les tests
    test_golden_line_length()
    test_montant_formatting()
    test_generate_line_vs_golden()
