"""
Script d'import des donnees de l'ancien programme (enci) vers le nouveau systeme EOS
Ce script importe les enquetes, reponses, et contestations des fichiers Excel
"""

import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal

# Configuration de l'environnement
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client
from models.enqueteur import Enqueteur

# Chemin vers les fichiers Excel
ENCI_DIR = os.path.join(os.path.dirname(__file__), '..', 'enci', 'sample')

# Mapping des codes clients anciens vers les nouveaux
CLIENT_MAPPING = {
    'EOS': 'EOS',
    'eos': 'EOS',
    'cr': 'PARTNER',  # Ancien code pour PARTNER
    'CR': 'PARTNER',
    'crcont': 'PARTNER',  # Contestations PARTNER
    'CRCONT': 'PARTNER',
    'partner': 'PARTNER',
    'PARTNER': 'PARTNER',
    'rg': 'RG_SHERLOCK',  # Ancien code pour RG Sherlock
    'RG': 'RG_SHERLOCK',
    'sherlock': 'RG_SHERLOCK',
    'SHERLOCK': 'RG_SHERLOCK',
    'RG_SHERLOCK': 'RG_SHERLOCK',
}

def parse_date(date_str):
    """Parse une date depuis differents formats"""
    if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
        return None

    date_str = str(date_str).strip()

    # Formats a essayer
    formats = [
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Essayer juste l'annee
    try:
        if len(date_str) == 4 and date_str.isdigit():
            return datetime(int(date_str), 1, 1).date()
    except:
        pass

    return None

def parse_decimal(value):
    """Parse une valeur decimale"""
    if pd.isna(value) or value == '':
        return None
    try:
        return Decimal(str(value))
    except:
        return None

def clean_string(value, max_length=None):
    """Nettoie une chaine de caracteres"""
    if pd.isna(value) or value is None:
        return None
    value = str(value).strip()
    if value.lower() in ('nan', 'none', ''):
        return None
    if max_length:
        value = value[:max_length]
    return value

def get_or_create_enqueteur(nom, prenom=None, app_context=None):
    """Recupere ou cree un enqueteur par nom"""
    if not nom:
        return None

    nom = clean_string(nom, 100)
    if not nom:
        return None

    # Chercher par nom
    enqueteur = Enqueteur.query.filter(
        db.func.upper(Enqueteur.nom) == nom.upper()
    ).first()

    if enqueteur:
        return enqueteur.id

    # Creer un nouvel enqueteur si necessaire
    prenom = clean_string(prenom, 100) or 'Import'
    email = f"{nom.lower().replace(' ', '.')}@import.enci.local"

    # Verifier que l'email n'existe pas deja
    existing = Enqueteur.query.filter_by(email=email).first()
    if existing:
        return existing.id

    new_enqueteur = Enqueteur(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=''
    )
    db.session.add(new_enqueteur)
    db.session.flush()  # Pour obtenir l'ID
    print(f"  Nouvel enqueteur cree: {nom} (ID={new_enqueteur.id})")
    return new_enqueteur.id

def import_requetes(app):
    """Importe les requetes (enquetes) de l'ancien programme"""
    print("\n=== IMPORT DES REQUETES (ENQUETES) ===")

    requetes_file = os.path.join(ENCI_DIR, 'requetes.xlsx')
    if not os.path.exists(requetes_file):
        print(f"Fichier non trouve: {requetes_file}")
        return {}

    df = pd.read_excel(requetes_file)
    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        # Charger les clients existants
        clients = {c.code.upper(): c.id for c in Client.query.all()}
        print(f"Clients disponibles: {list(clients.keys())}")

        # Creer un fichier "import" pour regrouper les donnees importees
        import_files = {}

        imported = 0
        skipped = 0
        id_mapping = {}  # Mapping ancien ID -> nouveau ID

        for idx, row in df.iterrows():
            try:
                # Determiner le client
                old_client = clean_string(row.get('client', ''), 50)
                if not old_client:
                    old_client = 'EOS'

                # Mapper vers le nouveau client
                new_client_code = CLIENT_MAPPING.get(old_client, CLIENT_MAPPING.get(old_client.upper(), 'EOS'))
                client_id = clients.get(new_client_code.upper())

                if not client_id:
                    print(f"  Ligne {idx}: Client inconnu '{old_client}' -> skip")
                    skipped += 1
                    continue

                # Creer ou recuperer le fichier d'import pour ce client
                if client_id not in import_files:
                    fichier = Fichier(
                        client_id=client_id,
                        nom=f"Import ENCI - {new_client_code} - {datetime.now().strftime('%Y%m%d')}",
                        chemin=ENCI_DIR,
                        date_upload=datetime.now()
                    )
                    db.session.add(fichier)
                    db.session.flush()
                    import_files[client_id] = fichier.id
                    print(f"  Fichier d'import cree pour {new_client_code} (ID={fichier.id})")

                fichier_id = import_files[client_id]

                # Recuperer ou creer l'enqueteur
                enqueteur_id = get_or_create_enqueteur(
                    clean_string(row.get('enqueteur'), 100)
                )

                # Creer la donnee (enquete)
                donnee = Donnee(
                    client_id=client_id,
                    fichier_id=fichier_id,
                    enqueteurId=enqueteur_id,

                    # Identifiants
                    numeroDossier=clean_string(row.get('noDossier'), 10),
                    referenceDossier=clean_string(row.get('referenceDossier'), 15),
                    numeroInterlocuteur=clean_string(row.get('numerointerlocuteur'), 12),
                    guidInterlocuteur=clean_string(row.get('guidinterlocuteur'), 36),

                    # Type de demande
                    typeDemande=clean_string(row.get('typededemandeenquete'), 3),
                    numeroDemande=clean_string(row.get('numerodemandeenquete'), 11),
                    numeroDemandeContestee=clean_string(row.get('numerodemandeenquetecontestee'), 11),
                    numeroDemandeInitiale=clean_string(row.get('numerodemandeenqueteinitiale'), 11),
                    forfaitDemande=clean_string(row.get('forfaitdemande'), 16),

                    # Dates
                    dateRetourEspere=parse_date(row.get('datederetouresperee')),
                    datedenvoie=parse_date(row.get('dateenvoi')),
                    date_butoir=parse_date(row.get('datederetour')),

                    # Etat civil
                    qualite=clean_string(row.get('qualite'), 10),
                    nom=clean_string(row.get('nom'), 30),
                    prenom=clean_string(row.get('prenom'), 20),
                    dateNaissance=parse_date(row.get('datedenaissance')),
                    lieuNaissance=clean_string(row.get('lieudenaissance'), 50),
                    codePostalNaissance=clean_string(row.get('codepostalnaissance'), 10),
                    paysNaissance=clean_string(row.get('paysdenaissance'), 32),
                    nomPatronymique=clean_string(row.get('nompatronymique'), 30),

                    # Adresse
                    adresse1=clean_string(row.get('adresse1'), 255),
                    adresse2=clean_string(row.get('adresse2'), 255),
                    adresse3=clean_string(row.get('adresse3'), 255),
                    adresse4=clean_string(row.get('adresse4'), 255),
                    ville=clean_string(row.get('ville'), 50),
                    codePostal=clean_string(row.get('codepostal'), 10),
                    paysResidence=clean_string(row.get('pays'), 32),

                    # Telephone/Employeur
                    telephonePersonnel=clean_string(row.get('telephonepersonnel'), 15),
                    telephoneEmployeur=clean_string(row.get('telephoneemployeur'), 15),
                    telecopieEmployeur=clean_string(row.get('telecopieemployeur'), 15),
                    nomEmployeur=clean_string(row.get('nomemployeur'), 32),

                    # Banque
                    banqueDomiciliation=clean_string(row.get('banquedomiciliation'), 32),
                    libelleGuichet=clean_string(row.get('libelleguichet'), 30),
                    titulaireCompte=clean_string(row.get('titulaireducompte'), 32),
                    codeBanque=clean_string(row.get('codebanque'), 5),
                    codeGuichet=clean_string(row.get('codeguichet'), 5),
                    numeroCompte=clean_string(row.get('exnumerodecompte'), 11),
                    ribCompte=clean_string(row.get('exribdecompte'), 2),

                    # Elements demandes
                    elementDemandes=clean_string(row.get('elementsdemandes'), 10),
                    elementObligatoires=clean_string(row.get('elementsobligatoires'), 10),
                    elementContestes=clean_string(row.get('elementscontestes'), 10),
                    codeMotif=clean_string(row.get('codemotifdecontestation'), 16),
                    motifDeContestation=clean_string(row.get('motifdecontestation'), 64),

                    # Autres
                    cumulMontantsPrecedents=parse_decimal(row.get('cumuldesmontantsprecedemmentfactures')),
                    codesociete=clean_string(row.get('codesociete'), 2),
                    urgence=clean_string(row.get('urgence'), 1),
                    commentaire=clean_string(row.get('commentaires'), 1000),

                    # Statut
                    statut_validation='valide' if row.get('retourne') else 'en_attente',

                    # Contestation?
                    est_contestation=(str(row.get('typededemandeenquete', '')).upper() == 'CON'),
                )

                db.session.add(donnee)
                db.session.flush()

                # Sauvegarder le mapping d'ID
                old_id = row.get('ID')
                if pd.notna(old_id):
                    id_mapping[int(old_id)] = donnee.id

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} enquetes importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} enquetes importees, {skipped} ignorees")
        return id_mapping

