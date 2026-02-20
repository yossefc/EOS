"""
Utilitaires pour la gestion des clients.
Permet de recuperer facilement le client par defaut (EOS)
et de gerer le multi-client.
"""
from models import Client, ImportProfile
from flask import current_app
import logging
import re
import unicodedata

logger = logging.getLogger(__name__)

# Cache du client EOS pour eviter les requetes repetees
_eos_client_cache = None
_eos_profile_cache = None


def get_client_by_code(code):
    """
    Recupere un client par son code.

    Args:
        code (str): Code du client (ex: 'EOS', 'CLIENT_B')

    Returns:
        Client: Instance du client ou None si non trouve
    """
    try:
        return Client.query.filter_by(code=code, actif=True).first()
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation du client {code}: {e}")
        return None


def get_client_by_id(client_id):
    """
    Recupere un client par son ID.

    Args:
        client_id (int): ID du client

    Returns:
        Client: Instance du client ou None si non trouve
    """
    try:
        return Client.query.filter_by(id=client_id, actif=True).first()
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation du client ID {client_id}: {e}")
        return None


def get_eos_client():
    """
    Recupere le client EOS par defaut (avec cache).

    Returns:
        Client: Instance du client EOS ou None si non trouve
    """
    global _eos_client_cache

    if _eos_client_cache is None:
        _eos_client_cache = get_client_by_code('EOS')

        if _eos_client_cache is None:
            logger.error("Client EOS non trouve dans la base de donnees")

    return _eos_client_cache


def get_client_or_default(client_id=None, client_code=None):
    """
    Recupere un client specifique ou le client EOS par defaut.

    Args:
        client_id (int, optional): ID du client
        client_code (str, optional): Code du client

    Returns:
        Client: Instance du client ou client EOS par defaut
    """
    if client_id:
        client = get_client_by_id(client_id)
        if client:
            return client
        logger.warning(f"Client ID {client_id} non trouve, utilisation du client EOS par defaut")

    if client_code:
        client = get_client_by_code(client_code)
        if client:
            return client
        logger.warning(f"Client code '{client_code}' non trouve, utilisation du client EOS par defaut")

    return get_eos_client()


def _normalize_hint(value):
    if not value:
        return ""
    text = str(value).strip().upper()
    if not text:
        return ""
    nfd = unicodedata.normalize('NFD', text)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', without_accents)


def _looks_like_contestation_label(value):
    token = _normalize_hint(value)
    if not token:
        return False
    return any(marker in token for marker in ('CONTEST', 'CONTREENQUETE', 'CRCONT'))


def get_import_profile_for_client(client_id, file_type='TXT_FIXED', filename=None, sheet_names=None):
    """
    Recupere le profil d'import pour un client et un type de fichier.

    Si plusieurs profils existent, applique des heuristiques (nom fichier / feuilles)
    pour choisir le bon profil, notamment pour les fichiers contestation.

    Args:
        client_id (int): ID du client
        file_type (str): Type de fichier ('TXT_FIXED', 'EXCEL', etc.)
        filename (str, optional): Nom du fichier importe
        sheet_names (list[str], optional): Noms de feuilles Excel detectees

    Returns:
        ImportProfile: Instance du profil d'import ou None
    """
    try:
        profiles = ImportProfile.query.filter_by(
            client_id=client_id,
            file_type=file_type,
            actif=True
        ).order_by(ImportProfile.id.asc()).all()

        if not profiles:
            return None

        if len(profiles) == 1:
            return profiles[0]

        filename_token = _normalize_hint(filename)
        contestation_by_filename = _looks_like_contestation_label(filename)

        if contestation_by_filename:
            for profile in profiles:
                if (
                    _looks_like_contestation_label(profile.name) or
                    _looks_like_contestation_label(profile.sheet_name)
                ):
                    logger.info(
                        f"Profil d'import selectionne (contestation) via nom fichier '{filename}': {profile.name}"
                    )
                    return profile

        normalized_sheets = {_normalize_hint(sheet) for sheet in (sheet_names or []) if sheet}
        if normalized_sheets:
            for profile in profiles:
                profile_sheet = _normalize_hint(profile.sheet_name)
                if profile_sheet and profile_sheet in normalized_sheets:
                    logger.info(
                        f"Profil d'import selectionne via feuille '{profile.sheet_name}': {profile.name}"
                    )
                    return profile

        if filename_token:
            for profile in profiles:
                profile_name_token = _normalize_hint(profile.name)
                if profile_name_token and profile_name_token in filename_token:
                    logger.info(
                        f"Profil d'import selectionne via rapprochement nom fichier/profil '{filename}': {profile.name}"
                    )
                    return profile

        for profile in profiles:
            if not (
                _looks_like_contestation_label(profile.name) or
                _looks_like_contestation_label(profile.sheet_name)
            ):
                return profile

        return profiles[0]
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation du profil d'import: {e}")
        return None


def get_eos_import_profile():
    """
    Recupere le profil d'import EOS par defaut (avec cache).

    Returns:
        ImportProfile: Instance du profil d'import EOS ou None
    """
    global _eos_profile_cache

    if _eos_profile_cache is None:
        eos_client = get_eos_client()
        if eos_client:
            _eos_profile_cache = get_import_profile_for_client(eos_client.id, 'TXT_FIXED')

            if _eos_profile_cache is None:
                logger.error("Profil d'import EOS non trouve dans la base de donnees")

    return _eos_profile_cache


def get_all_active_clients():
    """
    Recupere tous les clients actifs.

    Returns:
        list[Client]: Liste des clients actifs
    """
    try:
        return Client.query.filter_by(actif=True).all()
    except Exception as e:
        logger.error(f"Erreur lors de la recuperation des clients actifs: {e}")
        return []


def clear_client_cache():
    """
    Vide le cache des clients (utile apres modifications en base).
    """
    global _eos_client_cache, _eos_profile_cache
    _eos_client_cache = None
    _eos_profile_cache = None
    logger.info("Cache des clients vide")
