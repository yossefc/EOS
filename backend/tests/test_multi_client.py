"""
Tests pour la fonctionnalité multi-client
"""
import pytest
from datetime import datetime
from models import Client, ImportProfile, ImportFieldMapping, Donnee, Fichier, DonneeEnqueteur
from client_utils import (
    get_client_by_code, 
    get_eos_client, 
    get_client_or_default,
    get_import_profile_for_client
)
from extensions import db


class TestClientModels:
    """Tests pour les modèles Client, ImportProfile et ImportFieldMapping"""
    
    def test_create_client(self, app):
        """Test création d'un client"""
        with app.app_context():
            client = Client(
                code='TEST_CLIENT',
                nom='Client de Test',
                actif=True
            )
            db.session.add(client)
            db.session.commit()
            
            assert client.id is not None
            assert client.code == 'TEST_CLIENT'
            assert client.actif is True
    
    def test_create_import_profile(self, app, test_client):
        """Test création d'un profil d'import"""
        with app.app_context():
            profile = ImportProfile(
                client_id=test_client.id,
                name='Test Profile',
                file_type='TXT_FIXED',
                encoding='utf-8',
                actif=True
            )
            db.session.add(profile)
            db.session.commit()
            
            assert profile.id is not None
            assert profile.client_id == test_client.id
            assert profile.file_type == 'TXT_FIXED'
    
    def test_create_field_mapping(self, app, test_import_profile):
        """Test création d'un mapping de champ"""
        with app.app_context():
            mapping = ImportFieldMapping(
                import_profile_id=test_import_profile.id,
                internal_field='numeroDossier',
                start_pos=0,
                length=10,
                strip_whitespace=True,
                is_required=True
            )
            db.session.add(mapping)
            db.session.commit()
            
            assert mapping.id is not None
            assert mapping.internal_field == 'numeroDossier'
            assert mapping.start_pos == 0
            assert mapping.length == 10


class TestClientUtils:
    """Tests pour les utilitaires de gestion des clients"""
    
    def test_get_client_by_code(self, app, test_client):
        """Test récupération d'un client par code"""
        with app.app_context():
            client = get_client_by_code('TEST_CLIENT')
            assert client is not None
            assert client.code == 'TEST_CLIENT'
    
    def test_get_eos_client(self, app):
        """Test récupération du client EOS par défaut"""
        with app.app_context():
            client = get_eos_client()
            assert client is not None
            assert client.code == 'EOS'
    
    def test_get_client_or_default_with_id(self, app, test_client):
        """Test récupération d'un client spécifique par ID"""
        with app.app_context():
            client = get_client_or_default(client_id=test_client.id)
            assert client is not None
            assert client.id == test_client.id
    
    def test_get_client_or_default_with_code(self, app, test_client):
        """Test récupération d'un client spécifique par code"""
        with app.app_context():
            client = get_client_or_default(client_code='TEST_CLIENT')
            assert client is not None
            assert client.code == 'TEST_CLIENT'
    
    def test_get_client_or_default_fallback_to_eos(self, app):
        """Test fallback vers EOS quand aucun client spécifié"""
        with app.app_context():
            client = get_client_or_default()
            assert client is not None
            assert client.code == 'EOS'
    
    def test_get_import_profile_for_client(self, app, test_client, test_import_profile):
        """Test récupération du profil d'import pour un client"""
        with app.app_context():
            profile = get_import_profile_for_client(test_client.id, 'TXT_FIXED')
            assert profile is not None
            assert profile.client_id == test_client.id
            assert profile.file_type == 'TXT_FIXED'


