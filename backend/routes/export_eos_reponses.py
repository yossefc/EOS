# backend/routes/export_eos_reponses.py
"""
Export conforme au format "Réponses EOS" (fixed-width 2618 caractères + CRLF)

Format : fichier texte à longueur fixe, chaque champ padded avec espaces
Longueur ligne : EXACTEMENT 2618 caractères (hors CRLF) + \r\n
Encodage : CP1252 (Windows)
Fin de ligne : CRLF (\r\n)

INTERDICTIONS:
- strip/rstrip sur les lignes (perte espaces = fichier invalide)
- Utiliser des champs du format "Demandes" (elementDemandes, urgence, commentaire 1000, etc.)
"""

import datetime
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


# ============================================================================
# SPECIFICATION DES CHAMPS "REPONSES EOS" (format fixed-width)
# ============================================================================

# Format: (nom_champ, largeur, type_donnee, source_expr, commentaire)
# type_donnee: 'alpha' (padding right), 'numeric' (padding left), 'date' (JJ/MM/AAAA), 'amount' (décimal)
# source_expr: expression Python pour récupérer la valeur

EOS_REPONSES_FIELD_SPECS = [
    # === BLOC A: IDENTIFIANTS (135 chars) ===
    ('numeroDossier', 10, 'alpha', 'd.numeroDossier', 'N° dossier transmis par EOS'),
    ('referenceDossier', 15, 'alpha', 'd.referenceDossier', 'Référence dossier EOS'),
    ('numeroInterlocuteur', 12, 'alpha', 'd.numeroInterlocuteur', 'N° interlocuteur EOS'),
    ('guidInterlocuteur', 36, 'alpha', 'd.guidInterlocuteur', 'GUID interlocuteur EOS'),
    ('typeDemande', 3, 'alpha', 'd.typeDemande', 'ENQ ou CON'),
    ('numeroDemande', 11, 'alpha', 'd.numeroDemande', 'N° demande EOS'),
    ('numeroDemandeContestee', 11, 'alpha', 'd.numeroDemandeContestee if d.typeDemande == "CON" else ""', 'N° demande contestée (CON uniquement)'),
    ('numeroDemandeInitiale', 11, 'alpha', 'd.numeroDemandeInitiale if d.typeDemande == "CON" else ""', 'N° demande initiale (CON uniquement)'),
    ('forfaitDemande', 16, 'alpha', 'd.forfaitDemande', 'Forfait demande EOS'),
    ('dateRetourEspere', 10, 'date', 'd.dateRetourEspere', 'Date retour espéré'),

    # === BLOC B: ETAT CIVIL avec priorité corrections (192 chars) ===
    ('qualite', 10, 'alpha', 'e.qualite_corrigee or d.qualite', 'Civilité (priorité correction)'),
    ('nom', 30, 'alpha', 'e.nom_corrige or d.nom', 'Nom (priorité correction)'),
    ('prenom', 20, 'alpha', 'e.prenom_corrige or d.prenom', 'Prénom (priorité correction)'),
    ('dateNaissance', 10, 'date', 'd.dateNaissance', 'Date naissance'),
    ('lieuNaissance', 50, 'alpha', 'd.lieuNaissance', 'Lieu naissance'),
    ('codePostalNaissance', 10, 'alpha', 'e.code_postal_naissance_corrige or d.codePostalNaissance', 'CP naissance (priorité correction)'),
    ('paysNaissance', 32, 'alpha', 'e.pays_naissance_corrige or d.paysNaissance', 'Pays naissance (priorité correction)'),
    ('nomPatronymique', 30, 'alpha', 'e.nom_patronymique_corrige or d.nomPatronymique', 'Nom patronymique (priorité correction)'),

    # === BLOC C: RESULTAT (22 chars) ===
    ('dateRetour', 10, 'date', 'e.date_retour or datetime.date.today()', 'Date retour (aujourd\'hui par défaut)'),
    ('codeResultat', 1, 'alpha', 'e.code_resultat', 'Code résultat (P/N/H/Z/I/Y)'),
    ('elementsRetrouves', 10, 'alpha', 'e.elements_retrouves', 'Eléments retrouvés'),
    ('flagEtatCivilErrone', 1, 'alpha', 'e.flag_etat_civil_errone', 'Flag état civil erroné (E ou vide)'),

    # === BLOC D: FACTURATION (59 chars) ===
    ('numeroFacture', 9, 'alpha', '""', 'N° facture (toujours vide)'),
    ('dateFacture', 10, 'date', 'export_date', 'Date facture (date d\'export)'),
    ('montantFacture', 8, 'money', 'tarif_montant', 'Montant facturé (depuis tarifs_eos)'),
    ('tarifApplique', 8, 'money', 'tarif_montant', 'Tarif appliqué (même que montantFacture)'),
    ('cumulMontantsPrecedents', 8, 'money', '0.0', 'Cumul montants précédents (toujours 0.00)'),
    ('repriseFacturation', 8, 'int8', '0', 'Reprise facturation (toujours 0)'),
    ('remiseEventuelle', 8, 'int8', '0', 'Remise éventuelle (toujours 0)'),

    # === BLOC E: DECES (67 chars) ===
    ('dateDeces', 10, 'date', 'e.date_deces', 'Date décès'),
    ('numeroActeDeces', 10, 'alpha', 'e.numero_acte_deces', 'N° acte décès'),
    ('codeInseeDeces', 5, 'alpha', 'e.code_insee_deces', 'Code INSEE décès'),
    ('codePostalDeces', 10, 'alpha', 'e.code_postal_deces', 'CP décès'),
    ('localiteDeces', 32, 'alpha', 'e.localite_deces', 'Localité décès'),

    # === BLOC F: ADRESSE RESIDENCE (202 chars) ===
    ('adresse1', 32, 'alpha', 'e.adresse1', 'Adresse ligne 1'),
    ('adresse2', 32, 'alpha', 'e.adresse2', 'Adresse ligne 2'),
    ('adresse3', 32, 'alpha', 'e.adresse3', 'Adresse ligne 3'),
    ('adresse4', 32, 'alpha', 'e.adresse4', 'Adresse ligne 4'),
    ('codePostal', 10, 'alpha', 'e.code_postal', 'CP résidence'),
    ('ville', 32, 'alpha', 'e.ville', 'Ville résidence'),
    ('paysResidence', 32, 'alpha', 'e.pays_residence', 'Pays résidence'),

    # === BLOC G: TELEPHONES (30 chars) ===
    ('telephonePersonnel', 15, 'alpha', 'e.telephone_personnel', 'Téléphone personnel'),
    ('telephoneChezEmployeur', 15, 'alpha', 'e.telephone_chez_employeur', 'Téléphone chez employeur'),

    # === BLOC H: EMPLOYEUR (294 chars) ===
    ('nomEmployeur', 32, 'alpha', 'e.nom_employeur', 'Nom employeur'),
    ('telephoneEmployeur', 15, 'alpha', 'e.telephone_employeur', 'Téléphone employeur'),
    ('telecopieEmployeur', 15, 'alpha', 'e.telecopie_employeur', 'Télécopie employeur'),
    ('adresse1Employeur', 32, 'alpha', 'e.adresse1_employeur', 'Adresse employeur ligne 1'),
    ('adresse2Employeur', 32, 'alpha', 'e.adresse2_employeur', 'Adresse employeur ligne 2'),
    ('adresse3Employeur', 32, 'alpha', 'e.adresse3_employeur', 'Adresse employeur ligne 3'),
    ('adresse4Employeur', 32, 'alpha', 'e.adresse4_employeur', 'Adresse employeur ligne 4'),
    ('codePostalEmployeur', 10, 'alpha', 'e.code_postal_employeur', 'CP employeur'),
    ('villeEmployeur', 32, 'alpha', 'e.ville_employeur', 'Ville employeur'),
    ('paysEmployeur', 32, 'alpha', 'e.pays_employeur', 'Pays employeur'),

    # === BLOC I: BANQUE (117 chars) - NUMERO_COMPTE et RIB TOUJOURS VIDES ===
    ('banqueDomiciliation', 32, 'alpha', 'e.banque_domiciliation', 'Banque domiciliation'),
    ('libelleGuichet', 30, 'alpha', 'e.libelle_guichet', 'Libellé guichet'),
    ('titulaireCompte', 32, 'alpha', 'e.titulaire_compte', 'Titulaire compte'),
    ('codeBanque', 5, 'alpha', 'e.code_banque', 'Code banque'),
    ('codeGuichet', 5, 'alpha', 'e.code_guichet', 'Code guichet'),
    ('numeroCompte', 11, 'alpha', '""', 'N° compte TOUJOURS VIDE'),
    ('ribCompte', 2, 'alpha', '""', 'RIB TOUJOURS VIDE'),

    # === BLOC J: REVENUS (376 chars) ===
    ('commentairesRevenus', 128, 'alpha', 'e.commentaires_revenus', 'Commentaires revenus'),
    ('montantSalaire', 8, 'amount', 'e.montant_salaire', 'Montant salaire'),
    ('periodeVersementSalaire', 3, 'numeric', 'e.periode_versement_salaire', 'Période versement salaire'),
    ('frequenceVersementSalaire', 2, 'alpha', 'e.frequence_versement_salaire', 'Fréquence versement salaire (Q/H/BM/M/T/S/A)'),

    # Revenu 1
    ('natureRevenu1', 30, 'alpha', 'e.nature_revenu1', 'Nature revenu 1'),
    ('montantRevenu1', 8, 'amount', 'e.montant_revenu1', 'Montant revenu 1'),
    ('periodeVersementRevenu1', 3, 'numeric', 'e.periode_versement_revenu1', 'Période versement revenu 1'),
    ('frequenceVersementRevenu1', 2, 'alpha', 'e.frequence_versement_revenu1', 'Fréquence versement revenu 1'),

    # Revenu 2
    ('natureRevenu2', 30, 'alpha', 'e.nature_revenu2', 'Nature revenu 2'),
    ('montantRevenu2', 8, 'amount', 'e.montant_revenu2', 'Montant revenu 2'),
    ('periodeVersementRevenu2', 3, 'numeric', 'e.periode_versement_revenu2', 'Période versement revenu 2'),
    ('frequenceVersementRevenu2', 2, 'alpha', 'e.frequence_versement_revenu2', 'Fréquence versement revenu 2'),

    # Revenu 3
    ('natureRevenu3', 30, 'alpha', 'e.nature_revenu3', 'Nature revenu 3'),
    ('montantRevenu3', 8, 'amount', 'e.montant_revenu3', 'Montant revenu 3'),
    ('periodeVersementRevenu3', 3, 'numeric', 'e.periode_versement_revenu3', 'Période versement revenu 3'),
    ('frequenceVersementRevenu3', 2, 'alpha', 'e.frequence_versement_revenu3', 'Fréquence versement revenu 3'),

    # === BLOC K: MEMOS (1128 chars) ===
    ('memo1', 64, 'alpha', 'e.memo1', 'Mémo 1'),
    ('memo2', 64, 'alpha', 'e.memo2', 'Mémo 2'),
    ('memo3', 64, 'alpha', 'e.memo3', 'Mémo 3'),
    ('memo4', 64, 'alpha', 'e.memo4', 'Mémo 4'),
    ('memo5', 1000, 'alpha', 'e.memo5', 'Mémo 5 (long)'),
]