def import_reponses(app, id_mapping):
    """Importe les reponses des enqueteurs"""
    print("\n=== IMPORT DES REPONSES ===")

    reponses_file = os.path.join(ENCI_DIR, 'reponsesrequetes.xlsx')
    if not os.path.exists(reponses_file):
        print(f"Fichier non trouve: {reponses_file}")
        return

    df = pd.read_excel(reponses_file)
    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        # Charger les clients existants
        clients = {c.code.upper(): c.id for c in Client.query.all()}

        imported = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Trouver l'enquete correspondante
                old_requete_id = row.get('IDrequete')
                if pd.isna(old_requete_id):
                    skipped += 1
                    continue

                old_requete_id = int(old_requete_id)
                donnee_id = id_mapping.get(old_requete_id)

                if not donnee_id:
                    # Essayer de trouver par numero de dossier
                    no_dossier = clean_string(row.get('noDossier'), 10)
                    if no_dossier:
                        donnee = Donnee.query.filter_by(numeroDossier=no_dossier).first()
                        if donnee:
                            donnee_id = donnee.id

                    if not donnee_id:
                        skipped += 1
                        continue

                # Recuperer la donnee pour avoir le client_id
                donnee = db.session.get(Donnee, donnee_id)
                if not donnee:
                    skipped += 1
                    continue

                # Mapper le code resultat
                status_address = clean_string(row.get('statusaddress'), 1)
                status_telephone = clean_string(row.get('statustelephone'), 1)
                status_banque = clean_string(row.get('statusbanque'), 1)

                # Determiner le code resultat global
                code_resultat = None
                if status_address == 'P' or status_telephone == 'P' or status_banque == 'P':
                    code_resultat = 'P'  # Positif
                elif status_address == 'N' or status_telephone == 'N' or status_banque == 'N':
                    code_resultat = 'N'  # Negatif

                # Creer la reponse enqueteur
                donnee_enqueteur = DonneeEnqueteur(
                    client_id=donnee.client_id,
                    donnee_id=donnee_id,

                    code_resultat=code_resultat,
                    elements_retrouves=clean_string(row.get('elementdemande'), 10),
                    date_retour=parse_date(row.get('datetraitement')),

                    # Adresse
                    adresse1=clean_string(row.get('adresse1'), 32),
                    adresse2=clean_string(row.get('adresse2'), 32),
                    adresse3=clean_string(row.get('adresse3'), 32),
                    adresse4=clean_string(row.get('adresse4'), 32),
                    code_postal=clean_string(row.get('adressecp'), 10),
                    ville=clean_string(row.get('adresseville'), 32),
                    pays_residence=clean_string(row.get('adressepays'), 32),

                    # Telephone
                    telephone_personnel=clean_string(row.get('telephone'), 15),

                    # Employeur
                    nom_employeur=clean_string(row.get('employeurnom'), 32),
                    telephone_employeur=clean_string(row.get('employeurtelephone'), 15),
                    adresse1_employeur=clean_string(row.get('empadr1'), 32),
                    adresse2_employeur=clean_string(row.get('empadr2'), 32),
                    adresse3_employeur=clean_string(row.get('empadr3'), 32),
                    adresse4_employeur=clean_string(row.get('empadr4'), 32),
                    code_postal_employeur=clean_string(row.get('empcp'), 10),
                    ville_employeur=clean_string(row.get('empville'), 32),
                    pays_employeur=clean_string(row.get('emppays'), 32),

                    # Banque
                    code_banque=clean_string(row.get('banquecode'), 5),
                    code_guichet=clean_string(row.get('banqueguichet'), 5),
                    banque_domiciliation=clean_string(row.get('banquedomiciliation'), 32),

                    # Deces
                    date_deces=parse_date(row.get('decesdate')),
                    numero_acte_deces=clean_string(row.get('decesnumeroacte'), 10),
                    code_insee_deces=clean_string(row.get('decescodeinsee'), 5),
                    code_postal_deces=clean_string(row.get('decescp'), 10),
                    localite_deces=clean_string(row.get('deceslocalite'), 32),

                    # Revenus
                    commentaires_revenus=clean_string(row.get('revenucommentaire'), 128),
                    montant_salaire=parse_decimal(row.get('revenusalaire')),
                    nature_revenu1=clean_string(row.get('revenu1nature'), 30),
                    montant_revenu1=parse_decimal(row.get('revenu1montant')),
                    nature_revenu2=clean_string(row.get('revenu2nature'), 30),
                    montant_revenu2=parse_decimal(row.get('revenu2montant')),
                    nature_revenu3=clean_string(row.get('revenu3nature'), 30),
                    montant_revenu3=parse_decimal(row.get('revenu3montant')),
                )

                db.session.add(donnee_enqueteur)

                # Mettre a jour le statut de l'enquete
                if code_resultat:
                    donnee.statut_validation = 'valide'

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} reponses importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} reponses importees, {skipped} ignorees")

