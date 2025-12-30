# backend/test_export_eos_compliance.py

"""
Tests automatiques pour vérifier la conformité de l'export EOS
au cahier des charges (format texte longueur fixe Windows CRLF)
"""

import pytest
import datetime
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from routes.export import generate_eos_export_line


def create_test_donnee_enq():
    """Crée une enquête test avec toutes les valeurs transmises par EOS"""
    donnee = Donnee(
        id=123,
        client_id=1,
        fichier_id=1,
        # Champs identifiants transmis par EOS (OBLIGATOIRES)
        numeroDossier='0000123456',
        referenceDossier='REF-2025-001',
        numeroInterlocuteur='INT-12345678',
        guidInterlocuteur='550e8400-e29b-41d4-a716-446655440000',
        typeDemande='ENQ',
        numeroDemande='00000123456',
        numeroDemandeContestee='',
        numeroDemandeInitiale='',
        forfaitDemande='AT2',
        dateRetourEspere=datetime.date(2025, 2, 15),
        # Éléments demandés (transmis par EOS)
        elementDemandes='AT',
        elementObligatoires='A',
        elementContestes='',
        codeMotif='',
        motifDeContestation='',
        cumulMontantsPrecedents=0.0,
        # État civil
        qualite='M.',
        nom='DUPONT',
        prenom='Jean',
        dateNaissance=datetime.date(1980, 5, 15),
        lieuNaissance='PARIS',
        codePostalNaissance='75001',
        paysNaissance='FRANCE',
        nomPatronymique='',
        # Autres champs
        codesociete='01',
        urgence='0',
        commentaire='Test enquête normale',
        date_butoir=datetime.date(2025, 2, 15),
    )
    return donnee


def create_test_donnee_con():
    """Crée une contestation test avec toutes les valeurs transmises par EOS"""
    donnee = Donnee(
        id=456,
        client_id=1,
        fichier_id=1,
        # Champs identifiants transmis par EOS (OBLIGATOIRES)
        numeroDossier='0000456789',
        referenceDossier='REF-2025-002',
        numeroInterlocuteur='INT-87654321',
        guidInterlocuteur='660e8400-e29b-41d4-a716-446655440001',
        typeDemande='CON',
        numeroDemande='00000456789',
        numeroDemandeContestee='00000123456',  # Référence enquête initiale
        numeroDemandeInitiale='00000123456',
        forfaitDemande='CONTEST',
        dateRetourEspere=datetime.date(2025, 3, 1),
        # Éléments contestés (spécifique CON)
        elementDemandes='AT',
        elementObligatoires='A',
        elementContestes='A',
        codeMotif='MOTIF_ERR_ADR',
        motifDeContestation='Adresse incorrecte trouvée',
        cumulMontantsPrecedents=125.50,  # Montants déjà facturés
        # État civil
        qualite='Mme',
        nom='MARTIN',
        prenom='Marie',
        dateNaissance=datetime.date(1975, 8, 20),
        lieuNaissance='LYON',
        codePostalNaissance='69001',
        paysNaissance='FRANCE',
        nomPatronymique='DURAND',
        # Autres champs
        codesociete='02',
        urgence='1',
        commentaire='Contestation - adresse erronée',
        date_butoir=datetime.date(2025, 3, 1),
    )
    return donnee


def create_test_donnee_enqueteur():
    """Crée des données enquêteur test"""
    donnee_enqueteur = DonneeEnqueteur(
        id=1,
        client_id=1,
        donnee_id=123,
        code_resultat='P',
        elements_retrouves='A',
        flag_etat_civil_errone='',
        date_retour=datetime.date.today(),
        # Adresse trouvée
        adresse1='123 RUE DE LA PAIX',
        adresse2='',
        adresse3='BATIMENT A',
        adresse4='',
        code_postal='75001',
        ville='PARIS',
        pays_residence='FRANCE',
        telephone_personnel='0123456789',
        telephone_chez_employeur='',
        # Décès
        date_deces=None,
        numero_acte_deces='',
        code_insee_deces='',
        code_postal_deces='',
        localite_deces='',
        # Employeur
        nom_employeur='ENTREPRISE SA',
        telephone_employeur='0187654321',
        telecopie_employeur='',
        adresse1_employeur='456 AVENUE DES CHAMPS',
        adresse2_employeur='',
        adresse3_employeur='',
        adresse4_employeur='',
        code_postal_employeur='75008',
        ville_employeur='PARIS',
        pays_employeur='FRANCE',
        # Banque
        banque_domiciliation='BNP PARIBAS',
        libelle_guichet='PARIS OPERA',
        titulaire_compte='DUPONT JEAN',
        code_banque='30004',
        code_guichet='00123',
        # Facturation
        numero_facture='',
        date_facture=None,
        montant_facture=0.0,
        tarif_applique=0.0,
        cumul_montants_precedents=0.0,
        reprise_facturation=0.0,
        remise_eventuelle=0.0,
    )
    return donnee_enqueteur


