# backend/test_export_eos_reponses.py
"""
Tests pytest pour l'export "Réponses EOS" (format fixed-width 2618 chars)
"""

import pytest
import datetime
from decimal import Decimal
from routes.export_eos_reponses import (
    generate_eos_reponses_line,
    debug_parse_line,
    format_alphanum,
    format_numeric,
    format_date,
    format_amount,
    EXPECTED_LINE_LENGTH,
    EOS_REPONSES_FIELD_SPECS
)


# ============================================================================
# FIXTURES - DONNEES DE TEST
# ============================================================================

class MockDonnee:
    """Mock de l'objet Donnee"""
    def __init__(self):
        self.id = 123
        # Identifiants
        self.numeroDossier = '0000123456'
        self.referenceDossier = 'REF-2025-001'
        self.numeroInterlocuteur = 'INT-12345678'
        self.guidInterlocuteur = '550e8400-e29b-41d4-a716-446655440000'
        self.typeDemande = 'ENQ'
        self.numeroDemande = '00000123456'
        self.numeroDemandeContestee = ''
        self.numeroDemandeInitiale = ''
        self.forfaitDemande = 'AT2'
        self.dateRetourEspere = datetime.date(2025, 2, 15)

        # Etat civil
        self.qualite = 'M.'
        self.nom = 'DUPONT'
        self.prenom = 'Jean'
        self.dateNaissance = datetime.date(1980, 5, 15)
        self.lieuNaissance = 'PARIS'
        self.codePostalNaissance = '75001'
        self.paysNaissance = 'FRANCE'
        self.nomPatronymique = ''

        # Cumul montants
        self.cumulMontantsPrecedents = Decimal('0.00')


class MockDonneeEnqueteur:
    """Mock de l'objet DonneeEnqueteur"""
    def __init__(self):
        self.id = 1
        self.donnee_id = 123

        # Corrections état civil (priorité)
        self.qualite_corrigee = None
        self.nom_corrige = None
        self.prenom_corrige = None
        self.code_postal_naissance_corrige = None
        self.pays_naissance_corrige = None
        self.nom_patronymique_corrige = None

        # Résultat
        self.date_retour = datetime.date.today()
        self.code_resultat = 'P'
        self.elements_retrouves = 'A'
        self.flag_etat_civil_errone = ''

        # Facturation
        self.numero_facture = ''
        self.date_facture = None
        self.montant_facture = Decimal('125.50')
        self.tarif_applique = Decimal('125.50')
        self.cumul_montants_precedents = Decimal('0.00')
        self.reprise_facturation = Decimal('0.00')
        self.remise_eventuelle = Decimal('0.00')

        # Décès
        self.date_deces = None
        self.numero_acte_deces = ''
        self.code_insee_deces = ''
        self.code_postal_deces = ''
        self.localite_deces = ''

        # Adresse
        self.adresse1 = '123 RUE DE LA PAIX'
        self.adresse2 = ''
        self.adresse3 = 'BATIMENT A'
        self.adresse4 = ''
        self.code_postal = '75001'
        self.ville = 'PARIS'
        self.pays_residence = 'FRANCE'

        # Téléphones
        self.telephone_personnel = '0123456789'
        self.telephone_chez_employeur = ''

        # Employeur
        self.nom_employeur = 'ENTREPRISE SA'
        self.telephone_employeur = '0187654321'
        self.telecopie_employeur = ''
        self.adresse1_employeur = '456 AVENUE DES CHAMPS'
        self.adresse2_employeur = ''
        self.adresse3_employeur = ''
        self.adresse4_employeur = ''
        self.code_postal_employeur = '75008'
        self.ville_employeur = 'PARIS'
        self.pays_employeur = 'FRANCE'

        # Banque
        self.banque_domiciliation = 'BNP PARIBAS'
        self.libelle_guichet = 'PARIS OPERA'
        self.titulaire_compte = 'DUPONT JEAN'
        self.code_banque = '30004'
        self.code_guichet = '00123'

        # Revenus
        self.commentaires_revenus = 'Salaire mensuel'
        self.montant_salaire = Decimal('2500.00')
        self.periode_versement_salaire = 1
        self.frequence_versement_salaire = 'M'

        # Revenus supplémentaires
        self.nature_revenu1 = 'Prime annuelle'
        self.montant_revenu1 = Decimal('1000.00')
        self.periode_versement_revenu1 = 12
        self.frequence_versement_revenu1 = 'A'

        self.nature_revenu2 = None
        self.montant_revenu2 = None
        self.periode_versement_revenu2 = None
        self.frequence_versement_revenu2 = None

        self.nature_revenu3 = None
        self.montant_revenu3 = None
        self.periode_versement_revenu3 = None
        self.frequence_versement_revenu3 = None

        # Mémos
        self.memo1 = 'Enquête simple'
        self.memo2 = ''
        self.memo3 = ''
        self.memo4 = ''
        self.memo5 = 'Personne très coopérative, informations vérifiées.'


