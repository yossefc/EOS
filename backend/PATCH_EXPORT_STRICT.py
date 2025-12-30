#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PATCH COMPLET pour backend/routes/export.py
Rend l'export "Réponses EOS" STRICTEMENT conforme à l'exemple

APPLIQUER CE PATCH :
1. Remplacer les fonctions de formatage (lignes 54-109)
2. Remplacer generate_eos_export_line (lignes 1234-1479)
3. Ajouter golden test (nouveau fichier)
"""

# ========== SECTION 1: FORMATTERS (remplacer lignes 54-109) ==========

def format_alphanum_eos(value, length):
    """
    Formate un champ alphanumérique.
    - Padding à DROITE avec espaces
    - Troncature si trop long
    - None → espaces
    """
    if value is None:
        value = ''
    value_str = clean_special_chars(str(value).strip())
    if len(value_str) > length:
        value_str = value_str[:length]
    return value_str.ljust(length)


def format_numeric_eos(value, length):
    """
    Formate un champ numérique entier.
    - None → espaces (PAS zéros)
    - Valeurs négatives (-1) → justifié droite avec espaces
    - Valeurs positives → padding gauche avec zéros

    Exemples:
        format_numeric_eos(12, 3) → "012"
        format_numeric_eos(-1, 2) → "-1"
        format_numeric_eos(None, 3) → "   "
    """
    if value is None:
        return ' ' * length

    try:
        n = int(value)
        value_str = str(n)

        if len(value_str) > length:
            value_str = value_str[:length]

        # Si négatif, pas de zero-padding (garder le signe)
        if n < 0:
            return value_str.rjust(length)
        else:
            return value_str.rjust(length, '0')
    except (ValueError, TypeError):
        return ' ' * length


def format_date_eos(date_value):
    """
    Formate une date au format JJ/MM/AAAA (10 caractères).
    None → 10 espaces
    """
    if date_value is None:
        return ' ' * 10

    if isinstance(date_value, str):
        try:
            date_value = datetime.datetime.strptime(date_value, '%Y-%m-%d').date()
        except:
            return ' ' * 10

    if isinstance(date_value, datetime.datetime):
        date_value = date_value.date()

    if isinstance(date_value, datetime.date):
        return date_value.strftime('%d/%m/%Y')

    return ' ' * 10


def format_montant_8(montant):
    """
    Formate un montant FACTURATION au format sur 8 chars.
    - Séparateur décimal: POINT (pas virgule)
    - Padding: ESPACES à gauche (pas zéros)
    - 2 décimales
    - Valeurs négatives acceptées

    Exemples (conforme ligne exemple):
        format_montant_8(24.00) → "   24.00"
        format_montant_8(0.00) → "    0.00"
        format_montant_8(None) → "    0.00"
        format_montant_8(-10.50) → "  -10.50"
    """
    if montant is None:
        montant = 0.0

    try:
        montant_float = float(montant)
        # Formater avec 2 décimales, POINT décimal
        montant_str = f"{montant_float:.2f}"

        # Right-justify avec espaces sur 8 chars
        return montant_str.rjust(8)
    except (ValueError, TypeError):
        return "    0.00"


def format_montant_10(montant):
    """
    Formate un montant REVENUS/SALAIRE au format sur 10 chars.
    - Séparateur décimal: POINT (cohérence avec montant_8)
    - Padding: ESPACES à gauche
    - 2 décimales
    - Valeurs négatives acceptées

    Exemples:
        format_montant_10(123456.78) → " 123456.78"
        format_montant_10(0.00) → "      0.00"
        format_montant_10(None) → "      0.00"
    """
    if montant is None:
        montant = 0.0

    try:
        montant_float = float(montant)
        # Formater avec 2 décimales, POINT décimal
        montant_str = f"{montant_float:.2f}"

        # Right-justify avec espaces sur 10 chars
        return montant_str.rjust(10)
    except (ValueError, TypeError):
        return "      0.00"


# ========== SECTION 2: generate_eos_export_line COMPLET (remplacer lignes 1234-1479) ==========

def generate_eos_export_line(donnee, donnee_enqueteur, enqueteur, facturation=None):
    """
    Génère une ligne d'export au format "Réponses EOS" (fixed-width 2618 chars + CRLF).

    STRICTEMENT CONFORME AU CAHIER DES CHARGES + EXEMPLE FOURNI.

    Longueur: EXACTEMENT 2618 caractères (hors CRLF) + \\r\\n

    Args:
        donnee: Objet Donnee (table donnees)
        donnee_enqueteur: Objet DonneeEnqueteur (table donnees_enqueteur)
        enqueteur: Objet Enqueteur (non utilisé, compatibilité signature)
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

    # ===== GÉNÉRATION DE LA LIGNE (ordre strict) =====
    fields = []

    # ===== A. IDENTIFIANTS (135 chars) - Source: donnees (d) =====
    fields.append(format_alphanum_eos(donnee.numeroDossier, 10))
    fields.append(format_alphanum_eos(donnee.referenceDossier, 15))
    fields.append(format_alphanum_eos(donnee.numeroInterlocuteur, 12))
    fields.append(format_alphanum_eos(donnee.guidInterlocuteur, 36))
    fields.append(format_alphanum_eos(donnee.typeDemande, 3))
    fields.append(format_alphanum_eos(donnee.numeroDemande, 11))

    # Champs contestation (vides si ENQ)
    if est_contestation:
        fields.append(format_alphanum_eos(getattr(donnee, 'numeroDemandeContestee', ''), 11))
        fields.append(format_alphanum_eos(getattr(donnee, 'numeroDemandeInitiale', ''), 11))
    else:
        fields.append(format_alphanum_eos('', 11))
        fields.append(format_alphanum_eos('', 11))

    fields.append(format_alphanum_eos(donnee.forfaitDemande, 16))
    fields.append(format_date_eos(getattr(donnee, 'dateRetourEspere', None)))

    # ===== B. ÉTAT CIVIL (192 chars) - Priorité e.*_corrige, sinon d.* =====
    qualite = getattr(donnee_enqueteur, 'qualite_corrigee', None) or getattr(donnee, 'qualite', '')
    nom = getattr(donnee_enqueteur, 'nom_corrige', None) or getattr(donnee, 'nom', '')
    prenom = getattr(donnee_enqueteur, 'prenom_corrige', None) or getattr(donnee, 'prenom', '')
    cp_naissance = getattr(donnee_enqueteur, 'code_postal_naissance_corrige', None) or getattr(donnee, 'codePostalNaissance', '')
    pays_naissance = getattr(donnee_enqueteur, 'pays_naissance_corrige', None) or getattr(donnee, 'paysNaissance', '')
    nom_patronymique = getattr(donnee_enqueteur, 'nom_patronymique_corrige', None) or getattr(donnee, 'nomPatronymique', '')

    fields.append(format_alphanum_eos(qualite, 10))
    fields.append(format_alphanum_eos(nom, 30))
    fields.append(format_alphanum_eos(prenom, 20))
    fields.append(format_date_eos(getattr(donnee, 'dateNaissance', None)))
    fields.append(format_alphanum_eos(getattr(donnee, 'lieuNaissance', ''), 50))
    fields.append(format_alphanum_eos(cp_naissance, 10))
    fields.append(format_alphanum_eos(pays_naissance, 32))
    fields.append(format_alphanum_eos(nom_patronymique, 30))

    # ===== C. RÉSULTAT (22 chars) - Source: donnees_enqueteur (e) =====
    date_retour = getattr(donnee_enqueteur, 'date_retour', None) or datetime.date.today()
    fields.append(format_date_eos(date_retour))
    fields.append(format_alphanum_eos(donnee_enqueteur.code_resultat, 1))
    fields.append(format_alphanum_eos(donnee_enqueteur.elements_retrouves, 10))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'flag_etat_civil_errone', ''), 1))

    # ===== D. FACTURATION (59 chars) - Priorité e, sinon f =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'numero_facture', ''), 9))
    fields.append(format_date_eos(getattr(donnee_enqueteur, 'date_facture', None)))

    # Montant facture: priorité e, sinon f.resultat_eos_montant
    montant_facture = getattr(donnee_enqueteur, 'montant_facture', None)
    if montant_facture is None and facturation:
        montant_facture = getattr(facturation, 'resultat_eos_montant', None)
    fields.append(format_montant_8(montant_facture))

    # Tarif appliqué: priorité e, sinon f.tarif_eos_montant
    tarif_applique = getattr(donnee_enqueteur, 'tarif_applique', None)
    if tarif_applique is None and facturation:
        tarif_applique = getattr(facturation, 'tarif_eos_montant', None)
    fields.append(format_montant_8(tarif_applique))

    # Cumul: priorité e, sinon d
    cumul = getattr(donnee_enqueteur, 'cumul_montants_precedents', None) or getattr(donnee, 'cumulMontantsPrecedents', None)
    fields.append(format_montant_8(cumul))

    fields.append(format_montant_8(getattr(donnee_enqueteur, 'reprise_facturation', None)))
    fields.append(format_montant_8(getattr(donnee_enqueteur, 'remise_eventuelle', None)))

    # ===== E. DÉCÈS (67 chars) =====
    fields.append(format_date_eos(getattr(donnee_enqueteur, 'date_deces', None)))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'numero_acte_deces', ''), 10))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_insee_deces', ''), 5))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_postal_deces', ''), 10))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'localite_deces', ''), 32))

    # ===== F. ADRESSE RÉSIDENCE (202 chars) =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse1', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse2', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse3', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse4', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_postal', ''), 10))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'ville', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'pays_residence', ''), 32))

    # ===== G. TÉLÉPHONES (30 chars) =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'telephone_personnel', ''), 15))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'telephone_chez_employeur', ''), 15))

    # ===== H. EMPLOYEUR (294 chars) =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'nom_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'telephone_employeur', ''), 15))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'telecopie_employeur', ''), 15))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse1_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse2_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse3_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'adresse4_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_postal_employeur', ''), 10))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'ville_employeur', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'pays_employeur', ''), 32))

    # ===== I. BANQUE (117 chars) - numeroCompte et RIB TOUJOURS VIDES =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'banque_domiciliation', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'libelle_guichet', ''), 30))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'titulaire_compte', ''), 32))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_banque', ''), 5))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'code_guichet', ''), 5))
    fields.append(format_alphanum_eos('', 11))  # numeroCompte - TOUJOURS VIDE
    fields.append(format_alphanum_eos('', 2))   # RIB - TOUJOURS VIDE

    # ===== J. REVENUS (274 chars: 128 + 14 + 44*3) =====
    # NOTE: PAS de champs jour_versement (longueur totale = 2618)
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'commentaires_revenus', ''), 128))

    # Salaire (14 chars: 10+2+2)
    fields.append(format_montant_10(getattr(donnee_enqueteur, 'montant_salaire', None)))
    fields.append(format_numeric_eos(getattr(donnee_enqueteur, 'periode_versement_salaire', None), 2))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'frequence_versement_salaire', ''), 2))

    # Revenu 1 (44 chars: 30+10+2+2)
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'nature_revenu1', ''), 30))
    fields.append(format_montant_10(getattr(donnee_enqueteur, 'montant_revenu1', None)))
    fields.append(format_numeric_eos(getattr(donnee_enqueteur, 'periode_versement_revenu1', None), 2))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'frequence_versement_revenu1', ''), 2))

    # Revenu 2 (44 chars: 30+10+2+2)
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'nature_revenu2', ''), 30))
    fields.append(format_montant_10(getattr(donnee_enqueteur, 'montant_revenu2', None)))
    fields.append(format_numeric_eos(getattr(donnee_enqueteur, 'periode_versement_revenu2', None), 2))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'frequence_versement_revenu2', ''), 2))

    # Revenu 3 (44 chars: 30+10+2+2)
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'nature_revenu3', ''), 30))
    fields.append(format_montant_10(getattr(donnee_enqueteur, 'montant_revenu3', None)))
    fields.append(format_numeric_eos(getattr(donnee_enqueteur, 'periode_versement_revenu3', None), 2))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'frequence_versement_revenu3', ''), 2))

    # ===== K. MÉMOS (1256 chars) =====
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'memo1', ''), 64))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'memo2', ''), 64))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'memo3', ''), 64))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'memo4', ''), 64))
    fields.append(format_alphanum_eos(getattr(donnee_enqueteur, 'memo5', ''), 1000))

    # Joindre tous les champs
    line = ''.join(fields)

    # ===== VALIDATION HARD DE LA LONGUEUR =====
    EXPECTED_LENGTH = 2618
    if len(line) != EXPECTED_LENGTH:
        logger.error(f"ERREUR LONGUEUR export EOS: enquête ID={donnee.id}")
        logger.error(f"  Attendu: {EXPECTED_LENGTH} chars")
        logger.error(f"  Obtenu:  {len(line)} chars")
        logger.error(f"  Différence: {len(line) - EXPECTED_LENGTH:+d} chars")
        return None

    # Ajouter CRLF Windows
    return line + '\r\n'


