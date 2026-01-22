import sys
import os
import pytest
import pandas as pd
from io import BytesIO
from datetime import date

# Ajouter le dossier parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import Client, ImportProfile, ImportFieldMapping, Donnee, Fichier
from import_engine import ImportEngine

@pytest.fixture
def app():
    # S'assurer que DATABASE_URL est présent pour les tests
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
        
    app = create_app()
    with app.app_context():
        # S'assurer que le client RG_SHERLOCK existe (via seed ou manuellement)
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        if not client:
            client = Client(code='RG_SHERLOCK', nom="RG Sherlock")
            db.session.add(client)
            db.session.commit()
            
        profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL_VERTICAL').first()
        if not profile:
            profile = ImportProfile(client_id=client.id, name="Sherlock Vertical", file_type="EXCEL_VERTICAL")
            db.session.add(profile)
            db.session.commit()
            
        # On ne vide pas tout car on est sur la DB de dev, mais on peut supprimer nos tests précédents
        # Donnee.query.filter(Donnee.numeroDossier.like('SH-%')).delete()
        # db.session.commit()
        
        yield app

def test_rg_sherlock_vertical_parsing_and_mapping(app):
    with app.app_context():
        client = Client.query.filter_by(code='RG_SHERLOCK').first()
        profile = ImportProfile.query.filter_by(client_id=client.id, file_type='EXCEL_VERTICAL').first()
        
        # 1. Créer un fichier Excel vertical simulé avec un header horizontal au début (cas d'erreur courant)
        data = [
            ["DossierId", "RéférenceInterne"], # Header horizontal par erreur
            ["DossierId", "SH-001"],
            ["EC-Nom Usage", "Holmes"],
            ["EC-Prénom", "Sherlock"],
            ["AD-L4 Numéro", "221"],
            ["AD-L4 Type", "B"],
            ["AD-L4 Voie", "Baker Street"],
            ["AD-Téléphone", "01.02.03.04.05"],
            ["DossierId", "SH-002"],
            ["EC-Nom Usage", "Watson"],
            ["EC-Prénom", "John"],
            ["Date retour esperee", "20/05/2025"],
            ["Naissance CP", "75001"]
        ]
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False, header=False)
        content = output.getvalue()
        
        # 2. Utiliser ImportEngine
        engine = ImportEngine(profile)
        records = engine.parse_content(content)
        
        # Assertions Parsing
        assert len(records) >= 2
        
        # Record 1 (Holmes)
        r1 = next(r for r in records if r.get('numeroDossier') == "SH-001")
        assert r1['nom'] == "HOLMES" # Trim upper via YAML transform
        assert r1['prenom'] == "Sherlock"
        assert r1['adresse4'] == "221 B Baker Street" # Computed via YAML transform
        assert r1['telephonePersonnel'] == "0102030405" # Sanitize via YAML transform
        
        # Record 2 (Watson)
        r2 = next(r for r in records if r.get('numeroDossier') == "SH-002")
        assert r2['nom'] == "WATSON"
        assert isinstance(r2['dateRetourEspere'], date)
        assert r2['dateRetourEspere'].year == 2025
        assert r2['codePostalNaissance'] == "75001"
        
        # 3. Test de création d'objet Donnee
        # Création d'un mock Fichier
        fichier = Fichier(nom="test_sherlock.xlsx", client_id=client.id)
        db.session.add(fichier)
        db.session.commit()
        
        donnee = engine.create_donnee_from_record(r1, fichier_id=fichier.id, client_id=client.id)
        assert donnee.numeroDossier == "SH-001"
        assert donnee.nom == "HOLMES"
        assert donnee.adresse4 == "221 B Baker Street"
        
        print("\n✅ Test RG_SHERLOCK vertical réussi !")

if __name__ == '__main__':
    # Pour lancer manuellement : python backend/tests/test_rg_sherlock.py
    import pytest
    pytest.main([__file__])
