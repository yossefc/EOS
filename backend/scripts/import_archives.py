"""
Script d'import des enquetes archivees depuis les dossiers backup.

Dossiers sources :
- reponses_cr backup/       -> PARTNER (client_id=11) - fichiers .xls
- reponses_crcont backup/   -> PARTNER (client_id=11) contestations - fichiers .xls/.xlsx
- reponses_EOS backup/      -> EOS (client_id=1) - fichiers .csv

Usage:
    python import_archives.py                  # Mode dry-run (pas de commit)
    python import_archives.py --commit         # Mode reel (commit en DB)
"""

import sys
import os
import glob
import logging
import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pandas as pd

# Ajouter le dossier parent (backend/) au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Definir DATABASE_URL si non defini (PostgreSQL)
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('import_archives.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Chemins des dossiers backup (relatifs a la racine du projet)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CR_BACKUP_DIR = r'E:\LDMEOS\reponses_cr backup'
CRCONT_BACKUP_DIR = r'E:\LDMEOS\reponses_crcont backup'
EOS_BACKUP_DIR = r'E:\LDMEOS\reponses_EOS backup'

PARTNER_CLIENT_ID = 11
EOS_CLIENT_ID = 1


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def clean_val(value):
    """Nettoie une valeur pandas (NaN, None, 'nan' -> None, sinon strip)"""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    if s.lower() in ('nan', 'none', ''):
        return None
    return s


def clean_str(value, max_len=None):
    """Nettoie et tronque une valeur string"""
    v = clean_val(value)
    if v is None:
        return None
    if max_len:
        return v[:max_len]
    return v


def parse_date(value):
    """Parse une date depuis differents formats"""
    v = clean_val(value)
    if not v:
        return None

    # Si c'est deja un datetime/date pandas
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date() if hasattr(value, 'date') else value

    formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(v, fmt).date()
        except (ValueError, TypeError):
            continue

    # Essayer pandas comme fallback
    try:
        return pd.to_datetime(v, dayfirst=True).date()
    except Exception:
        return None


def parse_decimal(value):
    """Parse un decimal depuis une valeur"""
    v = clean_val(value)
    if not v:
        return None
    try:
        # Gerer les virgules comme separateur decimal
        v = v.replace(',', '.').replace(' ', '')
        return Decimal(v)
    except (InvalidOperation, ValueError):
        return None


def parse_int(value):
    """Parse un entier depuis une valeur"""
    v = clean_val(value)
    if not v:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def combine_date_parts(jour, mois, annee):
    """Combine JOUR/MOIS/ANNEE en une date"""
    j = parse_int(jour)
    m = parse_int(mois)
    a = parse_int(annee)

    if j and m and a and 1 <= j <= 31 and 1 <= m <= 12 and 1900 <= a <= 2100:
        try:
            from datetime import date
            return date(a, m, j)
        except ValueError:
            return None
    return None


def check_duplicate(client_id, numero_dossier, nom, prenom=None, reference_dossier=None):
    """Verifie si une enquete existe deja dans la DB.

    Pour PARTNER: le NUM est un numero sequentiel court (1, 2, 3...) qui se repete
    dans chaque fichier. Il faut donc verifier NUM + nom + prenom ensemble.
    Pour EOS: le referenceDossier est unique et suffit.
    """
    if not numero_dossier and not nom and not reference_dossier:
        return False

    # Pour EOS: verifier par referenceDossier (unique)
    if reference_dossier:
        existing = Donnee.query.filter_by(
            client_id=client_id,
            referenceDossier=reference_dossier
        ).first()
        if existing:
            return True

    # Pour PARTNER: verifier par numeroDossier + nom + prenom
    if numero_dossier and nom:
        query = Donnee.query.filter_by(
            client_id=client_id,
            numeroDossier=numero_dossier,
            nom=nom
        )
        if prenom:
            query = query.filter_by(prenom=prenom)
        existing = query.first()
        if existing:
            return True

    # Si seulement nom (sans numeroDossier), pas de verification de doublon
    # car plusieurs personnes peuvent avoir le meme nom
    return False


# ============================================================================
# Import PARTNER cr - Format A (65 colonnes, reponses completes)
# ============================================================================

def import_partner_cr_format_a(df, fichier_id, stats):
    """Importe les fichiers PARTNER cr avec 65 colonnes (donnees + reponses enqueteur)"""
    cols = list(df.columns)

    for _, row in df.iterrows():
        num_dossier = clean_str(row.get('NUM'), 10)
        nom = clean_str(row.get('NOM'), 30)
        prenom = clean_str(row.get('PRENOM'), 20)

        if not nom:
            stats['skipped'] += 1
            continue

        # Verifier doublon (NUM + nom + prenom car NUM est un seq court)
        if check_duplicate(PARTNER_CLIENT_ID, num_dossier, nom, prenom=prenom):
            stats['duplicates'] += 1
            continue

        # Combiner date de naissance
        date_naissance = combine_date_parts(
            row.get('JOUR'), row.get('MOIS'), row.get('ANNEE NAISSANCE')
        )

        # NOM2/PRENOM2 sont les infos du conjoint - on ne les importe pas directement

        donnee = Donnee(
            client_id=PARTNER_CLIENT_ID,
            fichier_id=fichier_id,
            statut_validation='archive',
            typeDemande='ENQ',
            numeroDossier=num_dossier,
            nom=nom,
            prenom=clean_str(row.get('PRENOM'), 20),
            nomPatronymique=clean_str(row.get('NJF'), 30),
            dateNaissance=date_naissance,
            lieuNaissance=clean_str(row.get('LIEUNAISSANCE'), 50),
            paysNaissance=clean_str(row.get('PAYSNAISSANCE'), 32),
            adresse1=clean_str(row.get('ADRESSE'), 255),
            codePostal=clean_str(row.get('CP'), 10),
            ville=clean_str(row.get('VILLE'), 50),
            paysResidence=clean_str(row.get('PAYS'), 32),
            telephonePersonnel=clean_str(row.get('TEL'), 15),
            titulaireCompte=clean_str(row.get('TITULAIRE'), 32),
            codeBanque=clean_str(row.get('CODEBANQUE'), 5),
            numeroCompte=clean_str(row.get('COMPTE'), 11),
            nomEmployeur=clean_str(row.get('EMPLOYEUR'), 32),
            tarif_lettre=clean_str(row.get('TARIF'), 10),
            recherche=clean_str(row.get('RECHERCHE'), 255),
            instructions=clean_str(row.get('INSTRUCTIONS')),
            date_butoir=parse_date(row.get('DATE BUTOIR')),
            datedenvoie=parse_date(row.get('DATE ENVOI')),
        )
        db.session.add(donnee)
        db.session.flush()

        # Construire notes_personnelles a partir de memo + memo banque + memo employeur
        notes_parts = []
        memo_val = clean_val(row.get('memo'))
        if memo_val:
            notes_parts.append(memo_val)
        memo_banque = clean_val(row.get('memo banque'))
        if memo_banque:
            notes_parts.append(f"[Banque] {memo_banque}")
        memo_employeur = clean_val(row.get('Memo employeur'))
        if memo_employeur:
            notes_parts.append(f"[Employeur] {memo_employeur}")

        # Telephone : combiner tel1 + portable1 pour telephone_personnel
        tel_personnel = clean_str(row.get('Telephone 1'), 15) or clean_str(row.get('Portable 1'), 15)
        tel_employeur_resp = clean_str(row.get('Telephone 2'), 15) or clean_str(row.get('Portable 2'), 15)

        # Resultat
        resultat = clean_str(row.get('Resultat'), 1)
        # Convertir POS/NEG en P/N
        resultat_raw = clean_val(row.get('Resultat'))
        if resultat_raw:
            r_upper = resultat_raw.upper().strip()
            if r_upper == 'POS':
                resultat = 'P'
            elif r_upper == 'NEG':
                resultat = 'N'
            elif r_upper == 'HOR':
                resultat = 'H'
            elif len(r_upper) == 1:
                resultat = r_upper
            else:
                resultat = r_upper[0] if r_upper else None

        donnee_enqueteur = DonneeEnqueteur(
            client_id=PARTNER_CLIENT_ID,
            donnee_id=donnee.id,
            code_resultat=resultat,
            adresse1=clean_str(row.get('Adresse 1'), 32),
            adresse2=clean_str(row.get('Adresse 2'), 32),
            adresse3=clean_str(row.get('Adresse 3'), 32),
            adresse4=clean_str(row.get('Adresse 4'), 32),
            code_postal=clean_str(row.get('Code postal'), 10),
            ville=clean_str(row.get('Ville', None) if 'Ville' not in ['VILLE'] else None, 32),
            pays_residence=clean_str(row.get('Pays'), 32),
            telephone_personnel=tel_personnel,
            telephone_chez_employeur=tel_employeur_resp,
            montant_facture=parse_decimal(row.get('Montant facture')),
            banque_domiciliation=clean_str(row.get('Nom banque'), 32),
            code_banque=clean_str(row.get('Code Banque'), 5),
            code_guichet=clean_str(row.get('Code guichet'), 5),
            nom_employeur=clean_str(row.get('Nom employeur'), 32),
            telephone_employeur=clean_str(row.get('Telepone banque') or row.get('Telephone employeur'), 15),
            notes_personnelles='\n'.join(notes_parts) if notes_parts else None,
        )
        db.session.add(donnee_enqueteur)
        stats['imported'] += 1


# ============================================================================
# Import PARTNER cr - Format B (5 colonnes, memo simple)
# ============================================================================

def import_partner_cr_format_b(df, fichier_id, stats):
    """Importe les fichiers PARTNER cr avec 5 colonnes (memo simple).

    Ces fichiers contiennent souvent les memos associes aux enquetes deja importees
    dans le Format A. On tente de rattacher le memo a une enquete existante.
    """
    for _, row in df.iterrows():
        nom = clean_str(row.get('nom'), 30)
        prenom = clean_str(row.get('prenom'), 20)
        reference = clean_str(row.get('reference'), 10)
        dossier = clean_str(row.get('dossier'), 15)
        memo = clean_val(row.get('memo'))

        if not nom and not reference:
            stats['skipped'] += 1
            continue

        # Essayer de trouver une enquete existante pour rattacher le memo
        # Chercher par reference + nom (car le NUM est un seq court)
        existing = None
        if reference and nom:
            existing = Donnee.query.filter_by(
                client_id=PARTNER_CLIENT_ID,
                numeroDossier=reference,
                nom=nom
            ).first()
        if not existing and reference:
            # Fallback: chercher par reference seul si nom ne matche pas
            existing = Donnee.query.filter_by(
                client_id=PARTNER_CLIENT_ID,
                numeroDossier=reference
            ).first()

        if existing:
            # Rattacher le memo a l'enquete existante
            de = DonneeEnqueteur.query.filter_by(donnee_id=existing.id).first()
            if de:
                if memo:
                    if de.notes_personnelles:
                        de.notes_personnelles = de.notes_personnelles + '\n' + memo
                    else:
                        de.notes_personnelles = memo
                stats['memo_attached'] += 1
            else:
                # Creer un DonneeEnqueteur pour stocker le memo
                de = DonneeEnqueteur(
                    client_id=PARTNER_CLIENT_ID,
                    donnee_id=existing.id,
                    notes_personnelles=memo,
                )
                db.session.add(de)
                stats['memo_attached'] += 1
        else:
            # Pas d'enquete existante, creer une nouvelle entree archive
            if check_duplicate(PARTNER_CLIENT_ID, reference, nom):
                stats['duplicates'] += 1
                continue

            donnee = Donnee(
                client_id=PARTNER_CLIENT_ID,
                fichier_id=fichier_id,
                statut_validation='archive',
                typeDemande='ENQ',
                numeroDossier=reference,
                referenceDossier=dossier,
                nom=nom,
                prenom=prenom,
            )
            db.session.add(donnee)
            db.session.flush()

            if memo:
                de = DonneeEnqueteur(
                    client_id=PARTNER_CLIENT_ID,
                    donnee_id=donnee.id,
                    notes_personnelles=memo,
                )
                db.session.add(de)

            stats['imported'] += 1


# ============================================================================
# Import PARTNER crcont (contestations)
# ============================================================================

def import_partner_crcont(df, fichier_id, stats):
    """Importe les fichiers PARTNER crcont (contestations - 17 colonnes)"""
    for _, row in df.iterrows():
        nom = clean_str(row.get('NOM'), 30)
        dossier = clean_str(row.get('Dossier'), 10)

        if not nom and not dossier:
            stats['skipped'] += 1
            continue

        motif = clean_str(row.get('MOTIF'), 255)
        if check_duplicate(PARTNER_CLIENT_ID, dossier, nom, prenom=motif):
            stats['duplicates'] += 1
            continue

        donnee = Donnee(
            client_id=PARTNER_CLIENT_ID,
            fichier_id=fichier_id,
            statut_validation='archive',
            typeDemande='CON',
            est_contestation=True,
            numeroDossier=dossier,
            nom=nom,
            motif=motif,
            date_jour=parse_date(row.get('DATE DU JOUR')),
            date_butoir=parse_date(row.get('DATE BUTOIR')),
        )
        db.session.add(donnee)
        db.session.flush()

        # Notes personnelles
        memo = clean_val(row.get('memo'))

        # Telephones
        tel_personnel = clean_str(row.get('Telephone 1'), 15) or clean_str(row.get('Portable 1'), 15)
        tel_employeur = clean_str(row.get('Telephone 2'), 15) or clean_str(row.get('Portable 2'), 15)

        donnee_enqueteur = DonneeEnqueteur(
            client_id=PARTNER_CLIENT_ID,
            donnee_id=donnee.id,
            adresse1=clean_str(row.get('Adresse 1'), 32),
            adresse2=clean_str(row.get('Adresse 2'), 32),
            adresse3=clean_str(row.get('Adresse 3'), 32),
            adresse4=clean_str(row.get('Adresse 4'), 32),
            code_postal=clean_str(row.get('Code postal'), 10),
            ville=clean_str(row.get('Ville'), 32),
            telephone_personnel=tel_personnel,
            telephone_chez_employeur=tel_employeur,
            montant_facture=parse_decimal(row.get('Montant facture')),
            notes_personnelles=memo,
        )
        db.session.add(donnee_enqueteur)
        stats['imported'] += 1


def import_partner_crcont_memo(df, fichier_id, stats):
    """Importe les fichiers crcont en format memo (5 colonnes).
    Meme logique que Format B des cr.
    """
    import_partner_cr_format_b(df, fichier_id, stats)


def import_partner_crcont_xlsx(df, fichier_id, stats):
    """Importe le fichier xlsx special dans crcont (5 colonnes urgentes)"""
    for _, row in df.iterrows():
        nom = clean_str(row.get('NOM'), 30)

        if not nom:
            stats['skipped'] += 1
            continue

        if check_duplicate(PARTNER_CLIENT_ID, None, nom):
            stats['duplicates'] += 1
            continue

        donnee = Donnee(
            client_id=PARTNER_CLIENT_ID,
            fichier_id=fichier_id,
            statut_validation='archive',
            typeDemande='CON',
            est_contestation=True,
            nom=nom,
            prenom=clean_str(row.get('PREN'), 20),
            motif=clean_str(row.get('MOTIF'), 255),
            date_jour=parse_date(row.get('DATE DU JOUR')),
            date_butoir=parse_date(row.get('DATE BUTOIR')),
        )
        db.session.add(donnee)
        db.session.flush()

        de = DonneeEnqueteur(
            client_id=PARTNER_CLIENT_ID,
            donnee_id=donnee.id,
        )
        db.session.add(de)
        stats['imported'] += 1


# ============================================================================
# Import EOS CSV
# ============================================================================

def _get_col(row, *col_names):
    """Recupere une valeur depuis la premiere colonne trouvee (gere encodage)"""
    for col in col_names:
        val = row.get(col)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            return val
    return None


def import_eos_csv(df, fichier_id, stats):
    """Importe les fichiers CSV EOS (81 colonnes)"""
    # Normaliser les noms de colonnes (enlever les accents d'encodage)
    col_map = {}
    for c in df.columns:
        # Creer des alias normalises
        norm = str(c).replace('\xc2\xb0', '°').replace('Â°', '°').replace('\xc3\x8a', 'E').replace('Ã\x8a', 'E')
        col_map[norm] = c

    for _, row in df.iterrows():
        num_dossier = clean_str(_get_col(row, 'N DOSSIER', 'N° DOSSIER', 'NÂ° DOSSIER'), 10)
        ref_dossier = clean_str(_get_col(row, 'REFERENCE DOSSIER'), 15)
        nom = clean_str(_get_col(row, 'NOM'), 30)

        if not nom and not num_dossier and not ref_dossier:
            stats['skipped'] += 1
            continue

        if check_duplicate(EOS_CLIENT_ID, num_dossier, nom, reference_dossier=ref_dossier):
            stats['duplicates'] += 1
            continue

        # Determiner le type de demande
        type_demande = clean_str(_get_col(row, "TYPE DE DEMANDE D'ENQUETE", "TYPE DE DEMANDE D'ENQUÊTE"), 3)
        est_contestation = (type_demande == 'CON')

        donnee = Donnee(
            client_id=EOS_CLIENT_ID,
            fichier_id=fichier_id,
            statut_validation='archive',
            typeDemande=type_demande or 'ENQ',
            est_contestation=est_contestation,
            numeroDossier=num_dossier,
            referenceDossier=ref_dossier,
            numeroInterlocuteur=clean_str(row.get('NUMERO INTERLOCUTEUR'), 12),
            guidInterlocuteur=clean_str(row.get('GUID INTERLOCUTEUR'), 36),
            numeroDemande=clean_str(row.get('NUMERO DEMANDE ENQUETE'), 11),
            numeroDemandeContestee=clean_str(row.get('NUMERO DEMANDE ENQUETE CONTESTEE'), 11),
            numeroDemandeInitiale=clean_str(row.get('NUMERO DEMANDE ENQUETE INITIALE'), 11),
            forfaitDemande=clean_str(row.get('FORFAIT DEMANDE'), 16),
            dateRetourEspere=parse_date(row.get('DATE DE RETOUR ESPERE')),
            qualite=clean_str(row.get('QUALITE'), 10),
            nom=nom,
            prenom=clean_str(row.get('PRENOM'), 20),
            dateNaissance=parse_date(row.get('DATE DE NAISSANCE')),
            lieuNaissance=clean_str(row.get('LIEU DE NAISSANCE'), 50),
            codePostalNaissance=clean_str(row.get('CODE POSTAL NAISSANCE'), 10),
            paysNaissance=clean_str(row.get('PAYS DE NAISSANCE'), 32),
            nomPatronymique=clean_str(row.get('NOM DE JEUNE FILLE'), 30),
        )
        db.session.add(donnee)
        db.session.flush()

        # DonneeEnqueteur avec toutes les donnees de reponse
        donnee_enqueteur = DonneeEnqueteur(
            client_id=EOS_CLIENT_ID,
            donnee_id=donnee.id,
            code_resultat=clean_str(row.get("CODE RESULTAT DE L'ENQUETE"), 1),
            elements_retrouves=clean_str(row.get('ELEMENTS RETROUVES'), 10),
            flag_etat_civil_errone=clean_str(row.get('FLAG etat civil errone'), 1),
            date_retour=parse_date(row.get('DATE DE RETOUR')),

            # Facturation
            numero_facture=clean_str(row.get('NUMERO DE FACTURE'), 9),
            date_facture=parse_date(row.get('DATE DE FACTURE')),
            montant_facture=parse_decimal(row.get('MONTANT FACTURE')),
            tarif_applique=parse_decimal(row.get('TARIF APPLIQUE')),
            cumul_montants_precedents=parse_decimal(row.get('CUMUL DES MONTANTS PRECEDEMMENT FACTURES')),
            reprise_facturation=parse_decimal(row.get('REPRISE DE FACTURATION')),
            remise_eventuelle=parse_decimal(row.get('REMISE EVENTUELLE')),

            # Deces
            date_deces=parse_date(row.get('DATE DE DECES')),
            numero_acte_deces=clean_str(row.get('N ACTE DE DECES'), 10),
            code_insee_deces=clean_str(row.get('CODE INSEE DECES'), 5),
            code_postal_deces=clean_str(row.get('CODE POSTAL DECES'), 10),
            localite_deces=clean_str(row.get('LOCALITE DECES'), 32),

            # Adresse trouvee
            adresse1=clean_str(row.get('ADRESSE 1'), 32),
            adresse2=clean_str(row.get('ADRESSE 2'), 32),
            adresse3=clean_str(row.get('ADRESSE 3'), 32),
            adresse4=clean_str(row.get('ADRESSE 4'), 32),
            code_postal=clean_str(row.get('CODE POSTAL'), 10),
            ville=clean_str(row.get('VILLE'), 32),
            pays_residence=clean_str(row.get('PAYS RESIDENCE'), 32),

            # Telephones
            telephone_personnel=clean_str(row.get('TELEPHONE PERSONNEL'), 15),
            telephone_chez_employeur=clean_str(row.get("TELEPHONE CHEZ L'EMPLOYEUR"), 15),

            # Employeur
            nom_employeur=clean_str(row.get("NOM DE L'EMPLOYEUR"), 32),
            telephone_employeur=clean_str(row.get("TELEPHONE DE L'EMPLOYEUR"), 15),
            telecopie_employeur=clean_str(row.get('TELECOPIE EMPLOYEUR'), 15),
            adresse1_employeur=clean_str(row.get("ADRESSE 1 DE L'EMPLOYEUR"), 32),
            adresse2_employeur=clean_str(row.get("ADRESSE 2 DE L'EMPLOYEUR"), 32),
            adresse3_employeur=clean_str(row.get("ADRESSE 3 DE L'EMPLOYEUR"), 32),
            adresse4_employeur=clean_str(row.get("ADRESSE 4 DE L'EMPLOYEUR"), 32),
            code_postal_employeur=clean_str(row.get("CODE POSTAL DE L'EMPLOYEUR"), 10),
            ville_employeur=clean_str(row.get("VILLE DE L'EMPLOYEUR"), 32),
            pays_employeur=clean_str(row.get("PAYS DE L'EMPLOYEUR"), 32),

            # Banque
            banque_domiciliation=clean_str(row.get('BANQUE DE DOMICILIATION'), 32),
            libelle_guichet=clean_str(row.get('LIBELLE GUICHET'), 30),
            titulaire_compte=clean_str(row.get('TITULAIRE DU COMPTE'), 32),
            code_banque=clean_str(row.get('CODE BANQUE'), 5),
            code_guichet=clean_str(row.get('CODE GUICHET'), 5),

            # Revenus
            commentaires_revenus=clean_str(row.get('COMMENTAIRES SUR LES REVENUS'), 128),
            montant_salaire=parse_decimal(row.get('MONTANT SALAIRE')),
            periode_versement_salaire=parse_int(row.get('PERIODE VERSEMENT SALAIRE')),
            frequence_versement_salaire=clean_str(row.get('FREQUENCE DE VERSEMENT DU SALAIRE'), 2),

            # Revenus additionnels 1
            nature_revenu1=clean_str(row.get('NATURE REVENU1'), 30),
            montant_revenu1=parse_decimal(row.get('MONTANT REVENU1')),
            periode_versement_revenu1=parse_int(row.get('PERIODE VERSEMENT REVENU1')),
            frequence_versement_revenu1=clean_str(row.get('FREQUENCE DE VERSEMENT DU REVENU1'), 2),

            # Revenus additionnels 2
            nature_revenu2=clean_str(row.get('NATURE REVENU2'), 30),
            montant_revenu2=parse_decimal(row.get('MONTANT REVENU2')),
            periode_versement_revenu2=parse_int(row.get('PERIODE VERSEMENT REVENU2')),
            frequence_versement_revenu2=clean_str(row.get('FREQUENCE DE VERSEMENT DU REVENU2'), 2),

            # Revenus additionnels 3
            nature_revenu3=clean_str(row.get('NATURE REVENU3'), 30),
            montant_revenu3=parse_decimal(row.get('MONTANT REVENU3')),
            periode_versement_revenu3=parse_int(row.get('PERIODE VERSEMENT REVENU3')),
            frequence_versement_revenu3=clean_str(row.get('FREQUENCE DE VERSEMENT DU REVENU3'), 2),

            # Memos
            memo1=clean_str(row.get('MEMO 1'), 64),
            memo2=clean_str(row.get('MEMO 2'), 64),
            memo3=clean_str(row.get('MEMO 3'), 64),
            memo4=clean_str(row.get('MEMO 4'), 64),
            memo5=clean_str(row.get('MEMO 5'), 1000),
        )
        db.session.add(donnee_enqueteur)

        # Champs supplementaires sur Donnee (RIB, numero compte)
        donnee.numeroCompte = clean_str(row.get('NUMERO DE COMPTE'), 11)
        donnee.ribCompte = clean_str(row.get('RIB DU COMPTE'), 2)

        stats['imported'] += 1


# ============================================================================
# Detection de format et orchestration
# ============================================================================

def detect_format_cr(df):
    """Detecte le format d'un fichier cr PARTNER"""
    cols_lower = [str(c).lower().strip() for c in df.columns]
    nb_cols = len(df.columns)

    if nb_cols >= 30:
        return 'FORMAT_A'  # 65 colonnes, reponses completes
    elif nb_cols <= 6 and 'nom' in cols_lower and 'memo' in cols_lower:
        return 'FORMAT_B'  # 5 colonnes, memo
    else:
        # Tenter de detecter par les noms de colonnes
        if 'NUM' in [str(c).strip() for c in df.columns]:
            return 'FORMAT_A'
        return 'FORMAT_B'


def detect_format_crcont(df):
    """Detecte le format d'un fichier crcont PARTNER"""
    cols = [str(c).strip() for c in df.columns]
    cols_lower = [c.lower() for c in cols]
    nb_cols = len(df.columns)

    if 'DATE DU JOUR' in cols and nb_cols >= 10:
        return 'CONTESTATION'  # 17 colonnes contestation
    elif 'nom' in cols_lower and 'memo' in cols_lower and nb_cols <= 6:
        return 'MEMO'  # 5 colonnes memo
    elif 'DATE DU JOUR' in cols and nb_cols <= 6:
        return 'XLSX_URGENT'  # 5 colonnes urgentes
    else:
        return 'CONTESTATION'  # Par defaut


def process_cr_backup(commit_mode, stats_global):
    """Traite tous les fichiers du dossier reponses_cr backup"""
    logger.info("=" * 60)
    logger.info("TRAITEMENT: reponses_cr backup (PARTNER)")
    logger.info("=" * 60)

    if not os.path.exists(CR_BACKUP_DIR):
        logger.error(f"Dossier introuvable: {CR_BACKUP_DIR}")
        return

    xls_files = sorted(glob.glob(os.path.join(CR_BACKUP_DIR, '*.xls')))
    logger.info(f"Fichiers .xls trouves: {len(xls_files)}")

    # Creer un fichier de reference pour le lot
    fichier = Fichier(
        client_id=PARTNER_CLIENT_ID,
        nom='[ARCHIVE] reponses_cr backup',
        chemin=CR_BACKUP_DIR,
        date_upload=datetime.now()
    )
    db.session.add(fichier)
    db.session.flush()

    stats = {'imported': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0, 'memo_attached': 0}

    for filepath in xls_files:
        filename = os.path.basename(filepath)
        try:
            df = pd.read_excel(filepath)

            if df.empty:
                continue

            fmt = detect_format_cr(df)

            if fmt == 'FORMAT_A':
                import_partner_cr_format_a(df, fichier.id, stats)
            elif fmt == 'FORMAT_B':
                import_partner_cr_format_b(df, fichier.id, stats)

            logger.info(f"  {filename}: {fmt} - {len(df)} lignes")

        except Exception as e:
            logger.error(f"  ERREUR {filename}: {e}")
            stats['errors'] += 1

    logger.info(f"CR PARTNER - Importes: {stats['imported']}, Memos rattaches: {stats['memo_attached']}, "
                f"Doublons: {stats['duplicates']}, Ignores: {stats['skipped']}, Erreurs: {stats['errors']}")
    stats_global['cr'] = stats


def process_crcont_backup(commit_mode, stats_global):
    """Traite tous les fichiers du dossier reponses_crcont backup"""
    logger.info("=" * 60)
    logger.info("TRAITEMENT: reponses_crcont backup (PARTNER contestations)")
    logger.info("=" * 60)

    if not os.path.exists(CRCONT_BACKUP_DIR):
        logger.error(f"Dossier introuvable: {CRCONT_BACKUP_DIR}")
        return

    xls_files = sorted(glob.glob(os.path.join(CRCONT_BACKUP_DIR, '*.xls')))
    xlsx_files = sorted(glob.glob(os.path.join(CRCONT_BACKUP_DIR, '*.xlsx')))
    logger.info(f"Fichiers .xls trouves: {len(xls_files)}, .xlsx: {len(xlsx_files)}")

    # Creer un fichier de reference pour le lot
    fichier = Fichier(
        client_id=PARTNER_CLIENT_ID,
        nom='[ARCHIVE] reponses_crcont backup',
        chemin=CRCONT_BACKUP_DIR,
        date_upload=datetime.now()
    )
    db.session.add(fichier)
    db.session.flush()

    stats = {'imported': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0, 'memo_attached': 0}

    # Traiter les .xls
    for filepath in xls_files:
        filename = os.path.basename(filepath)
        try:
            df = pd.read_excel(filepath)

            if df.empty:
                continue

            fmt = detect_format_crcont(df)

            if fmt == 'CONTESTATION':
                import_partner_crcont(df, fichier.id, stats)
            elif fmt == 'MEMO':
                import_partner_crcont_memo(df, fichier.id, stats)

            logger.info(f"  {filename}: {fmt} - {len(df)} lignes")

        except Exception as e:
            logger.error(f"  ERREUR {filename}: {e}")
            stats['errors'] += 1

    # Traiter les .xlsx
    for filepath in xlsx_files:
        filename = os.path.basename(filepath)
        try:
            df = pd.read_excel(filepath)

            if df.empty:
                continue

            fmt = detect_format_crcont(df)

            if fmt == 'XLSX_URGENT':
                import_partner_crcont_xlsx(df, fichier.id, stats)
            elif fmt == 'CONTESTATION':
                import_partner_crcont(df, fichier.id, stats)
            elif fmt == 'MEMO':
                import_partner_crcont_memo(df, fichier.id, stats)

            logger.info(f"  {filename}: {fmt} - {len(df)} lignes")

        except Exception as e:
            logger.error(f"  ERREUR {filename}: {e}")
            stats['errors'] += 1

    logger.info(f"CRCONT PARTNER - Importes: {stats['imported']}, Memos rattaches: {stats['memo_attached']}, "
                f"Doublons: {stats['duplicates']}, Ignores: {stats['skipped']}, Erreurs: {stats['errors']}")
    stats_global['crcont'] = stats


def process_eos_backup(commit_mode, stats_global):
    """Traite tous les fichiers du dossier reponses_EOS backup"""
    logger.info("=" * 60)
    logger.info("TRAITEMENT: reponses_EOS backup (EOS)")
    logger.info("=" * 60)

    if not os.path.exists(EOS_BACKUP_DIR):
        logger.error(f"Dossier introuvable: {EOS_BACKUP_DIR}")
        return

    csv_files = sorted(glob.glob(os.path.join(EOS_BACKUP_DIR, '*.csv')))
    logger.info(f"Fichiers .csv trouves: {len(csv_files)}")

    # Creer un fichier de reference pour le lot
    fichier = Fichier(
        client_id=EOS_CLIENT_ID,
        nom='[ARCHIVE] reponses_EOS backup',
        chemin=EOS_BACKUP_DIR,
        date_upload=datetime.now()
    )
    db.session.add(fichier)
    db.session.flush()

    stats = {'imported': 0, 'duplicates': 0, 'skipped': 0, 'errors': 0, 'memo_attached': 0}

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        try:
            # Les CSV EOS utilisent ; comme separateur
            # Essayer differents encodages
            df = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, sep=';', encoding=encoding)
                    if len(df.columns) > 1:
                        break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue

            if df is None or df.empty:
                logger.warning(f"  {filename}: impossible de lire ou vide")
                continue

            import_eos_csv(df, fichier.id, stats)
            logger.info(f"  {filename}: {len(df)} lignes")

        except Exception as e:
            logger.error(f"  ERREUR {filename}: {e}")
            stats['errors'] += 1

    logger.info(f"EOS - Importes: {stats['imported']}, "
                f"Doublons: {stats['duplicates']}, Ignores: {stats['skipped']}, Erreurs: {stats['errors']}")
    stats_global['eos'] = stats


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Import des enquetes archivees")
    parser.add_argument('--commit', action='store_true', help='Mode reel (commit en DB)')
    args = parser.parse_args()

    commit_mode = args.commit

    logger.info("=" * 60)
    logger.info(f"IMPORT DES ARCHIVES - Mode: {'COMMIT' if commit_mode else 'DRY-RUN'}")
    logger.info("=" * 60)

    app = create_app()

    with app.app_context():
        stats_global = {}

        try:
            # Traiter les 3 dossiers
            process_cr_backup(commit_mode, stats_global)
            process_crcont_backup(commit_mode, stats_global)
            process_eos_backup(commit_mode, stats_global)

            if commit_mode:
                db.session.commit()
                logger.info("COMMIT effectue avec succes !")
            else:
                db.session.rollback()
                logger.info("DRY-RUN termine (aucune modification en DB)")

        except Exception as e:
            db.session.rollback()
            logger.error(f"ERREUR FATALE: {e}")
            import traceback
            traceback.print_exc()

        # Resume final
        logger.info("")
        logger.info("=" * 60)
        logger.info("RESUME FINAL")
        logger.info("=" * 60)

        total_imported = 0
        total_duplicates = 0
        total_errors = 0

        for source, stats in stats_global.items():
            imported = stats.get('imported', 0)
            duplicates = stats.get('duplicates', 0)
            errors = stats.get('errors', 0)
            memo = stats.get('memo_attached', 0)

            logger.info(f"  {source}: {imported} importes, {duplicates} doublons, {errors} erreurs, {memo} memos rattaches")
            total_imported += imported
            total_duplicates += duplicates
            total_errors += errors

        logger.info(f"  TOTAL: {total_imported} importes, {total_duplicates} doublons, {total_errors} erreurs")
        logger.info(f"  Mode: {'COMMIT (donnees enregistrees)' if commit_mode else 'DRY-RUN (rien enregistre)'}")


if __name__ == '__main__':
    main()