# Vérification longueur totale attendue
EXPECTED_LINE_LENGTH = 2618
_calculated_length = sum(spec[1] for spec in EOS_REPONSES_FIELD_SPECS)
assert _calculated_length == EXPECTED_LINE_LENGTH, f"ERREUR SPEC: longueur calculée {_calculated_length} != attendue {EXPECTED_LINE_LENGTH}"


# ============================================================================
# HELPERS DE FORMATAGE
# ============================================================================

def format_alphanum(value, width):
    """
    Formate un champ alphanumérique : trim + padding à droite avec espaces

    Args:
        value: Valeur à formater (str, int, float, None)
        width: Largeur fixe du champ

    Returns:
        str: Chaîne de exactement `width` caractères
    """
    if value is None:
        value = ''

    # Convertir en string et nettoyer
    value_str = str(value).strip()

    # Nettoyer caractères spéciaux pour CP1252
    value_str = clean_special_chars(value_str)

    # Tronquer si trop long
    if len(value_str) > width:
        value_str = value_str[:width]

    # Padding à droite avec espaces
    return value_str.ljust(width)


def format_numeric(value, width):
    """
    Formate un champ numérique : digits only + padding à gauche avec zéros

    Args:
        value: Valeur numérique (int, float, None)
        width: Largeur fixe du champ

    Returns:
        str: Chaîne de exactement `width` caractères
    """
    if value is None or value == '':
        # Espaces si vide (pas de zéros)
        return ' ' * width

    try:
        # Convertir en entier
        value_int = int(value)
        value_str = str(value_int)

        # Tronquer si trop long
        if len(value_str) > width:
            value_str = value_str[:width]

        # Padding à gauche avec zéros
        return value_str.rjust(width, '0')
    except (ValueError, TypeError):
        # Si conversion impossible, retourner espaces
        return ' ' * width


