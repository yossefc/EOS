#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export EOS "Réponses" - Format Fixed-Width STRICT
Conforme au cahier des charges (pages 15-21) + exemple Reponses_EOS_2025-12-24_23_54_56 (1).txt

Approche SPEC-DRIVEN avec validation stricte des largeurs et formatage.
"""

import datetime
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


# ============================================================================
# FIELD_SPECS - Définition déclarative de tous les champs
# ============================================================================
# Format: (nom_champ, largeur, type, source_expr, commentaire)
#
# Types de champs:
#   - 'alpha'   : Alphanumérique, padding droite avec espaces
#   - 'numeric' : Numérique, padding gauche avec zéros (ou espaces si None)
#   - 'date'    : Date JJ/MM/AAAA (10 chars)
#   - 'amount8' : Montant 8 chars (99999,99) pour facturation
#   - 'amount10': Montant 10 chars (9999999,99) pour salaire/revenus
#   - 'period2' : Période 2 chars (accepte -1, padding gauche zéros ou espaces si None)
#
# Source: d=donnees, e=donnees_enqueteur, f=enquete_facturation

EOS_REPONSES_FIELD_SPECS = [
    # ===== A. IDENTIFIANTS (135 chars) - Source: donnees (d) =====
    ('numeroDossier', 10, 'alpha', 'd.numeroDossier', 'N° dossier EOS (EXACT tel que reçu)'),
    ('referenceDossier', 15, 'alpha', 'd.referenceDossier', 'Référence dossier EOS'),
    ('numeroInterlocuteur', 12, 'alpha', 'd.numeroInterlocuteur', 'N° interlocuteur EOS'),
    ('guidInterlocuteur', 36, 'alpha', 'd.guidInterlocuteur', 'GUID interlocuteur EOS'),
    ('typeDemande', 3, 'alpha', 'd.typeDemande', 'ENQ ou CON'),
    ('numeroDemande', 11, 'alpha', 'd.numeroDemande', 'N° demande EOS'),
    ('numeroDemandeContestee', 11, 'alpha', 'd.numeroDemandeContestee if CON else ""', 'Si contestation'),
    ('numeroDemandeInitiale', 11, 'alpha', 'd.numeroDemandeInitiale if CON else ""', 'Si contestation'),
    ('forfaitDemande', 16, 'alpha', 'd.forfaitDemande', 'Forfait demande EOS'),
    ('dateRetourEspere', 10, 'date', 'd.dateRetourEspere', 'Date retour espéré EOS'),

    # ===== B. ÉTAT CIVIL (192 chars) - Priorité e.*_corrige, sinon d.* =====
    ('qualite', 10, 'alpha', 'e.qualite_corrigee or d.qualite', 'Civilité (priorité correction)'),
    ('nom', 30, 'alpha', 'e.nom_corrige or d.nom', 'Nom (priorité correction)'),
    ('prenom', 20, 'alpha', 'e.prenom_corrige or d.prenom', 'Prénom (priorité correction)'),
    ('dateNaissance', 10, 'date', 'd.dateNaissance', 'Date naissance'),
    ('lieuNaissance', 50, 'alpha', 'd.lieuNaissance', 'Lieu naissance'),
    ('codePostalNaissance', 10, 'alpha', 'e.code_postal_naissance_corrige or d.codePostalNaissance', 'CP naissance (priorité correction)'),
    ('paysNaissance', 32, 'alpha', 'e.pays_naissance_corrige or d.paysNaissance', 'Pays naissance (priorité correction)'),
    ('nomPatronymique', 30, 'alpha', 'e.nom_patronymique_corrige or d.nomPatronymique', 'Nom patronymique (priorité correction)'),

    # ===== C. RÉSULTAT (22 chars) - Source: donnees_enqueteur (e) =====
    ('dateRetour', 10, 'date', 'e.date_retour or today()', 'Date retour réelle'),
    ('codeResultat', 1, 'alpha', 'e.code_resultat', 'P/N/H/Z/I/Y (OBLIGATOIRE)'),
    ('elementsRetrouves', 10, 'alpha', 'e.elements_retrouves', 'A/T/B/E/R/D (OBLIGATOIRE)'),
    ('flagEtatCivilErrone', 1, 'alpha', 'e.flag_etat_civil_errone', 'E ou vide'),

    # ===== D. FACTURATION (59 chars) - Priorité e, sinon f =====
    ('numeroFacture', 9, 'alpha', 'e.numero_facture', 'N° facture'),
    ('dateFacture', 10, 'date', 'e.date_facture', 'Date facture'),
    ('montantFacture', 8, 'amount8', 'e.montant_facture or f.resultat_eos_montant', 'Montant facturé (priorité e, sinon f)'),
    ('tarifApplique', 8, 'amount8', 'e.tarif_applique or f.tarif_eos_montant', 'Tarif appliqué (priorité e, sinon f)'),
    ('cumulMontantsPrecedents', 8, 'amount8', 'e.cumul_montants_precedents or d.cumulMontantsPrecedents', 'Cumul montants précédents'),
    ('repriseFacturation', 8, 'amount8', 'e.reprise_facturation', 'Reprise facturation'),
    ('remiseEventuelle', 8, 'amount8', 'e.remise_eventuelle', 'Remise éventuelle'),

    # ===== E. DÉCÈS (67 chars) - Source: donnees_enqueteur (e) =====
    ('dateDeces', 10, 'date', 'e.date_deces', 'Date décès'),
    ('numeroActeDeces', 10, 'alpha', 'e.numero_acte_deces', 'N° acte décès'),
    ('codeInseeDeces', 5, 'alpha', 'e.code_insee_deces', 'Code INSEE décès'),
    ('codePostalDeces', 10, 'alpha', 'e.code_postal_deces', 'CP décès'),
    ('localiteDeces', 32, 'alpha', 'e.localite_deces', 'Localité décès'),

    # ===== F. ADRESSE RÉSIDENCE (202 chars) - Source: donnees_enqueteur (e) =====
    ('adresse1', 32, 'alpha', 'e.adresse1', 'Adresse ligne 1'),
    ('adresse2', 32, 'alpha', 'e.adresse2', 'Adresse ligne 2'),
    ('adresse3', 32, 'alpha', 'e.adresse3', 'Adresse ligne 3'),
    ('adresse4', 32, 'alpha', 'e.adresse4', 'Adresse ligne 4'),
    ('codePostal', 10, 'alpha', 'e.code_postal', 'Code postal'),
    ('ville', 32, 'alpha', 'e.ville', 'Ville'),
    ('paysResidence', 32, 'alpha', 'e.pays_residence', 'Pays résidence'),

    # ===== G. TÉLÉPHONES (30 chars) - Source: donnees_enqueteur (e) =====
    ('telephonePersonnel', 15, 'alpha', 'e.telephone_personnel', 'Téléphone personnel'),
    ('telephoneChezEmployeur', 15, 'alpha', 'e.telephone_chez_employeur', 'Téléphone chez employeur'),

    # ===== H. EMPLOYEUR (294 chars) - Source: donnees_enqueteur (e) =====
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

    # ===== I. BANQUE (117 chars) - Source: donnees_enqueteur (e) =====
    # ATTENTION: numeroCompte et RIB doivent être TOUJOURS VIDES (espaces)
    ('banqueDomiciliation', 32, 'alpha', 'e.banque_domiciliation', 'Domiciliation bancaire'),
    ('libelleGuichet', 30, 'alpha', 'e.libelle_guichet', 'Libellé guichet'),
    ('titulaireCompte', 32, 'alpha', 'e.titulaire_compte', 'Titulaire compte'),
    ('codeBanque', 5, 'alpha', 'e.code_banque', 'Code banque'),
    ('codeGuichet', 5, 'alpha', 'e.code_guichet', 'Code guichet'),
    ('numeroCompte', 11, 'alpha', '""', 'N° compte - TOUJOURS VIDE'),
    ('ribCompte', 2, 'alpha', '""', 'RIB - TOUJOURS VIDE'),

    # ===== J. REVENUS (274 chars) - Source: donnees_enqueteur (e) =====
    # Largeurs CORRIGÉES: montant=10, période=2 (pas 8 et 3)
    ('commentairesRevenus', 128, 'alpha', 'e.commentaires_revenus', 'Commentaires revenus'),

    # Salaire (14 chars: 10+2+2)
    ('montantSalaire', 10, 'amount10', 'e.montant_salaire', 'Montant salaire'),
    ('periodeVersementSalaire', 2, 'period2', 'e.periode_versement_salaire', 'Période versement salaire'),
    ('frequenceVersementSalaire', 2, 'alpha', 'e.frequence_versement_salaire', 'Fréquence versement salaire'),

    # Revenu 1 (44 chars: 30+10+2+2)
    ('natureRevenu1', 30, 'alpha', 'e.nature_revenu1', 'Nature revenu 1'),
    ('montantRevenu1', 10, 'amount10', 'e.montant_revenu1', 'Montant revenu 1'),
    ('periodeVersementRevenu1', 2, 'period2', 'e.periode_versement_revenu1', 'Période versement revenu 1'),
    ('frequenceVersementRevenu1', 2, 'alpha', 'e.frequence_versement_revenu1', 'Fréquence versement revenu 1'),

    # Revenu 2 (44 chars: 30+10+2+2)
    ('natureRevenu2', 30, 'alpha', 'e.nature_revenu2', 'Nature revenu 2'),
    ('montantRevenu2', 10, 'amount10', 'e.montant_revenu2', 'Montant revenu 2'),
    ('periodeVersementRevenu2', 2, 'period2', 'e.periode_versement_revenu2', 'Période versement revenu 2'),
    ('frequenceVersementRevenu2', 2, 'alpha', 'e.frequence_versement_revenu2', 'Fréquence versement revenu 2'),

    # Revenu 3 (44 chars: 30+10+2+2)
    ('natureRevenu3', 30, 'alpha', 'e.nature_revenu3', 'Nature revenu 3'),
    ('montantRevenu3', 10, 'amount10', 'e.montant_revenu3', 'Montant revenu 3'),
    ('periodeVersementRevenu3', 2, 'period2', 'e.periode_versement_revenu3', 'Période versement revenu 3'),
    ('frequenceVersementRevenu3', 2, 'alpha', 'e.frequence_versement_revenu3', 'Fréquence versement revenu 3'),

    # ===== K. MÉMOS (1128 chars) - Source: donnees_enqueteur (e) =====
    ('memo1', 64, 'alpha', 'e.memo1', 'Mémo 1'),
    ('memo2', 64, 'alpha', 'e.memo2', 'Mémo 2'),
    ('memo3', 64, 'alpha', 'e.memo3', 'Mémo 3'),
    ('memo4', 64, 'alpha', 'e.memo4', 'Mémo 4'),
    ('memo5', 1000, 'alpha', 'e.memo5', 'Mémo 5 (long)'),
]


# ============================================================================
# CALCUL LONGUEUR ATTENDUE (validation stricte)
# ============================================================================
EXPECTED_LINE_LENGTH = sum(spec[1] for spec in EOS_REPONSES_FIELD_SPECS)

logger.info(f"Export EOS 'Réponses' - Longueur attendue: {EXPECTED_LINE_LENGTH} chars (calculée depuis FIELD_SPECS)")


# ============================================================================
# HELPERS DE FORMATAGE - STRICT selon cahier des charges
# ============================================================================

def format_alpha(value, width):
    """
    Formatte un champ alphanumérique.
    - Padding à DROITE avec espaces
    - Troncature si trop long
    - None → espaces

    Exemple: format_alpha("TEST", 10) → "TEST      "
    """
    if value is None:
        value = ''
    s = str(value).strip()
    if len(s) > width:
        s = s[:width]
    return s.ljust(width)


def format_numeric(value, width):
    """
    Formatte un champ numérique (entier).
    - Padding à GAUCHE avec zéros si value est présent
    - Padding à GAUCHE avec espaces si value est None
    - Digits only

    Exemple: format_numeric(123, 5) → "00123"
    Exemple: format_numeric(None, 5) → "     "
    """
    if value is None:
        return ' ' * width

    # Convertir en int puis string (enlève décimales si présentes)
    try:
        n = int(value)
        s = str(n)
        if len(s) > width:
            s = s[:width]
        return s.rjust(width, '0')
    except (ValueError, TypeError):
        return ' ' * width


def format_date(date_value):
    """
    Formatte une date au format JJ/MM/AAAA (10 chars).
    - None → espaces

    Exemple: format_date(datetime.date(2025, 12, 30)) → "30/12/2025"
    """
    if date_value is None:
        return ' ' * 10

    if isinstance(date_value, str):
        # Déjà formatée ou vide
        if len(date_value) == 10:
            return date_value
        return ' ' * 10

    try:
        return date_value.strftime('%d/%m/%Y')
    except AttributeError:
        return ' ' * 10


def format_amount_8(montant):
    """
    Formatte un montant au format 99999,99 (8 chars) pour FACTURATION.
    - Virgule comme séparateur décimal (pas point)
    - Padding à gauche avec zéros
    - 2 décimales
    - None → "0000,00"

    Exemple: format_amount_8(1234.56) → "01234,56"
    Exemple: format_amount_8(None) → "0000,00"
    """
    if montant is None:
        montant = 0.0

    try:
        # Convertir en float
        montant_float = float(montant)

        # Formater avec 2 décimales, virgule
        montant_str = f"{montant_float:.2f}".replace('.', ',')

        # Padding gauche avec zéros (8 chars total)
        return montant_str.rjust(8, '0')
    except (ValueError, TypeError):
        return "0000,00"


def format_amount_10(montant):
    """
    Formatte un montant au format 9999999,99 (10 chars) pour SALAIRE/REVENUS.
    - Virgule comme séparateur décimal (pas point)
    - Padding à gauche avec zéros
    - 2 décimales
    - None → "00000000,00"

    Exemple: format_amount_10(123456.78) → "0123456,78"
    Exemple: format_amount_10(None) → "00000000,00"
    """
    if montant is None:
        montant = 0.0

    try:
        # Convertir en float
        montant_float = float(montant)

        # Formater avec 2 décimales, virgule
        montant_str = f"{montant_float:.2f}".replace('.', ',')

        # Padding gauche avec zéros (10 chars total)
        return montant_str.rjust(10, '0')
    except (ValueError, TypeError):
        return "00000000,00"


def format_period_2(periode):
    """
    Formatte une période de versement (2 chars).
    - Accepte -1 comme valeur valide
    - Padding à gauche avec espaces si None
    - Padding à gauche avec zéros si valeur présente

    Exemple: format_period_2(12) → "12"
    Exemple: format_period_2(-1) → "-1"
    Exemple: format_period_2(None) → "  "
    """
    if periode is None:
        return '  '

    try:
        n = int(periode)
        s = str(n)
        if len(s) > 2:
            s = s[:2]
        # Si négatif (-1), pas de padding zéro supplémentaire
        if n < 0:
            return s.rjust(2)
        else:
            return s.rjust(2, '0')
    except (ValueError, TypeError):
        return '  '


# ============================================================================
# FONCTION PRINCIPALE - Génération ligne d'export
# ============================================================================

def generate_eos_export_line_strict(donnee, donnee_enqueteur, facturation=None):
    """
    Génère une ligne d'export au format "Réponses EOS" (fixed-width).

    STRICTEMENT CONFORME AU CAHIER DES CHARGES (pages 15-21).

    Utilise FIELD_SPECS pour garantir:
    - Ordre exact des champs
    - Largeur exacte de chaque champ
    - Formatage conforme (padding, séparateur décimal, etc.)
    - CRLF Windows (\\r\\n)

    Args:
        donnee: Objet Donnee (table donnees)
        donnee_enqueteur: Objet DonneeEnqueteur (table donnees_enqueteur)
        facturation: Objet EnqueteFacturation (optionnel, pour fallback montants)

    Returns:
        str: Ligne formatée + CRLF, ou None si erreur/champs manquants
    """
    # ===== VALIDATION HARD DES CHAMPS OBLIGATOIRES =====
    champs_obligatoires = {
        'numeroDossier': getattr(donnee, 'numeroDossier', None),
        'referenceDossier': getattr(donnee, 'referenceDossier', None),
        'numeroInterlocuteur': getattr(donnee, 'numeroInterlocuteur', None),
        'guidInterlocuteur': getattr(donnee, 'guidInterlocuteur', None),
        'typeDemande': getattr(donnee, 'typeDemande', None),
        'numeroDemande': getattr(donnee, 'numeroDemande', None),
        'forfaitDemande': getattr(donnee, 'forfaitDemande', None),
        'code_resultat': getattr(donnee_enqueteur, 'code_resultat', None),
        'elements_retrouves': getattr(donnee_enqueteur, 'elements_retrouves', None),
    }

    champs_manquants = [nom for nom, val in champs_obligatoires.items() if not val]
    if champs_manquants:
        logger.warning(f"Enquête ID={donnee.id} REJETÉE - champs obligatoires manquants: {', '.join(champs_manquants)}")
        return None

    # Déterminer si c'est une contestation
    est_contestation = (getattr(donnee, 'typeDemande', '') == 'CON')

    # ===== GÉNÉRATION DE LA LIGNE (spec-driven) =====
    fields = []

    for field_name, width, field_type, source_expr, comment in EOS_REPONSES_FIELD_SPECS:
        # Extraire la valeur depuis la source appropriée
        value = _extract_field_value(field_name, source_expr, donnee, donnee_enqueteur, facturation, est_contestation)

        # Formater selon le type
        if field_type == 'alpha':
            formatted = format_alpha(value, width)
        elif field_type == 'numeric':
            formatted = format_numeric(value, width)
        elif field_type == 'date':
            formatted = format_date(value)
        elif field_type == 'amount8':
            formatted = format_amount_8(value)
        elif field_type == 'amount10':
            formatted = format_amount_10(value)
        elif field_type == 'period2':
            formatted = format_period_2(value)
        else:
            logger.error(f"Type de champ inconnu: {field_type} pour {field_name}")
            formatted = ' ' * width

        fields.append(formatted)

    # Joindre tous les champs
    line = ''.join(fields)

    # ===== VALIDATION HARD DE LA LONGUEUR =====
    if len(line) != EXPECTED_LINE_LENGTH:
        logger.error(f"ERREUR LONGUEUR export EOS: enquête ID={donnee.id}")
        logger.error(f"  Attendu: {EXPECTED_LINE_LENGTH} chars")
        logger.error(f"  Obtenu:  {len(line)} chars")
        logger.error(f"  Différence: {len(line) - EXPECTED_LINE_LENGTH:+d} chars")
        return None

    # Ajouter CRLF Windows
    return line + '\r\n'


def _extract_field_value(field_name, source_expr, donnee, donnee_enqueteur, facturation, est_contestation):
    """
    Extrait la valeur d'un champ depuis les objets source.

    Gère les expressions source (e.g., "e.nom_corrige or d.nom").
    """
    d = donnee
    e = donnee_enqueteur
    f = facturation

    # Cas spéciaux
    if source_expr == '""':
        # Champs toujours vides (numeroCompte, RIB)
        return ''

    if 'if CON else' in source_expr:
        # Champs conditionnels contestation
        if est_contestation:
            # Extraire la partie avant "if CON"
            field_expr = source_expr.split(' if CON')[0].strip()
        else:
            return ''
    else:
        field_expr = source_expr

    if 'today()' in field_expr:
        # Date du jour
        return datetime.date.today()

    # Gérer les expressions "e.X or d.Y" (priorité)
    if ' or ' in field_expr:
        parts = field_expr.split(' or ')
        for part in parts:
            val = _get_attr_safe(part.strip(), d, e, f)
            if val:
                return val
        return None

    # Expression simple (e.X, d.Y, f.Z)
    return _get_attr_safe(field_expr, d, e, f)


def _get_attr_safe(expr, d, e, f):
    """
    Récupère un attribut de manière sécurisée.

    Exemples:
        "d.nom" → getattr(donnee, 'nom', None)
        "e.qualite_corrigee" → getattr(donnee_enqueteur, 'qualite_corrigee', None)
    """
    if expr.startswith('d.'):
        attr_name = expr[2:]
        return getattr(d, attr_name, None)
    elif expr.startswith('e.'):
        attr_name = expr[2:]
        return getattr(e, attr_name, None)
    elif expr.startswith('f.'):
        attr_name = expr[2:]
        return getattr(f, attr_name, None) if f else None
    else:
        return None


# ============================================================================
# DEBUG HELPER - Parser une ligne exportée
# ============================================================================

def debug_parse_line_strict(line):
    """
    Parse une ligne d'export EOS et affiche tous les champs.

    Utile pour debugging et vérification visuelle.

    Args:
        line: Ligne complète (avec ou sans CRLF)

    Returns:
        dict: {field_name: field_value}
    """
    # Retirer CRLF si présent
    line_data = line.rstrip('\r\n')

    print(f"\n{'='*80}")
    print(f"DEBUG PARSE LIGNE (longueur: {len(line_data)})")
    print(f"{'='*80}\n")

    parsed = {}
    pos = 0

    for field_name, width, field_type, source_expr, comment in EOS_REPONSES_FIELD_SPECS:
        if pos + width > len(line_data):
            print(f"⚠️  ERREUR: position {pos} + largeur {width} dépasse longueur ligne {len(line_data)}")
            break

        value = line_data[pos:pos+width]
        parsed[field_name] = value

        # Affichage formaté
        print(f"{field_name:30s} [{pos:4d}-{pos+width:4d}] ({width:3d}) : '{value}' | {comment}")

        pos += width

    print(f"\n{'='*80}\n")

    return parsed


# ============================================================================
# CHECKLIST CHAMPS/TAILLES (auto-généré depuis FIELD_SPECS)
# ============================================================================

def print_field_checklist():
    """
    Affiche une checklist de tous les champs avec leurs tailles.

    Utile pour vérification manuelle vs cahier des charges.
    """
    print("\n" + "="*80)
    print("CHECKLIST CHAMPS/TAILLES - Format 'Réponses EOS'")
    print("="*80 + "\n")

    total = 0
    section = None

    for field_name, width, field_type, source_expr, comment in EOS_REPONSES_FIELD_SPECS:
        # Détection changement de section (basé sur commentaire)
        if '=====' in comment:
            if section:
                print(f"  Sous-total: {total} chars\n")
            section = comment
            print(f"{section}")
            total = 0

        print(f"  [{width:3d}] {field_name:30s} ({field_type:8s}) - {comment}")
        total += width

    print(f"  Sous-total: {total} chars\n")
    print(f"{'='*80}")
    print(f"TOTAL: {EXPECTED_LINE_LENGTH} caractères")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    # Afficher la checklist au lancement
    print_field_checklist()