# ========== CHECKLIST CHAMPS/TAILLES (auto-vérifié) ==========
"""
IDENTIFIANTS (135):
  numeroDossier (10) + referenceDossier (15) + numeroInterlocuteur (12) +
  guidInterlocuteur (36) + typeDemande (3) + numeroDemande (11) +
  numeroDemandeContestee (11) + numeroDemandeInitiale (11) +
  forfaitDemande (16) + dateRetourEspere (10) = 135

ÉTAT CIVIL (192):
  qualite (10) + nom (30) + prenom (20) + dateNaissance (10) +
  lieuNaissance (50) + codePostalNaissance (10) + paysNaissance (32) +
  nomPatronymique (30) = 192

RÉSULTAT (22):
  dateRetour (10) + codeResultat (1) + elementsRetrouves (10) +
  flagEtatCivilErrone (1) = 22

FACTURATION (59):
  numeroFacture (9) + dateFacture (10) + montantFacture (8) +
  tarifApplique (8) + cumulMontantsPrecedents (8) +
  repriseFacturation (8) + remiseEventuelle (8) = 59

DÉCÈS (67):
  dateDeces (10) + numeroActeDeces (10) + codeInseeDeces (5) +
  codePostalDeces (10) + localiteDeces (32) = 67

ADRESSE (202):
  adresse1-4 (32*4) + codePostal (10) + ville (32) + paysResidence (32) = 202

TÉLÉPHONES (30):
  telephonePersonnel (15) + telephoneChezEmployeur (15) = 30

EMPLOYEUR (294):
  nomEmployeur (32) + telephoneEmployeur (15) + telecopieEmployeur (15) +
  adresse1-4Employeur (32*4) + codePostalEmployeur (10) +
  villeEmployeur (32) + paysEmployeur (32) = 264

BANQUE (117):
  banqueDomiciliation (32) + libelleGuichet (30) + titulaireCompte (32) +
  codeBanque (5) + codeGuichet (5) + numeroCompte (11) + ribCompte (2) = 117

REVENUS (274):
  commentairesRevenus (128) + montantSalaire (10) + periodeVersementSalaire (2) +
  frequenceVersementSalaire (2) + [nature (30) + montant (10) + periode (2) +
  frequence (2)] * 3 = 128 + 14 + 132 = 274

MÉMOS (1256):
  memo1-4 (64*4) + memo5 (1000) = 1256

TOTAL: 135 + 192 + 22 + 59 + 67 + 202 + 30 + 264 + 117 + 274 + 1256 = 2618 ✓
"""