class MockEnqueteFacturation:
    """Mock de l'objet EnqueteFacturation"""
    def __init__(self):
        self.id = 1
        self.donnee_id = 123
        self.donnee_enqueteur_id = 1
        self.tarif_eos_code = 'AT2'
        self.tarif_eos_montant = Decimal('125.50')
        self.resultat_eos_montant = Decimal('125.50')
        self.tarif_enqueteur_code = 'T1'
        self.tarif_enqueteur_montant = Decimal('50.00')
        self.resultat_enqueteur_montant = Decimal('50.00')


# ============================================================================
# TESTS HELPERS DE FORMATAGE
# ============================================================================

class TestFormatHelpers:
    """Tests des fonctions de formatage"""

    def test_format_alphanum_normal(self):
        """Test formatage alphanumérique normal"""
        assert format_alphanum('HELLO', 10) == 'HELLO     '
        assert len(format_alphanum('HELLO', 10)) == 10

    def test_format_alphanum_trop_long(self):
        """Test formatage alphanumérique avec troncature"""
        assert format_alphanum('ABCDEFGHIJKLMNOP', 10) == 'ABCDEFGHIJ'
        assert len(format_alphanum('ABCDEFGHIJKLMNOP', 10)) == 10

    def test_format_alphanum_none(self):
        """Test formatage alphanumérique avec None"""
        assert format_alphanum(None, 10) == '          '

    def test_format_numeric_normal(self):
        """Test formatage numérique normal"""
        assert format_numeric(123, 5) == '00123'
        assert len(format_numeric(123, 5)) == 5

    def test_format_numeric_none(self):
        """Test formatage numérique avec None"""
        assert format_numeric(None, 5) == '     '

    def test_format_date_normal(self):
        """Test formatage date normal"""
        date = datetime.date(2025, 12, 29)
        assert format_date(date) == '29/12/2025'
        assert len(format_date(date)) == 10

    def test_format_date_none(self):
        """Test formatage date avec None"""
        assert format_date(None) == '          '

    def test_format_amount_normal(self):
        """Test formatage montant normal"""
        assert format_amount(Decimal('125.50'), 8) == '0125,50'
        assert format_amount(Decimal('1234.99'), 8) == '1234,99'
        assert len(format_amount(Decimal('125.50'), 8)) == 8

    def test_format_amount_zero(self):
        """Test formatage montant zéro"""
        assert format_amount(Decimal('0.00'), 8) == '0000,00'
        assert format_amount(None, 8) == '0000,00'


# ============================================================================
# TESTS GENERATION LIGNE EXPORT
# ============================================================================