def format_date(date_value):
    """
    Formate une date au format JJ/MM/AAAA (10 caractères)

    Args:
        date_value: Date (datetime.date, datetime.datetime, str, None)

    Returns:
        str: Date formatée 'JJ/MM/AAAA' ou 10 espaces si None
    """
    if date_value is None:
        return ' ' * 10

    # Si string, essayer de parser
    if isinstance(date_value, str):
        try:
            date_value = datetime.datetime.strptime(date_value, '%Y-%m-%d').date()
        except:
            return ' ' * 10

    # Si datetime, extraire date
    if isinstance(date_value, datetime.datetime):
        date_value = date_value.date()

    # Formater
    if isinstance(date_value, datetime.date):
        return date_value.strftime('%d/%m/%Y')

    return ' ' * 10


def format_amount(montant, width=8):
    """
    OBSOLETE: Ancienne version avec virgule et zero-padding
    Utiliser format_money_8() ou format_int_8() à la place
    """
    if montant is None:
        montant = 0.0

    try:
        # Convertir en Decimal pour précision
        if isinstance(montant, (int, float, str)):
            montant = Decimal(str(montant))

        # Formater avec 2 décimales
        montant_str = f"{montant:.2f}".replace('.', ',')

        # Padding à gauche avec zéros
        return montant_str.rjust(width, '0')
    except:
        # En cas d'erreur, retourner 0
        return '0,00'.rjust(width, '0')