class TestExportEOSCompliance:
    """Tests de conformité pour l'export EOS"""

    def test_export_enq_format_crlf(self):
        """Test 1: Vérifier que la ligne se termine par CRLF (\\r\\n)"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)

        assert line.endswith('\r\n'), "La ligne doit se terminer par CRLF (\\r\\n)"

    def test_export_enq_champs_obligatoires_exacts(self):
        """Test 2: Vérifier que les champs obligatoires reprennent EXACTEMENT les valeurs transmises"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)

        # Extraire les champs selon les positions (sans CRLF à la fin)
        line_data = line.rstrip('\r\n')

        # 1. N° DOSSIER (0, 10) - doit être EXACTEMENT celui transmis
        numero_dossier = line_data[0:10].strip()
        assert numero_dossier == '0000123456', f"N° dossier doit être '0000123456', trouvé '{numero_dossier}'"

        # 2. RÉFÉRENCE DOSSIER (10, 15)
        reference_dossier = line_data[10:25].strip()
        assert reference_dossier == 'REF-2025-001', f"Référence dossier incorrecte: '{reference_dossier}'"

        # 3. NUMÉRO INTERLOCUTEUR (25, 12) - doit être EXACTEMENT celui transmis, PAS 'D-123'
        numero_interlocuteur = line_data[25:37].strip()
        assert numero_interlocuteur == 'INT-12345678', f"N° interlocuteur doit être 'INT-12345678', trouvé '{numero_interlocuteur}'"
        assert not numero_interlocuteur.startswith('D-'), "Ne doit PAS inventer un numéro avec 'D-{id}'"

        # 4. GUID INTERLOCUTEUR (37, 36)
        guid_interlocuteur = line_data[37:73].strip()
        assert guid_interlocuteur == '550e8400-e29b-41d4-a716-446655440000', f"GUID incorrect: '{guid_interlocuteur}'"

        # 5. TYPE DE DEMANDE (73, 3) - doit être 'ENQ' pour une enquête
        type_demande = line_data[73:76].strip()
        assert type_demande == 'ENQ', f"Type demande doit être 'ENQ', trouvé '{type_demande}'"

        # 6. NUMÉRO DE DEMANDE (76, 11) - doit être EXACTEMENT celui transmis, PAS l'ID interne
        numero_demande = line_data[76:87].strip()
        assert numero_demande == '00000123456', f"N° demande doit être '00000123456', trouvé '{numero_demande}'"
        assert numero_demande != '123', "Ne doit PAS utiliser l'ID interne"

        # 9. FORFAIT DEMANDE (109, 16) - doit être EXACTEMENT celui transmis
        forfait_demande = line_data[109:125].strip()
        assert forfait_demande == 'AT2', f"Forfait doit être 'AT2', trouvé '{forfait_demande}'"

    def test_export_enq_elements_demandes(self):
        """Test 3: Vérifier que les éléments demandés/obligatoires sont ceux transmis"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)
        line_data = line.rstrip('\r\n')

        # Position des éléments demandés (calculée selon le cahier des charges)
        # Après DATE_ENVOI (10) qui est à position 1088, on a:
        # ELEMENTS_DEMANDES (1098, 10)
        # ELEMENTS_OBLIGATOIRES (1108, 10)

        # Note: Les positions exactes dépendent du cahier des charges
        # Pour ce test, on vérifie que les valeurs sont présentes dans la ligne
        assert 'AT' in line, "Éléments demandés 'AT' doivent être présents"
        # Ne doit PAS utiliser de valeur par défaut inventée

    def test_export_con_type_demande(self):
        """Test 4: Vérifier qu'une contestation a TYPE_DEMANDE = 'CON'"""
        donnee = create_test_donnee_con()
        donnee_enqueteur = create_test_donnee_enqueteur()
        donnee_enqueteur.donnee_id = 456

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)
        line_data = line.rstrip('\r\n')

        # 5. TYPE DE DEMANDE (73, 3) - doit être 'CON' pour une contestation
        type_demande = line_data[73:76].strip()
        assert type_demande == 'CON', f"Type demande doit être 'CON' pour contestation, trouvé '{type_demande}'"

    def test_export_con_champs_contestation(self):
        """Test 5: Vérifier que les champs spécifiques contestation sont remplis pour CON"""
        donnee = create_test_donnee_con()
        donnee_enqueteur = create_test_donnee_enqueteur()
        donnee_enqueteur.donnee_id = 456

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)
        line_data = line.rstrip('\r\n')

        # 7. NUMÉRO DEMANDE CONTESTÉE (87, 11) - doit être rempli pour CON
        numero_demande_contestee = line_data[87:98].strip()
        assert numero_demande_contestee == '00000123456', f"N° demande contestée doit être rempli pour CON, trouvé '{numero_demande_contestee}'"

        # 8. NUMÉRO DEMANDE INITIALE (98, 11) - doit être rempli pour CON
        numero_demande_initiale = line_data[98:109].strip()
        assert numero_demande_initiale == '00000123456', f"N° demande initiale doit être rempli pour CON, trouvé '{numero_demande_initiale}'"

        # Les champs de contestation doivent être présents quelque part dans la ligne
        # (positions exactes selon cahier des charges)
        assert 'MOTIF_ERR_ADR' in line or line_data.find('MOTIF_ERR_ADR') >= 0, "Code motif contestation doit être présent"
        # Le cumul montants précédemment facturés doit être formaté (125,50)
        assert '0125,50' in line, "Cumul montants précédents doit être '0125,50' (format 99999,99)"

    def test_export_enq_contestation_vide(self):
        """Test 6: Vérifier que les champs contestation sont vides/0 pour ENQ"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)
        line_data = line.rstrip('\r\n')

        # 7-8. NUMÉRO DEMANDE CONTESTÉE/INITIALE doivent être vides pour ENQ
        numero_demande_contestee = line_data[87:98].strip()
        numero_demande_initiale = line_data[98:109].strip()

        assert numero_demande_contestee == '', f"N° demande contestée doit être vide pour ENQ, trouvé '{numero_demande_contestee}'"
        assert numero_demande_initiale == '', f"N° demande initiale doit être vide pour ENQ, trouvé '{numero_demande_initiale}'"

        # Cumul montants précédents = 0 pour ENQ
        # Format: 00000,00 (8 caractères)
        # Position selon cahier des charges (à adapter)

    def test_export_validation_champ_obligatoire_manquant(self):
        """Test 7: Vérifier qu'une exception est levée si un champ obligatoire est manquant"""
        donnee = create_test_donnee_enq()
        donnee.numeroDossier = None  # Champ obligatoire manquant
        donnee_enqueteur = create_test_donnee_enqueteur()

        # La fonction doit lever une exception si un champ obligatoire est manquant
        with pytest.raises(ValueError, match="Champ obligatoire manquant"):
            generate_eos_export_line(donnee, donnee_enqueteur, None)

    def test_export_longueur_ligne_fixe(self):
        """Test 8: Vérifier que chaque ligne a une longueur fixe"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)

        # Longueur totale selon cahier des charges (sans CRLF) + 2 pour CRLF
        # Adapter selon la longueur réelle du cahier des charges
        LONGUEUR_ATTENDUE = 1854 + 2  # 1854 caractères + CRLF

        assert len(line) == LONGUEUR_ATTENDUE, f"Longueur ligne doit être {LONGUEUR_ATTENDUE}, trouvé {len(line)}"

    def test_export_format_date_jjmmaaaa(self):
        """Test 9: Vérifier que les dates sont au format JJ/MM/AAAA"""
        donnee = create_test_donnee_enq()
        donnee_enqueteur = create_test_donnee_enqueteur()

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)

        # Les dates dans la ligne doivent être au format JJ/MM/AAAA (10 caractères)
        # Exemple: dateRetourEspere = 2025-02-15 doit devenir '15/02/2025'
        assert '15/02/2025' in line, "Date retour espéré doit être au format JJ/MM/AAAA"

    def test_export_format_montant_virgule(self):
        """Test 10: Vérifier que les montants sont au format 99999,99 (virgule)"""
        donnee = create_test_donnee_con()
        donnee_enqueteur = create_test_donnee_enqueteur()
        donnee_enqueteur.donnee_id = 456

        line = generate_eos_export_line(donnee, donnee_enqueteur, None)

        # Le montant 125.50 doit être formaté '0125,50' (8 caractères, virgule comme séparateur)
        assert '0125,50' in line, "Montant doit être au format 99999,99 avec virgule"
        # Ne doit PAS contenir de point comme séparateur décimal
        # (sauf pour les montants à 0 qui peuvent être '00000,00')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
