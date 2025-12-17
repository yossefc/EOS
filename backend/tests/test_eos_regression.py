"""
Tests de régression pour s'assurer qu'EOS fonctionne toujours après l'ajout de CLIENT_X
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import date

from app import create_app
from extensions import db
from models.client import Client
from models.tarifs import TarifEOS
from services.tarification_service import TarificationService


class TestEOSRegression(unittest.TestCase):
    """Tests de régression EOS"""
    
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
        self.client_test = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Créer le client EOS
        self.client_eos = Client(
            code='EOS',
            nom='EOS France',
            actif=True
        )
        db.session.add(self.client_eos)
        db.session.flush()
        
        # Créer des tarifs EOS
        tarifs_eos = [
            {'code': 'A', 'description': 'Adresse seule', 'montant': 8.0},
            {'code': 'T', 'description': 'Téléphone seul', 'montant': 14.0},
            {'code': 'AT', 'description': 'Adresse et téléphone', 'montant': 22.0},
        ]
        
        for tarif_data in tarifs_eos:
            tarif = TarifEOS(
                code=tarif_data['code'],
                description=tarif_data['description'],
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
    
    def test_tarif_eos_still_works(self):
        """Test que les tarifs EOS fonctionnent toujours"""
        # Sans client_id, doit utiliser TarifEOS
        tarif = TarificationService.get_tarif_eos('A')
        
        self.assertIsNotNone(tarif)
        self.assertEqual(float(tarif.montant), 8.0)
        self.assertIsInstance(tarif, TarifEOS)
    
    def test_tarif_eos_with_eos_client_id(self):
        """Test que les tarifs EOS fonctionnent avec client_id=EOS"""
        tarif = TarificationService.get_tarif_eos('AT', client_id=self.client_eos.id)
        
        self.assertIsNotNone(tarif)
        self.assertEqual(float(tarif.montant), 22.0)
        self.assertIsInstance(tarif, TarifEOS)
    
    def test_eos_client_exists(self):
        """Test que le client EOS existe"""
        client = Client.query.filter_by(code='EOS').first()
        
        self.assertIsNotNone(client)
        self.assertTrue(client.actif)
        self.assertEqual(client.nom, 'EOS France')


if __name__ == '__main__':
    unittest.main()