def import_autres_clients(app):
    """Importe les requetes d'autres clients (autresclients.xlsx)"""
    print("\n=== IMPORT AUTRES CLIENTS ===")

    autres_file = os.path.join(ENCI_DIR, 'autresclients.xlsx')
    if not os.path.exists(autres_file):
        print(f"Fichier non trouve: {autres_file}")
        return {}

    df = pd.read_excel(autres_file)
    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        clients = {c.code.upper(): c.id for c in Client.query.all()}
        print(f"Clients disponibles: {list(clients.keys())}")

        import_files = {}
        imported = 0
        skipped = 0
        id_mapping = {}

        for idx, row in df.iterrows():
            try:
                # Determiner le client
                old_client = clean_string(row.get('client', ''), 50)
                if not old_client:
                    old_client = 'PARTNER'

                new_client_code = CLIENT_MAPPING.get(old_client, CLIENT_MAPPING.get(old_client.upper(), 'PARTNER'))
                client_id = clients.get(new_client_code.upper())

                if not client_id:
                    # Essayer de deviner le client par le code
                    if 'rg' in old_client.lower() or 'sherlock' in old_client.lower():
                        client_id = clients.get('RG_SHERLOCK')
                        print(f"  Ligne {idx}: Client '{old_client}' -> RG_SHERLOCK")
                    elif 'cr' in old_client.lower() or 'partner' in old_client.lower():
                        client_id = clients.get('PARTNER')
                        print(f"  Ligne {idx}: Client '{old_client}' -> PARTNER")
                    else:
                        client_id = clients.get('EOS')
                        print(f"  Ligne {idx}: Client inconnu '{old_client}' -> EOS par defaut")

                if not client_id:
                    skipped += 1
                    continue

                # Creer ou recuperer le fichier d'import
                file_key = f"autres_{client_id}"
                if file_key not in import_files:
                    fichier = Fichier(
                        client_id=client_id,
                        nom=f"Import ENCI Autres - {new_client_code} - {datetime.now().strftime('%Y%m%d')}",
                        chemin=ENCI_DIR,
                        date_upload=datetime.now()
                    )
                    db.session.add(fichier)
                    db.session.flush()
                    import_files[file_key] = fichier.id

                fichier_id = import_files[file_key]

                # Recuperer ou creer l'enqueteur
                enqueteur_id = get_or_create_enqueteur(
                    clean_string(row.get('enqueteur'), 100)
                )

                # Parser les elements demandes
                elements = clean_string(row.get('elementsdemandes'), 255)
                if elements and 'ENQ:' in elements:
                    elements = elements.replace('ENQ:', '').replace('/', '')

                # Creer la donnee
                donnee = Donnee(
                    client_id=client_id,
                    fichier_id=fichier_id,
                    enqueteurId=enqueteur_id,

                    numeroDossier=clean_string(str(row.get('dossier', '')), 10),
                    nom=clean_string(row.get('nom'), 30),
                    prenom=clean_string(row.get('prenom'), 20),
                    dateNaissance=parse_date(row.get('datenaissance')),
                    lieuNaissance=clean_string(row.get('lieunaissance'), 50),
                    codePostalNaissance=clean_string(row.get('codepostalnaissance'), 10),
                    paysNaissance=clean_string(row.get('paysnaissance'), 32),

                    datedenvoie=parse_date(row.get('dateenvoi')),
                    elementDemandes=clean_string(elements, 10),

                    statut_validation='valide' if row.get('valide') else 'en_attente',
                    est_contestation=False,

                    # Champs specifiques PARTNER
                    instructions=clean_string(row.get('memointerne'), 1000),
                )

                db.session.add(donnee)
                db.session.flush()

                # Sauvegarder le mapping
                old_id = row.get('ID')
                if pd.notna(old_id):
                    id_mapping[int(old_id)] = donnee.id

                # Si on a des reponses dans champreponses, creer une DonneeEnqueteur
                champreponses = clean_string(row.get('champreponses'), 5000)
                if champreponses and row.get('valide'):
                    code_resultat = 'P' if row.get('validepositif') else ('N' if row.get('validenegatif') else None)

                    donnee_enqueteur = DonneeEnqueteur(
                        client_id=client_id,
                        donnee_id=donnee.id,
                        code_resultat=code_resultat,
                        date_retour=parse_date(row.get('datetraitement')),
                        montant_facture=parse_decimal(row.get('montantfacture')),
                        notes_personnelles=champreponses[:1000] if champreponses else None,
                    )
                    db.session.add(donnee_enqueteur)

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} enquetes autres clients importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} enquetes importees, {skipped} ignorees")
        return id_mapping

