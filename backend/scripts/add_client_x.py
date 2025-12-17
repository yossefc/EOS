"""
Script pour ajouter le client CLIENT_X avec ses profils d'import
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from models.client import Client
from models.import_config import ImportProfile, ImportFieldMapping
from models.tarifs import TarifClient
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_client_x():
    """Ajoute CLIENT_X et ses configurations d'import"""
    
    # 1. Vérifier si CLIENT_X existe déjà et le supprimer pour recommencer proprement
    existing_client = Client.query.filter_by(code='CLIENT_X').first()
    if existing_client:
        logger.info(f"CLIENT_X existe déjà (ID: {existing_client.id}). Suppression pour réinstallation propre...")
        
        # Supprimer les tarifs associés
        TarifClient.query.filter_by(client_id=existing_client.id).delete()
        
        # Supprimer les mappings des profils
        for profile in ImportProfile.query.filter_by(client_id=existing_client.id).all():
            ImportFieldMapping.query.filter_by(import_profile_id=profile.id).delete()
        
        # Supprimer les profils
        ImportProfile.query.filter_by(client_id=existing_client.id).delete()
        
        # Supprimer les données et fichiers (avec cascade)
        from models.models import Fichier, Donnee
        Donnee.query.filter_by(client_id=existing_client.id).delete()
        Fichier.query.filter_by(client_id=existing_client.id).delete()
        
        # Supprimer le client
        db.session.delete(existing_client)
        db.session.commit()
        logger.info("CLIENT_X et toutes ses données ont été supprimés")
    
    # 2. Créer le client CLIENT_X
    client_x = Client(
        code='CLIENT_X',
        nom='Client X',
        actif=True
    )
    db.session.add(client_x)
    db.session.flush()
    logger.info(f"Client CLIENT_X créé avec ID: {client_x.id}")
    
    # 3. Créer le profil d'import ENQUÊTES
    profile_enquetes = ImportProfile(
        client_id=client_x.id,
        name='ENQUETES',
        file_type='EXCEL',
        sheet_name='Worksheet',
        encoding='utf-8',
        actif=True
    )
    db.session.add(profile_enquetes)
    db.session.flush()
    logger.info(f"Profil ENQUETES créé avec ID: {profile_enquetes.id}")
    
    # 4. Créer les mappings pour ENQUÊTES
    mappings_enquetes = [
        {'internal_field': 'numeroDossier', 'column_name': 'NUM', 'is_required': True},
        {'internal_field': 'nom', 'column_name': 'NOM', 'is_required': True},
        {'internal_field': 'prenom', 'column_name': 'PRENOM', 'is_required': True},
        {'internal_field': 'dateNaissance', 'column_name': 'JOUR', 'is_required': False},  # Sera combiné
        {'internal_field': 'dateNaissance_mois', 'column_name': 'MOIS', 'is_required': False},  # Sera combiné
        {'internal_field': 'dateNaissance_annee', 'column_name': 'ANNEE NAISSANCE', 'is_required': False},  # Sera combiné
        {'internal_field': 'lieuNaissance', 'column_name': 'LIEUNAISSANCE', 'is_required': False},
        {'internal_field': 'datedenvoie', 'column_name': 'DATE ENVOI', 'is_required': False},
        {'internal_field': 'date_butoir', 'column_name': 'DATE BUTOIR', 'is_required': False},
        {'internal_field': 'adresse1', 'column_name': 'ADRESSE', 'is_required': False},
        {'internal_field': 'codePostal', 'column_name': 'CP', 'is_required': False},
        {'internal_field': 'ville', 'column_name': 'VILLE', 'is_required': False},
        {'internal_field': 'telephonePersonnel', 'column_name': 'TEL', 'is_required': False},
        {'internal_field': 'tarif_lettre', 'column_name': 'TARIF', 'is_required': False},
        {'internal_field': 'recherche', 'column_name': 'RECHERCHE', 'is_required': False},
        {'internal_field': 'instructions', 'column_name': 'INSTRUCTIONS', 'is_required': False},
        {'internal_field': 'typeDemande', 'column_name': '', 'default_value': 'ENQ', 'is_required': False},
    ]
    
    for mapping_data in mappings_enquetes:
        mapping = ImportFieldMapping(
            import_profile_id=profile_enquetes.id,
            internal_field=mapping_data['internal_field'],
            column_name=mapping_data.get('column_name'),
            strip_whitespace=True,
            default_value=mapping_data.get('default_value'),
            is_required=mapping_data.get('is_required', False)
        )
        db.session.add(mapping)
    
    logger.info(f"Mappings ENQUETES créés pour le profil {profile_enquetes.id}")
    
    # 5. Créer le profil d'import CONTESTATIONS
    profile_contestations = ImportProfile(
        client_id=client_x.id,
        name='CONTESTATIONS',
        file_type='EXCEL',
        sheet_name='FICHIER 1 CONTRE',
        encoding='utf-8',
        actif=True
    )
    db.session.add(profile_contestations)
    db.session.flush()
    logger.info(f"Profil CONTESTATIONS créé avec ID: {profile_contestations.id}")
    
    # 6. Créer les mappings pour CONTESTATIONS
    mappings_contestations = [
        {'internal_field': 'date_jour', 'column_name': 'DATE DU JOUR', 'is_required': False},
        {'internal_field': 'nom_complet', 'column_name': 'NOM', 'is_required': True},
        {'internal_field': 'urgence', 'column_name': 'PRENOM', 'is_required': False},  # true si "URGENT"
        {'internal_field': 'motif', 'column_name': 'MOTIF', 'is_required': False},
        {'internal_field': 'date_butoir', 'column_name': 'DATE BUTOIR', 'is_required': False},
        {'internal_field': 'typeDemande', 'column_name': '', 'default_value': 'CON', 'is_required': False},
    ]
    
    for mapping_data in mappings_contestations:
        mapping = ImportFieldMapping(
            import_profile_id=profile_contestations.id,
            internal_field=mapping_data['internal_field'],
            column_name=mapping_data.get('column_name'),
            strip_whitespace=True,
            default_value=mapping_data.get('default_value'),
            is_required=mapping_data.get('is_required', False)
        )
        db.session.add(mapping)
    
    logger.info(f"Mappings CONTESTATIONS créés pour le profil {profile_contestations.id}")
    
    # 7. Créer les tarifs CLIENT_X (exemples)
    tarifs_client_x = [
        {'code_lettre': 'A', 'description': 'Tarif A', 'montant': 15.0},
        {'code_lettre': 'B', 'description': 'Tarif B', 'montant': 20.0},
        {'code_lettre': 'C', 'description': 'Tarif C', 'montant': 25.0},
        {'code_lettre': 'D', 'description': 'Tarif D', 'montant': 30.0},
        {'code_lettre': 'E', 'description': 'Tarif E', 'montant': 35.0},
    ]
    
    for tarif_data in tarifs_client_x:
        tarif = TarifClient(
            client_id=client_x.id,
            code_lettre=tarif_data['code_lettre'],
            description=tarif_data['description'],
            montant=tarif_data['montant'],
            date_debut=datetime.now().date(),
            actif=True
        )
        db.session.add(tarif)
    
    logger.info(f"Tarifs CLIENT_X créés")
    
    # Commit final
    db.session.commit()
    logger.info("CLIENT_X ajouté avec succès !")


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        add_client_x()

