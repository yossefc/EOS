"""
Tests pour CLIENT_X
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime, date
from io import BytesIO
import pandas as pd

from app import create_app
from extensions import db
from models.client import Client
from models.import_config import ImportProfile, ImportFieldMapping
from models.tarifs import TarifClient
from models.models import Donnee, Fichier
from import_engine import ImportEngine


class TestClientX(unittest.TestCase):
    """Tests pour CLIENT_X"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Supprimer DATABASE_URL pour forcer SQLite en mémoire
        import os
        self.old_database_url = os.environ.get('DATABASE_URL')
        if 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Créer CLIENT_X
        self.client_x = Client(
            code='CLIENT_X',
            nom='Client X',
            actif=True
        )
        db.session.add(self.client_x)
        db.session.flush()
        
        # Créer le profil ENQUETES
        self.profile_enquetes = ImportProfile(
            client_id=self.client_x.id,
            name='ENQUETES',
            file_type='EXCEL',
            sheet_name='Worksheet',
            actif=True
        )
        db.session.add(self.profile_enquetes)
        db.session.flush()
        
        # Créer les mappings
        mappings = [
            {'internal_field': 'numeroDossier', 'column_name': 'NUM', 'is_required': True},
            {'internal_field': 'nom', 'column_name': 'NOM', 'is_required': True},
            {'internal_field': 'prenom', 'column_name': 'PRENOM', 'is_required': True},
            {'internal_field': 'dateNaissance', 'column_name': 'JOUR', 'is_required': False},
            {'internal_field': 'dateNaissance_mois', 'column_name': 'MOIS', 'is_required': False},
            {'internal_field': 'dateNaissance_annee', 'column_name': 'ANNEE NAISSANCE', 'is_required': False},
            {'internal_field': 'lieuNaissance', 'column_name': 'LIEUNAISSANCE', 'is_required': False},
            {'internal_field': 'adresse1', 'column_name': 'ADRESSE', 'is_required': False},
            {'internal_field': 'codePostal', 'column_name': 'CP', 'is_required': False},
            {'internal_field': 'ville', 'column_name': 'VILLE', 'is_required': False},
            {'internal_field': 'telephonePersonnel', 'column_name': 'TEL', 'is_required': False},
            {'internal_field': 'tarif_lettre', 'column_name': 'TARIF', 'is_required': False},
            {'internal_field': 'recherche', 'column_name': 'RECHERCHE', 'is_required': False},
            {'internal_field': 'typeDemande', 'column_name': '', 'default_value': 'ENQ', 'is_required': False},
        ]
        
        for mapping_data in mappings:
            mapping = ImportFieldMapping(
                import_profile_id=self.profile_enquetes.id,
                internal_field=mapping_data['internal_field'],
                column_name=mapping_data.get('column_name'),
                strip_whitespace=True,
                default_value=mapping_data.get('default_value'),
                is_required=mapping_data.get('is_required', False)
            )
            db.session.add(mapping)
        
        # Créer des tarifs
        tarifs = [
            {'code_lettre': 'A', 'montant': 15.0},
            {'code_lettre': 'B', 'montant': 20.0},
            {'code_lettre': 'C', 'montant': 25.0},
        ]
        
        for tarif_data in tarifs:
            tarif = TarifClient(
                client_id=self.client_x.id,
                code_lettre=tarif_data['code_lettre'],
                montant=tarif_data['montant'],
                date_debut=date.today(),
                actif=True
            )
            db.session.add(tarif)
        
        db.session.commit()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Restaurer DATABASE_URL
        import os
        if self.old_database_url:
            os.environ['DATABASE_URL'] = self.old_database_url
    
    def test_import_enquetes_normalisation_cp(self):
        """Test de l'import avec normalisation du code postal"""
        # Créer un fichier Excel de test
        data = {
            'NUM': ['001', '002'],
            'NOM': ['DUPONT', 'MARTIN'],
            'PRENOM': ['Jean', 'Marie'],
            'JOUR': ['15', '20'],
            'MOIS': ['3', '6'],
            'ANNEE NAISSANCE': ['1980', '1975'],
            'LIEUNAISSANCE': ['Paris', 'Lyon'],
            'ADRESSE': ['10 rue de la Paix', '5 avenue Victor Hugo'],
            'CP': ['75001', '456'],  # Le second doit être normalisé à 00456
            'VILLE': ['Paris', 'Lyon'],
            'TEL': ['0612345678', '0'],  # Le second doit être null
            'TARIF': ['A', 'B'],
            'RECHERCHE': ['Recherche 1', 'Recherche 2']
        }
        
        df = pd.DataFrame(data)
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Worksheet', index=False)
        excel_buffer.seek(0)
        
        # Utiliser ImportEngine
        engine = ImportEngine(self.profile_enquetes)
        parsed_records = engine.parse_content(excel_buffer.read())
        
        self.assertEqual(len(parsed_records), 2)
        
        # Créer les données
        fichier = Fichier(nom='test.xlsx', client_id=self.client_x.id)
        db.session.add(fichier)
        db.session.flush()
        
        for record in parsed_records:
            donnee = engine.create_donnee_from_record(
                record,
                fichier_id=fichier.id,
                client_id=self.client_x.id
            )
            db.session.add(donnee)
        
        db.session.commit()
        
        # Vérifier les données
        donnees = Donnee.query.filter_by(client_id=self.client_x.id).all()
        self.assertEqual(len(donnees), 2)
        
        # Vérifier la normalisation du CP
        donnee2 = Donnee.query.filter_by(numeroDossier='002').first()
        self.assertEqual(donnee2.codePostal, '00456')
        
        # Vérifier que le téléphone "0" est null
        self.assertIsNone(donnee2.telephonePersonnel)
        
        # Vérifier le tarif_lettre
        donnee1 = Donnee.query.filter_by(numeroDossier='001').first()
        self.assertEqual(donnee1.tarif_lettre, 'A')
    
    def test_import_lignes_vides_ignorees(self):
        """Test que les lignes vides sont ignorées"""
        data = {
            'NUM': ['001', None, '003'],
            'NOM': ['DUPONT', None, 'BERNARD'],
            'PRENOM': ['Jean', None, 'Paul'],
            'JOUR': ['15', None, '25'],
            'MOIS': ['3', None, '12'],
            'ANNEE NAISSANCE': ['1980', None, '1990'],
            'LIEUNAISSANCE': ['Paris', None, 'Marseille'],
            'ADRESSE': ['10 rue', None, '20 avenue'],
            'CP': ['75001', None, '13001'],
            'VILLE': ['Paris', None, 'Marseille'],
            'TEL': ['0612345678', None, '0698765432'],
            'TARIF': ['A', None, 'C'],
            'RECHERCHE': ['Recherche 1', None, 'Recherche 3']
        }
        
        df = pd.DataFrame(data)
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Worksheet', index=False)
        excel_buffer.seek(0)
        
        engine = ImportEngine(self.profile_enquetes)
        parsed_records = engine.parse_content(excel_buffer.read())
        
        # Devrait ignorer la ligne vide
        self.assertEqual(len(parsed_records), 2)
    
    def test_tarif_client_retrieval(self):
        """Test de récupération des tarifs CLIENT_X"""
        from services.tarification_service import TarificationService
        
        # Récupérer un tarif CLIENT_X
        tarif = TarificationService.get_tarif_eos('A', client_id=self.client_x.id)
        
        self.assertIsNotNone(tarif)
        self.assertEqual(float(tarif.montant), 15.0)
        
        # Vérifier que c'est bien un TarifClient
        self.assertIsInstance(tarif, TarifClient)
    
    def test_update_date_naissance_allowed(self):
        """Test que la mise à jour de la date de naissance est autorisée pour CLIENT_X"""
        # Créer une donnée
        fichier = Fichier(nom='test.xlsx', client_id=self.client_x.id)
        db.session.add(fichier)
        db.session.flush()
        
        donnee = Donnee(
            client_id=self.client_x.id,
            fichier_id=fichier.id,
            numeroDossier='TEST001',
            nom='DUPONT',
            prenom='Jean',
            dateNaissance=date(1980, 3, 15),
            lieuNaissance='Paris'
        )
        db.session.add(donnee)
        db.session.commit()
        
        # Mettre à jour via l'API
        response = self.client.put(
            f'/api/donnees/{donnee.id}',
            json={
                'dateNaissance': '1981-05-20',
                'lieuNaissance': 'Lyon'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la mise à jour
        donnee_updated = Donnee.query.get(donnee.id)
        self.assertEqual(donnee_updated.dateNaissance, date(1981, 5, 20))
        self.assertEqual(donnee_updated.lieuNaissance, 'Lyon')


if __name__ == '__main__':
    unittest.main()