def import_requetes_retournees(app, existing_mapping):
    """Importe les requetes retournees/archivees"""
    print("\n=== IMPORT DES REQUETES RETOURNEES (ARCHIVES EOS) ===")

    retournees_file = os.path.join(ENCI_DIR, 'requetesretournees.xlsx')
    if not os.path.exists(retournees_file):
        print(f"Fichier non trouve: {retournees_file}")
        return existing_mapping

    df = pd.read_excel(retournees_file)
    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        clients = {c.code.upper(): c.id for c in Client.query.all()}
        import_files = {}
        imported = 0
        skipped = 0
        id_mapping = existing_mapping.copy()

        for idx, row in df.iterrows():
            try:
                # Determiner le client (EOS par defaut pour ce fichier)
                old_client = clean_string(row.get('client', ''), 50) or 'EOS'
                new_client_code = CLIENT_MAPPING.get(old_client, CLIENT_MAPPING.get(old_client.upper(), 'EOS'))
                client_id = clients.get(new_client_code.upper())

                if not client_id:
                    client_id = clients.get('EOS')

                # Verifier si deja importe (par ID ou numero de dossier)
                old_id = row.get('ID')
                if pd.notna(old_id) and int(old_id) in id_mapping:
                    skipped += 1
                    continue

                no_dossier = clean_string(row.get('noDossier'), 10)
                if no_dossier:
                    existing = Donnee.query.filter_by(numeroDossier=no_dossier, client_id=client_id).first()
                    if existing:
                        if pd.notna(old_id):
                            id_mapping[int(old_id)] = existing.id
                        skipped += 1
                        continue

                # Creer fichier d'import
                file_key = f"retournees_{client_id}"
                if file_key not in import_files:
                    fichier = Fichier(
                        client_id=client_id,
                        nom=f"Import ENCI Archives - {new_client_code} - {datetime.now().strftime('%Y%m%d')}",
                        chemin=ENCI_DIR,
                        date_upload=datetime.now()
                    )
                    db.session.add(fichier)
                    db.session.flush()
                    import_files[file_key] = fichier.id

                fichier_id = import_files[file_key]

                # Recuperer enqueteur
                enqueteur_id = get_or_create_enqueteur(clean_string(row.get('enqueteur'), 100))

                # Determiner si c'est une contestation
                type_demande = clean_string(row.get('typededemandeenquete'), 3)
                est_contestation = (type_demande and type_demande.upper() == 'CON')

                # Creer la donnee
                donnee = Donnee(
                    client_id=client_id,
                    fichier_id=fichier_id,
                    enqueteurId=enqueteur_id,

                    numeroDossier=no_dossier,
                    referenceDossier=clean_string(row.get('referenceDossier'), 15),
                    numeroInterlocuteur=clean_string(row.get('numerointerlocuteur'), 12),
                    guidInterlocuteur=clean_string(row.get('guidinterlocuteur'), 36),

                    typeDemande=type_demande,
                    numeroDemande=clean_string(row.get('numerodemandeenquete'), 11),
                    numeroDemandeContestee=clean_string(row.get('numerodemandeenquetecontestee'), 11),
                    numeroDemandeInitiale=clean_string(row.get('numerodemandeenqueteinitiale'), 11),
                    forfaitDemande=clean_string(row.get('forfaitdemande'), 16),

                    dateRetourEspere=parse_date(row.get('datederetouresperee')),
                    datedenvoie=parse_date(row.get('dateenvoi')),
                    date_butoir=parse_date(row.get('datederetour')),

                    qualite=clean_string(row.get('qualite'), 10),
                    nom=clean_string(row.get('nom'), 30),
                    prenom=clean_string(row.get('prenom'), 20),
                    dateNaissance=parse_date(row.get('datedenaissance')),
                    lieuNaissance=clean_string(row.get('lieudenaissance'), 50),
                    codePostalNaissance=clean_string(row.get('codepostalnaissance'), 10),
                    paysNaissance=clean_string(row.get('paysdenaissance'), 32),
                    nomPatronymique=clean_string(row.get('nompatronymique'), 30),

                    adresse1=clean_string(row.get('adresse1'), 255),
                    adresse2=clean_string(row.get('adresse2'), 255),
                    adresse3=clean_string(row.get('adresse3'), 255),
                    adresse4=clean_string(row.get('adresse4'), 255),
                    ville=clean_string(row.get('ville'), 50),
                    codePostal=clean_string(row.get('codepostal'), 10),
                    paysResidence=clean_string(row.get('pays'), 32),

                    telephonePersonnel=clean_string(row.get('telephonepersonnel'), 15),
                    nomEmployeur=clean_string(row.get('nomemployeur'), 32),

                    elementDemandes=clean_string(row.get('elementsdemandes'), 10),
                    elementObligatoires=clean_string(row.get('elementsobligatoires'), 10),
                    elementContestes=clean_string(row.get('elementscontestes'), 10),
                    codeMotif=clean_string(row.get('codemotifdecontestation'), 16),
                    motifDeContestation=clean_string(row.get('motifdecontestation'), 64),

                    codesociete=clean_string(row.get('codesociete'), 2),
                    urgence=clean_string(row.get('urgence'), 1),
                    commentaire=clean_string(row.get('commentaires'), 1000),

                    statut_validation='valide',  # Archives = deja traitees
                    est_contestation=est_contestation,
                    exported=True,  # Marquer comme deja exporte
                )

                db.session.add(donnee)
                db.session.flush()

                if pd.notna(old_id):
                    id_mapping[int(old_id)] = donnee.id

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} enquetes archivees importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} enquetes archivees importees, {skipped} ignorees/doublons")
        return id_mapping