def format_money_8(montant):
    """
    Formate un montant décimal sur 8 caractères avec POINT et padding ESPACES
    Conforme à la spec EOS (ex: " 24.00", " -22.00", "   0.00")

    Args:
        montant: Montant (Decimal, float, int, None)

    Returns:
        str: Montant formaté avec point, exactement 8 caractères, padding espaces à gauche
    """
    if montant is None:
        montant = 0.0

    try:
        # Convertir en Decimal pour précision
        if isinstance(montant, (int, float, str)):
            montant = Decimal(str(montant))

        # Formater avec 2 décimales et POINT (pas virgule)
        montant_str = f"{montant:.2f}"

        # Padding à gauche avec ESPACES (pas zéros)
        return montant_str.rjust(8)
    except:
        # En cas d'erreur, retourner 0.00
        return "    0.00"


def format_int_8(n):
    """
    Formate un entier sur 8 caractères avec padding ESPACES à gauche
    Conforme à la spec EOS (ex: "       0", "     123")

    Args:
        n: Entier (int, None)

    Returns:
        str: Entier formaté, exactement 8 caractères, padding espaces à gauche
    """
    if n is None:
        n = 0

    try:
        # Convertir en entier
        n_int = int(n)
        n_str = str(n_int)

        # Padding à gauche avec ESPACES (pas zéros)
        return n_str.rjust(8)
    except:
        # En cas d'erreur, retourner 0
        return "       0"