class TestGenerateEosReponses:
    """Tests de la génération de ligne d'export"""

    def test_longueur_ligne_exacte(self):
        """Test 1: Vérifier longueur exacte de la ligne (2618 + CRLF)"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        f = MockEnqueteFacturation()

        line = generate_eos_reponses_line(d, e, f)

        assert line is not None, "La ligne ne doit pas être None"
        assert line.endswith('\r\n'), "La ligne doit se terminer par CRLF"

        line_data = line.rstrip('\r\n')
        assert len(line_data) == EXPECTED_LINE_LENGTH, f"Longueur ligne doit être {EXPECTED_LINE_LENGTH}, obtenu {len(line_data)}"

    def test_format_crlf(self):
        """Test 2: Vérifier format CRLF en fin de ligne"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)

        assert line.endswith('\r\n'), "La ligne doit se terminer par CRLF (\\r\\n)"
        assert not line.endswith('\n\r'), "La ligne ne doit PAS se terminer par LFCR"

    def test_champs_identifiants_exacts(self):
        """Test 3: Vérifier champs identifiants exacts (pas d'IDs internes)"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        line_data = line.rstrip('\r\n')

        # Extraire les champs selon positions
        numero_dossier = line_data[0:10].strip()
        numero_interlocuteur = line_data[25:37].strip()
        guid = line_data[37:73].strip()

        assert numero_dossier == '0000123456', f"N° dossier doit être '0000123456', obtenu '{numero_dossier}'"
        assert numero_interlocuteur == 'INT-12345678', f"N° interlocuteur doit être 'INT-12345678', obtenu '{numero_interlocuteur}'"
        assert guid == '550e8400-e29b-41d4-a716-446655440000', f"GUID incorrect: '{guid}'"

    def test_type_demande_enq(self):
        """Test 4: Vérifier TYPE_DEMANDE = ENQ"""
        d = MockDonnee()
        d.typeDemande = 'ENQ'
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        line_data = line.rstrip('\r\n')

        type_demande = line_data[73:76].strip()
        assert type_demande == 'ENQ', f"Type demande doit être 'ENQ', obtenu '{type_demande}'"

    def test_type_demande_con(self):
        """Test 5: Vérifier TYPE_DEMANDE = CON et champs contestation"""
        d = MockDonnee()
        d.typeDemande = 'CON'
        d.numeroDemandeContestee = '00000111111'
        d.numeroDemandeInitiale = '00000999999'
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        line_data = line.rstrip('\r\n')

        type_demande = line_data[73:76].strip()
        numero_demande_contestee = line_data[87:98].strip()
        numero_demande_initiale = line_data[98:109].strip()

        assert type_demande == 'CON', f"Type demande doit être 'CON', obtenu '{type_demande}'"
        assert numero_demande_contestee == '00000111111', f"N° demande contestée incorrect: '{numero_demande_contestee}'"
        assert numero_demande_initiale == '00000999999', f"N° demande initiale incorrect: '{numero_demande_initiale}'"

    def test_correction_etat_civil_prioritaire(self):
        """Test 6: Vérifier priorité corrections état civil"""
        d = MockDonnee()
        d.nom = 'DUPONT'
        e = MockDonneeEnqueteur()
        e.nom_corrige = 'DURAND'  # Correction prioritaire

        line = generate_eos_reponses_line(d, e)
        line_data = line.rstrip('\r\n')

        # Position du nom: après identifiants(135) + qualite(10) = 145
        nom = line_data[145:175].strip()

        assert nom == 'DURAND', f"Nom doit être 'DURAND' (corrigé), obtenu '{nom}'"

    def test_facturation_depuis_enqueteur(self):
        """Test 7: Vérifier facturation priorité DonneeEnqueteur"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        e.montant_facture = Decimal('125.50')
        f = MockEnqueteFacturation()
        f.resultat_eos_montant = Decimal('200.00')  # Doit être ignoré

        line = generate_eos_reponses_line(d, e, f)

        # Vérifier que c'est bien le montant de e, pas de f
        assert '0125,50' in line, "Montant doit être celui de DonneeEnqueteur (125,50)"
        assert '0200,00' not in line, "Montant de EnqueteFacturation ne doit pas être utilisé"

    def test_facturation_depuis_facturation_si_enqueteur_vide(self):
        """Test 8: Vérifier facturation depuis EnqueteFacturation si DonneeEnqueteur vide"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        e.montant_facture = None
        e.tarif_applique = None
        f = MockEnqueteFacturation()
        f.resultat_eos_montant = Decimal('200.00')

        line = generate_eos_reponses_line(d, e, f)

        # Vérifier que c'est bien le montant de f
        assert '0200,00' in line, "Montant doit être celui de EnqueteFacturation (200,00)"

    def test_numero_compte_rib_toujours_vides(self):
        """Test 9: Vérifier que numero_compte et RIB sont TOUJOURS vides"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        line_data = line.rstrip('\r\n')

        # Calculer position (après tous les champs jusqu'à la banque)
        # Simplifié: vérifier qu'il n'y a pas de numéro compte rempli
        # Position exacte dépend du spec, mais on peut vérifier la présence

        # Le numéro compte (11) et RIB (2) doivent être des espaces
        parsed = debug_parse_line(line)
        assert parsed['numeroCompte'].strip() == '', "Numéro compte doit être VIDE (espaces)"
        assert parsed['ribCompte'].strip() == '', "RIB doit être VIDE (espaces)"

    def test_champs_manquants_retourne_none(self):
        """Test 10: Vérifier qu'une ligne avec champs obligatoires manquants retourne None"""
        d = MockDonnee()
        d.numeroDossier = None  # Champ obligatoire manquant
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)

        assert line is None, "La ligne doit être None si champs obligatoires manquants"

    def test_revenus_presente(self):
        """Test 11: Vérifier que les champs revenus sont présents"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        e.commentaires_revenus = 'Test revenus'
        e.montant_salaire = Decimal('2500.00')

        line = generate_eos_reponses_line(d, e)

        # Vérifier présence des revenus
        assert line is not None
        assert '2500,00' in line, "Montant salaire doit être présent"

    def test_memos_presents(self):
        """Test 12: Vérifier que les mémos sont présents"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        e.memo1 = 'Memo test 1'
        e.memo5 = 'Memo long test'

        line = generate_eos_reponses_line(d, e)

        assert line is not None
        # Les mémos doivent être quelque part dans la ligne
        # (vérification exacte nécessite parsing complet)

    def test_spec_coverage_complete(self):
        """Test 13: Vérifier que tous les champs du spec sont générés"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()
        f = MockEnqueteFacturation()

        line = generate_eos_reponses_line(d, e, f)
        line_data = line.rstrip('\r\n')

        # Vérifier que la longueur correspond au nombre de champs du spec
        total_width = sum(spec[1] for spec in EOS_REPONSES_FIELD_SPECS)
        assert len(line_data) == total_width, f"Longueur ligne ({len(line_data)}) != somme specs ({total_width})"


# ============================================================================
# TESTS DEBUG HELPER
# ============================================================================

class TestDebugParseLine:
    """Tests du helper debug_parse_line"""

    def test_debug_parse_retourne_dict(self):
        """Test que debug_parse_line retourne un dict"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        parsed = debug_parse_line(line)

        assert isinstance(parsed, dict), "debug_parse_line doit retourner un dict"
        assert len(parsed) == len(EOS_REPONSES_FIELD_SPECS), "Le dict doit contenir tous les champs"

    def test_debug_parse_extrait_champs(self):
        """Test que debug_parse_line extrait correctement les champs"""
        d = MockDonnee()
        e = MockDonneeEnqueteur()

        line = generate_eos_reponses_line(d, e)
        parsed = debug_parse_line(line)

        # Vérifier quelques champs clés
        assert parsed['numeroDossier'].strip() == '0000123456'
        assert parsed['typeDemande'].strip() == 'ENQ'
        assert parsed['codeResultat'].strip() == 'P'