def import_autres_clients_retournees(app):
    """Importe les requetes retournees d'autres clients (archives PARTNER/RG)"""
    print("\n=== IMPORT AUTRES CLIENTS RETOURNEES (ARCHIVES) ===")

    retournees_file = os.path.join(ENCI_DIR, 'autresclientsretournees.xlsx')
    if not os.path.exists(retournees_file):
        print(f"Fichier non trouve: {retournees_file}")
        return {}

    df = pd.read_excel(retournees_file)
    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        clients = {c.code.upper(): c.id for c in Client.query.all()}
        import_files = {}
        imported = 0
        skipped = 0
        id_mapping = {}

        for idx, row in df.iterrows():
            try:
                # Determiner le client
                old_client = clean_string(row.get('client', ''), 50) or 'PARTNER'

                # Detecter les contestations par le code client
                est_contestation = 'cont' in old_client.lower()

                new_client_code = CLIENT_MAPPING.get(old_client, CLIENT_MAPPING.get(old_client.upper(), 'PARTNER'))
                client_id = clients.get(new_client_code.upper())

                if not client_id:
                    if 'rg' in old_client.lower():
                        client_id = clients.get('RG_SHERLOCK')
                    else:
                        client_id = clients.get('PARTNER', clients.get('EOS'))

                # Verifier doublons
                no_dossier = clean_string(str(row.get('dossier', '')), 10)
                nom = clean_string(row.get('nom'), 30)
                if no_dossier and nom:
                    existing = Donnee.query.filter_by(
                        numeroDossier=no_dossier,
                        client_id=client_id,
                        nom=nom
                    ).first()
                    if existing:
                        skipped += 1
                        continue

                # Creer fichier d'import
                file_key = f"autres_retournees_{client_id}"
                if file_key not in import_files:
                    fichier = Fichier(
                        client_id=client_id,
                        nom=f"Import ENCI Archives Autres - {new_client_code} - {datetime.now().strftime('%Y%m%d')}",
                        chemin=ENCI_DIR,
                        date_upload=datetime.now()
                    )
                    db.session.add(fichier)
                    db.session.flush()
                    import_files[file_key] = fichier.id

                fichier_id = import_files[file_key]

                # Recuperer enqueteur
                enqueteur_id = get_or_create_enqueteur(clean_string(row.get('enqueteur'), 100))

                # Parser elements demandes
                elements = clean_string(row.get('elementsdemandes'), 255)
                if elements and 'ENQ:' in elements:
                    elements = elements.replace('ENQ:', '').replace('/', '')

                # Creer la donnee
                donnee = Donnee(
                    client_id=client_id,
                    fichier_id=fichier_id,
                    enqueteurId=enqueteur_id,

                    numeroDossier=no_dossier,
                    nom=nom,
                    prenom=clean_string(row.get('prenom'), 20),
                    dateNaissance=parse_date(row.get('datenaissance')),
                    lieuNaissance=clean_string(row.get('lieunaissance'), 50),
                    codePostalNaissance=clean_string(row.get('codepostalnaissance'), 10),
                    paysNaissance=clean_string(row.get('paysnaissance'), 32),

                    datedenvoie=parse_date(row.get('dateenvoi')),
                    elementDemandes=clean_string(elements, 10),

                    statut_validation='valide',  # Archives = deja traitees
                    est_contestation=est_contestation,
                    exported=True,

                    instructions=clean_string(row.get('memointerne'), 1000),
                )

                db.session.add(donnee)
                db.session.flush()

                old_id = row.get('ID')
                if pd.notna(old_id):
                    id_mapping[int(old_id)] = donnee.id

                # Creer DonneeEnqueteur si reponses
                champreponses = clean_string(row.get('champreponses'), 5000)
                if champreponses or row.get('valide'):
                    code_resultat = 'P' if row.get('validepositif') else ('N' if row.get('validenegatif') else None)

                    donnee_enqueteur = DonneeEnqueteur(
                        client_id=client_id,
                        donnee_id=donnee.id,
                        code_resultat=code_resultat,
                        date_retour=parse_date(row.get('datetraitement')),
                        date_facture=parse_date(row.get('datefacture')),
                        montant_facture=parse_decimal(row.get('montantfacture')),
                        notes_personnelles=champreponses[:1000] if champreponses else None,
                    )
                    db.session.add(donnee_enqueteur)

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} enquetes autres clients archivees importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} enquetes archivees importees, {skipped} ignorees/doublons")
        return id_mapping