def clean_special_chars(text):
    """Nettoie les caractères spéciaux pour l'encodage CP1252"""
    if text is None:
        return ''

    # Remplacements pour les caractères problématiques
    replacements = {
        'œ': 'oe', 'Œ': 'OE',
        'æ': 'ae', 'Æ': 'AE',
        '€': 'EUR',
        '—': '-', '–': '-',
        ''': "'", ''': "'",
        '"': '"', '"': '"',
        '…': '...',
    }

    text = str(text)
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Encoder en cp1252 avec remplacement des caractères non supportés
    try:
        text.encode('cp1252')
        return text
    except UnicodeEncodeError:
        return text.encode('cp1252', errors='replace').decode('cp1252')


# ============================================================================
# GENERATION LIGNE EXPORT (SPEC-DRIVEN)
# ============================================================================

def get_tarif_eos(code_tarif, export_date):
    """
    Récupère le montant du tarif EOS actif pour un code et une date donnés

    Args:
        code_tarif: Code tarif (ex: 'A', 'AT', 'D')
        export_date: Date de l'export (datetime.date)

    Returns:
        Decimal or None: Montant du tarif si trouvé, None sinon
    """
    if not code_tarif or not export_date:
        return None

    # Importer le modèle ici pour éviter les imports circulaires
    from models.tarifs import TarifEOS
    from extensions import db

    # Nettoyer le code tarif
    code_tarif = str(code_tarif).strip()

    try:
        # Rechercher le tarif actif pour cette date
        tarif = db.session.query(TarifEOS).filter(
            TarifEOS.code == code_tarif,
            TarifEOS.actif == True,
            TarifEOS.date_debut <= export_date,
            db.or_(
                TarifEOS.date_fin.is_(None),
                TarifEOS.date_fin >= export_date
            )
        ).order_by(TarifEOS.date_debut.desc()).first()

        if tarif:
            return tarif.montant
        else:
            logger.warning(f"Tarif EOS introuvable pour code='{code_tarif}' à la date {export_date}")
            return None

    except Exception as e:
        logger.error(f"Erreur lors de la recherche du tarif EOS (code='{code_tarif}'): {e}")
        return None