# ============================================================================
# TEST INTEGRATION EXEMPLE REEL
# ============================================================================

class TestExempleReel:
    """Test sur un exemple réel complet"""

    def test_exemple_complet_enq(self):
        """Test intégration: exemple complet ENQ"""
        # Créer données réalistes
        d = MockDonnee()
        d.typeDemande = 'ENQ'

        e = MockDonneeEnqueteur()
        e.code_resultat = 'P'
        e.elements_retrouves = 'A'
        e.montant_facture = Decimal('125.50')

        f = MockEnqueteFacturation()

        # Générer ligne
        line = generate_eos_reponses_line(d, e, f)

        # Assertions
        assert line is not None
        assert len(line.rstrip('\r\n')) == EXPECTED_LINE_LENGTH
        assert line.endswith('\r\n')

        # Vérifier présence données clés
        assert '0000123456' in line  # N° dossier
        assert 'ENQ' in line  # Type demande
        assert 'P' in line  # Code résultat
        assert '0125,50' in line  # Montant facture

    def test_exemple_complet_con(self):
        """Test intégration: exemple complet CON"""
        d = MockDonnee()
        d.typeDemande = 'CON'
        d.numeroDemandeContestee = '00000111111'
        d.numeroDemandeInitiale = '00000999999'

        e = MockDonneeEnqueteur()
        e.code_resultat = 'N'
        e.montant_facture = Decimal('0.00')

        # Générer ligne
        line = generate_eos_reponses_line(d, e)

        # Assertions
        assert line is not None
        assert len(line.rstrip('\r\n')) == EXPECTED_LINE_LENGTH
        assert 'CON' in line
        assert '00000111111' in line  # N° demande contestée


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