def import_reponses_retournees(app, id_mapping):
    """Importe les reponses retournees (archives)"""
    print("\n=== IMPORT DES REPONSES RETOURNEES (ARCHIVES) ===")

    reponses_file = os.path.join(ENCI_DIR, 'reponsesrequetesretournees.xlsx')
    if not os.path.exists(reponses_file):
        print(f"Fichier non trouve: {reponses_file}")
        return

    try:
        df = pd.read_excel(reponses_file)
    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
        return

    print(f"Fichier lu: {len(df)} lignes")

    with app.app_context():
        clients = {c.code.upper(): c.id for c in Client.query.all()}
        imported = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Trouver l'enquete correspondante
                old_requete_id = row.get('IDrequete')
                donnee_id = None

                if pd.notna(old_requete_id):
                    donnee_id = id_mapping.get(int(old_requete_id))

                if not donnee_id:
                    no_dossier = clean_string(row.get('noDossier'), 10)
                    if no_dossier:
                        donnee = Donnee.query.filter_by(numeroDossier=no_dossier).first()
                        if donnee:
                            donnee_id = donnee.id

                if not donnee_id:
                    skipped += 1
                    continue

                # Verifier si reponse existe deja
                existing = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
                if existing:
                    skipped += 1
                    continue

                donnee = db.session.get(Donnee, donnee_id)
                if not donnee:
                    skipped += 1
                    continue

                # Code resultat
                status_address = clean_string(row.get('statusaddress'), 1)
                status_telephone = clean_string(row.get('statustelephone'), 1)
                code_resultat = None
                if status_address == 'P' or status_telephone == 'P':
                    code_resultat = 'P'
                elif status_address == 'N' or status_telephone == 'N':
                    code_resultat = 'N'

                donnee_enqueteur = DonneeEnqueteur(
                    client_id=donnee.client_id,
                    donnee_id=donnee_id,
                    code_resultat=code_resultat,
                    elements_retrouves=clean_string(row.get('elementdemande'), 10),
                    date_retour=parse_date(row.get('datetraitement')),

                    adresse1=clean_string(row.get('adresse1'), 32),
                    adresse2=clean_string(row.get('adresse2'), 32),
                    adresse3=clean_string(row.get('adresse3'), 32),
                    adresse4=clean_string(row.get('adresse4'), 32),
                    code_postal=clean_string(row.get('adressecp'), 10),
                    ville=clean_string(row.get('adresseville'), 32),
                    pays_residence=clean_string(row.get('adressepays'), 32),

                    telephone_personnel=clean_string(row.get('telephone'), 15),

                    nom_employeur=clean_string(row.get('employeurnom'), 32),
                    telephone_employeur=clean_string(row.get('employeurtelephone'), 15),
                    adresse1_employeur=clean_string(row.get('empadr1'), 32),
                    code_postal_employeur=clean_string(row.get('empcp'), 10),
                    ville_employeur=clean_string(row.get('empville'), 32),

                    code_banque=clean_string(row.get('banquecode'), 5),
                    code_guichet=clean_string(row.get('banqueguichet'), 5),
                    banque_domiciliation=clean_string(row.get('banquedomiciliation'), 32),

                    date_deces=parse_date(row.get('decesdate')),
                    numero_acte_deces=clean_string(row.get('decesnumeroacte'), 10),
                    localite_deces=clean_string(row.get('deceslocalite'), 32),

                    commentaires_revenus=clean_string(row.get('revenucommentaire'), 128),
                )

                db.session.add(donnee_enqueteur)

                imported += 1
                if imported % 20 == 0:
                    print(f"  {imported} reponses archivees importees...")
                    db.session.commit()

            except Exception as e:
                print(f"  Erreur ligne {idx}: {e}")
                skipped += 1
                continue

        db.session.commit()
        print(f"\nResultat: {imported} reponses archivees importees, {skipped} ignorees/doublons")


def main():
    """Point d'entree principal"""
    print("=" * 60)
    print("IMPORT DES DONNEES ENCI VERS LE NOUVEAU SYSTEME EOS")
    print("=" * 60)

    app = create_app()

    # Etape 1: Importer les requetes principales (client EOS)
    id_mapping = import_requetes(app)

    # Etape 2: Importer les reponses liees aux requetes
    import_reponses(app, id_mapping)

    # Etape 3: Importer les requetes d'autres clients
    autres_mapping = import_autres_clients(app)

    # Etape 4: Importer les requetes retournees/archivees EOS
    id_mapping = import_requetes_retournees(app, id_mapping)

    # Etape 5: Importer les reponses retournees/archivees
    import_reponses_retournees(app, id_mapping)

    # Etape 6: Importer les autres clients retournes/archives
    import_autres_clients_retournees(app)

    print("\n" + "=" * 60)
    print("IMPORT TERMINE")
    print("=" * 60)

if __name__ == '__main__':
    main()