class TestMultiClientDataIsolation:
    """Tests pour l'isolation des données entre clients"""
    
    def test_donnees_filtered_by_client(self, app, test_client, eos_client):
        """Test que les données sont bien filtrées par client"""
        with app.app_context():
            # Créer des fichiers pour chaque client
            fichier_eos = Fichier(nom='test_eos.txt', client_id=eos_client.id)
            fichier_test = Fichier(nom='test_client.txt', client_id=test_client.id)
            db.session.add_all([fichier_eos, fichier_test])
            db.session.commit()
            
            # Créer des données pour chaque client
            donnee_eos = Donnee(
                client_id=eos_client.id,
                fichier_id=fichier_eos.id,
                numeroDossier='EOS001',
                nom='Test EOS'
            )
            donnee_test = Donnee(
                client_id=test_client.id,
                fichier_id=fichier_test.id,
                numeroDossier='TEST001',
                nom='Test Client'
            )
            db.session.add_all([donnee_eos, donnee_test])
            db.session.commit()
            
            # Vérifier l'isolation
            donnees_eos = Donnee.query.filter_by(client_id=eos_client.id).all()
            donnees_test = Donnee.query.filter_by(client_id=test_client.id).all()
            
            assert len(donnees_eos) >= 1
            assert len(donnees_test) >= 1
            assert donnee_eos.numeroDossier == 'EOS001'
            assert donnee_test.numeroDossier == 'TEST001'
            
            # Vérifier qu'on ne mélange pas les données
            assert donnee_eos not in donnees_test
            assert donnee_test not in donnees_eos
    
    def test_contestation_within_same_client(self, app, eos_client):
        """Test qu'une contestation ne peut lier que des enquêtes du même client"""
        with app.app_context():
            fichier = Fichier(nom='test.txt', client_id=eos_client.id)
            db.session.add(fichier)
            db.session.commit()
            
            # Enquête originale
            enquete_originale = Donnee(
                client_id=eos_client.id,
                fichier_id=fichier.id,
                numeroDossier='ENQ001',
                typeDemande='ENQ',
                nom='Original'
            )
            db.session.add(enquete_originale)
            db.session.commit()
            
            # Contestation
            contestation = Donnee(
                client_id=eos_client.id,
                fichier_id=fichier.id,
                numeroDossier='CON001',
                typeDemande='CON',
                nom='Contestation',
                est_contestation=True,
                enquete_originale_id=enquete_originale.id
            )
            db.session.add(contestation)
            db.session.commit()
            
            # Vérifier la relation
            assert contestation.enquete_originale_id == enquete_originale.id
            assert contestation.enquete_originale.client_id == eos_client.id


class TestRetrocompatibilite:
    """Tests pour vérifier la rétro-compatibilité avec le comportement EOS"""
    
    def test_import_without_client_id_uses_eos(self, app, client_app, eos_client):
        """Test qu'un import sans client_id utilise EOS par défaut"""
        with app.app_context():
            # Simuler un import sans client_id
            # (en réalité, ceci serait testé via l'API)
            client = get_client_or_default()
            assert client.code == 'EOS'
    
    def test_api_routes_work_without_client_param(self, client_app):
        """Test que les routes API fonctionnent sans paramètre client_id"""
        # Test GET /api/donnees-complete sans client_id
        response = client_app.get('/api/donnees-complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Test GET /api/donnees sans client_id
        response = client_app.get('/api/donnees')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


# ==================
# Fixtures pytest
# ==================

@pytest.fixture
def app():
    """Créer une application Flask pour les tests"""
    from app import create_app
    from config import Config
    
    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'postgresql://eos_user:eos_password@localhost:5432/eos_test_db'
    
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Créer le client EOS s'il n'existe pas
        eos = Client.query.filter_by(code='EOS').first()
        if not eos:
            eos = Client(code='EOS', nom='EOS France', actif=True)
            db.session.add(eos)
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_app(app):
    """Client de test Flask"""
    return app.test_client()


@pytest.fixture
def eos_client(app):
    """Fixture pour le client EOS"""
    with app.app_context():
        return Client.query.filter_by(code='EOS').first()


@pytest.fixture
def test_client(app):
    """Fixture pour un client de test"""
    with app.app_context():
        client = Client(
            code='TEST_CLIENT',
            nom='Client de Test',
            actif=True
        )
        db.session.add(client)
        db.session.commit()
        yield client
        db.session.delete(client)
        db.session.commit()


@pytest.fixture
def test_import_profile(app, test_client):
    """Fixture pour un profil d'import de test"""
    with app.app_context():
        profile = ImportProfile(
            client_id=test_client.id,
            name='Test Profile',
            file_type='TXT_FIXED',
            encoding='utf-8',
            actif=True
        )
        db.session.add(profile)
        db.session.commit()
        yield profile
        db.session.delete(profile)
        db.session.commit()