def generate_eos_reponses_line(d, e, f=None, export_date=None):
    """
    Génère une ligne d'export au format "Réponses EOS" (spec-driven)

    Args:
        d: Objet Donnee (table donnees)
        e: Objet DonneeEnqueteur (table donnees_enqueteur)
        f: Objet EnqueteFacturation (table enquete_facturation, optionnel)
        export_date: Date de l'export (datetime.date, défaut: aujourd'hui)

    Returns:
        str: Ligne formatée de 2618 caractères + CRLF, ou None si erreur
    """
    # Date d'export par défaut = aujourd'hui
    if export_date is None:
        export_date = datetime.date.today()

    # ===== CALCUL DU TARIF EOS =====
    # Déterminer le code tarif : priorité 1 = elementDemandes, sinon elements_retrouves
    code_tarif = None
    if d.elementDemandes:
        code_tarif = str(d.elementDemandes).strip()
    elif e.elements_retrouves:
        code_tarif = str(e.elements_retrouves).strip()

    # Récupérer le montant depuis tarifs_eos
    tarif_montant = get_tarif_eos(code_tarif, export_date)
    if tarif_montant is None:
        tarif_montant = Decimal('0.00')
        if code_tarif:
            logger.warning(f"Enquête ID={d.id}: code tarif '{code_tarif}' introuvable, montant=0.00")

    # Validation champs obligatoires
    champs_obligatoires = {
        'numeroDossier': d.numeroDossier,
        'referenceDossier': d.referenceDossier,
        'numeroInterlocuteur': d.numeroInterlocuteur,
        'guidInterlocuteur': d.guidInterlocuteur,
        'typeDemande': d.typeDemande,
        'numeroDemande': d.numeroDemande,
        'forfaitDemande': d.forfaitDemande,
    }

    champs_manquants = [nom for nom, val in champs_obligatoires.items() if not val]
    if champs_manquants:
        logger.warning(f"Enquête ID={d.id} ignorée - champs obligatoires manquants: {', '.join(champs_manquants)}")
        return None

    # Construire la ligne champ par champ selon EOS_REPONSES_FIELD_SPECS
    fields = []

    for field_name, width, field_type, source_expr, comment in EOS_REPONSES_FIELD_SPECS:
        try:
            # Evaluer l'expression source pour obtenir la valeur
            # Note: eval avec contexte contrôlé (d, e, f, export_date, tarif_montant)
            value = eval(source_expr, {
                'd': d, 
                'e': e, 
                'f': f, 
                'datetime': datetime,
                'export_date': export_date,
                'tarif_montant': tarif_montant
            })

            # Formatter selon le type
            if field_type == 'alpha':
                formatted = format_alphanum(value, width)
            elif field_type == 'numeric':
                formatted = format_numeric(value, width)
            elif field_type == 'date':
                formatted = format_date(value)
            elif field_type == 'money':
                formatted = format_money_8(value)
            elif field_type == 'int8':
                formatted = format_int_8(value)
            elif field_type == 'amount':
                # OBSOLETE: utiliser 'money' ou 'int8' à la place
                formatted = format_money_8(value)
            else:
                # Type inconnu, fallback alphanum
                formatted = format_alphanum(value, width)

            fields.append(formatted)

        except Exception as ex:
            # En cas d'erreur, logger et utiliser espaces
            logger.warning(f"Erreur champ '{field_name}' pour enquête ID={d.id}: {ex}")
            fields.append(' ' * width)

    # Joindre tous les champs
    line = ''.join(fields)

    # Vérification longueur (CRITIQUE)
    if len(line) != EXPECTED_LINE_LENGTH:
        logger.error(f"ERREUR LONGUEUR: enquête ID={d.id}, attendu {EXPECTED_LINE_LENGTH}, obtenu {len(line)}")
        return None

    # Ajouter CRLF (Windows)
    return line + '\r\n'


# ============================================================================
# DEBUG HELPER
# ============================================================================

def debug_parse_line(line):
    """
    Parse et affiche une ligne d'export pour vérification manuelle

    Args:
        line: Ligne d'export (avec ou sans CRLF)

    Returns:
        dict: Dictionnaire {nom_champ: valeur_extraite}
    """
    # Retirer CRLF si présent
    line_data = line.rstrip('\r\n')

    if len(line_data) != EXPECTED_LINE_LENGTH:
        print(f"⚠️  ATTENTION: longueur {len(line_data)} != attendue {EXPECTED_LINE_LENGTH}")

    print(f"\n{'='*80}")
    print(f"DEBUG PARSE LIGNE (longueur: {len(line_data)})")
    print(f"{'='*80}\n")

    parsed = {}
    pos = 0

    for field_name, width, field_type, source_expr, comment in EOS_REPONSES_FIELD_SPECS:
        # Extraire la valeur
        value = line_data[pos:pos+width]
        parsed[field_name] = value

        # Afficher
        print(f"{field_name:30} [{pos:4}-{pos+width:4}] ({width:3}) : '{value}' | {comment}")

        pos += width

    print(f"\n{'='*80}\n")

    return parsed


# ============================================================================
# VALIDATION FACTURATION
# ============================================================================

def validate_facturation(d, e, f):
    """
    Valide la cohérence de la facturation selon le code résultat

    Args:
        d: Donnee
        e: DonneeEnqueteur
        f: EnqueteFacturation (optionnel)

    Returns:
        bool: True si valide, False sinon (avec log d'erreur)
    """
    code_resultat = e.code_resultat

    # Codes résultats facturables (selon vos règles métier)
    codes_facturables = ['P', 'H']  # Ajuster selon vos règles

    if code_resultat in codes_facturables:
        # Vérifier qu'un montant est présent
        montant = e.montant_facture or (f.resultat_eos_montant if f else None)

        if montant is None or montant == 0:
            logger.error(f"Enquête ID={d.id}: code résultat '{code_resultat}' facturable mais montant=0")
            return False

    return True
