"""
Utilitaires pour la gestion des clients
Permet de récupérer facilement le client par défaut (EOS) et gérer le multi-client
"""
from models import Client, ImportProfile
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Cache du client EOS pour éviter les requêtes répétées
_eos_client_cache = None
_eos_profile_cache = None


def get_client_by_code(code):
    """
    Récupère un client par son code
    
    Args:
        code (str): Code du client (ex: 'EOS', 'CLIENT_B')
        
    Returns:
        Client: Instance du client ou None si non trouvé
    """
    try:
        return Client.query.filter_by(code=code, actif=True).first()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du client {code}: {e}")
        return None


def get_client_by_id(client_id):
    """
    Récupère un client par son ID
    
    Args:
        client_id (int): ID du client
        
    Returns:
        Client: Instance du client ou None si non trouvé
    """
    try:
        return Client.query.filter_by(id=client_id, actif=True).first()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du client ID {client_id}: {e}")
        return None


def get_eos_client():
    """
    Récupère le client EOS par défaut (avec cache)
    
    Returns:
        Client: Instance du client EOS ou None si non trouvé
    """
    global _eos_client_cache
    
    if _eos_client_cache is None:
        _eos_client_cache = get_client_by_code('EOS')
        
        if _eos_client_cache is None:
            logger.error("Client EOS non trouvé dans la base de données!")
    
    return _eos_client_cache


def get_client_or_default(client_id=None, client_code=None):
    """
    Récupère un client spécifique ou le client EOS par défaut
    
    Args:
        client_id (int, optional): ID du client
        client_code (str, optional): Code du client
        
    Returns:
        Client: Instance du client ou client EOS par défaut
    """
    if client_id:
        client = get_client_by_id(client_id)
        if client:
            return client
        logger.warning(f"Client ID {client_id} non trouvé, utilisation du client EOS par défaut")
    
    if client_code:
        client = get_client_by_code(client_code)
        if client:
            return client
        logger.warning(f"Client code '{client_code}' non trouvé, utilisation du client EOS par défaut")
    
    return get_eos_client()


def get_import_profile_for_client(client_id, file_type='TXT_FIXED'):
    """
    Récupère le profil d'import pour un client et un type de fichier
    
    Args:
        client_id (int): ID du client
        file_type (str): Type de fichier ('TXT_FIXED', 'EXCEL', etc.)
        
    Returns:
        ImportProfile: Instance du profil d'import ou None
    """
    try:
        return ImportProfile.query.filter_by(
            client_id=client_id,
            file_type=file_type,
            actif=True
        ).first()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil d'import: {e}")
        return None


def get_eos_import_profile():
    """
    Récupère le profil d'import EOS par défaut (avec cache)
    
    Returns:
        ImportProfile: Instance du profil d'import EOS ou None
    """
    global _eos_profile_cache
    
    if _eos_profile_cache is None:
        eos_client = get_eos_client()
        if eos_client:
            _eos_profile_cache = get_import_profile_for_client(eos_client.id, 'TXT_FIXED')
            
            if _eos_profile_cache is None:
                logger.error("Profil d'import EOS non trouvé dans la base de données!")
    
    return _eos_profile_cache


def get_all_active_clients():
    """
    Récupère tous les clients actifs
    
    Returns:
        list[Client]: Liste des clients actifs
    """
    try:
        return Client.query.filter_by(actif=True).all()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des clients actifs: {e}")
        return []


def clear_client_cache():
    """
    Vide le cache des clients (utile après modifications en base)
    """
    global _eos_client_cache, _eos_profile_cache
    _eos_client_cache = None
    _eos_profile_cache = None
    logger.info("Cache des clients vidé")


