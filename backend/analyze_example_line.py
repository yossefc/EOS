#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse de la ligne exemple pour déduire les formatages exacts
"""

# Ligne exemple fournie (2618 chars)
EXAMPLE_LINE = "8293043   50839992349001 D-8293043   a924673a-fd45-4b7f-a88a-af41f95afa01ENQ                                 LDM             27/12/2025M         CUMBO                         CYRIL               14/07/1976MARSEILLE                                         13        FRANCE                                                        24/12/2025PA                   31/12/2025   24.00   24.00    0.00       0       0                                                                                                                                   112 ALLEE VAL FLEURI BOULOURIS                                  83700     ST RAPHAEL                      FRANCE                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               "

# Spécifications des champs (nom, largeur, description)
FIELD_SPECS = [
    # IDENTIFIANTS (135)
    ('numeroDossier', 10),
    ('referenceDossier', 15),
    ('numeroInterlocuteur', 12),
    ('guidInterlocuteur', 36),
    ('typeDemande', 3),
    ('numeroDemande', 11),
    ('numeroDemandeContestee', 11),
    ('numeroDemandeInitiale', 11),
    ('forfaitDemande', 16),
    ('dateRetourEspere', 10),

    # ÉTAT CIVIL (192)
    ('qualite', 10),
    ('nom', 30),
    ('prenom', 20),
    ('dateNaissance', 10),
    ('lieuNaissance', 50),
    ('codePostalNaissance', 10),
    ('paysNaissance', 32),
    ('nomPatronymique', 30),

    # RÉSULTAT (22)
    ('dateRetour', 10),
    ('codeResultat', 1),
    ('elementsRetrouves', 10),
    ('flagEtatCivilErrone', 1),

    # FACTURATION (59)
    ('numeroFacture', 9),
    ('dateFacture', 10),
    ('montantFacture', 8),
    ('tarifApplique', 8),
    ('cumulMontantsPrecedents', 8),
    ('repriseFacturation', 8),
    ('remiseEventuelle', 8),

    # DÉCÈS (67)
    ('dateDeces', 10),
    ('numeroActeDeces', 10),
    ('codeInseeDeces', 5),
    ('codePostalDeces', 10),
    ('localiteDeces', 32),

    # ADRESSE (202)
    ('adresse1', 32),
    ('adresse2', 32),
    ('adresse3', 32),
    ('adresse4', 32),
    ('codePostal', 10),
    ('ville', 32),
    ('paysResidence', 32),

    # TÉLÉPHONES (30)
    ('telephonePersonnel', 15),
    ('telephoneChezEmployeur', 15),

    # EMPLOYEUR (294)
    ('nomEmployeur', 32),
    ('telephoneEmployeur', 15),
    ('telecopieEmployeur', 15),
    ('adresse1Employeur', 32),
    ('adresse2Employeur', 32),
    ('adresse3Employeur', 32),
    ('adresse4Employeur', 32),
    ('codePostalEmployeur', 10),
    ('villeEmployeur', 32),
    ('paysEmployeur', 32),

    # BANQUE (117)
    ('banqueDomiciliation', 32),
    ('libelleGuichet', 30),
    ('titulaireCompte', 32),
    ('codeBanque', 5),
    ('codeGuichet', 5),
    ('numeroCompte', 11),
    ('ribCompte', 2),

    # REVENUS (280: 128 + 14 + 46*3)
    ('commentairesRevenus', 128),
    ('montantSalaire', 10),
    ('periodeVersementSalaire', 2),
    ('frequenceVersementSalaire', 2),
    ('natureRevenu1', 30),
    ('montantRevenu1', 10),
    ('periodeVersementRevenu1', 2),
    ('jourVersementRevenu1', 2),
    ('frequenceVersementRevenu1', 2),
    ('natureRevenu2', 30),
    ('montantRevenu2', 10),
    ('periodeVersementRevenu2', 2),
    ('jourVersementRevenu2', 2),
    ('frequenceVersementRevenu2', 2),
    ('natureRevenu3', 30),
    ('montantRevenu3', 10),
    ('periodeVersementRevenu3', 2),
    ('jourVersementRevenu3', 2),
    ('frequenceVersementRevenu3', 2),

    # MÉMOS (1256)
    ('memo1', 64),
    ('memo2', 64),
    ('memo3', 64),
    ('memo4', 64),
    ('memo5', 1000),
]

def analyze_line():
    """Analyse la ligne exemple et affiche chaque champ"""
    print(f"\n{'='*100}")
    print(f"ANALYSE LIGNE EXEMPLE (longueur totale: {len(EXAMPLE_LINE)} chars)")
    print(f"{'='*100}\n")

    pos = 0
    total_expected = sum(width for _, width in FIELD_SPECS)

    print(f"Longueur attendue (somme specs): {total_expected} chars")
    print(f"Longueur réelle: {len(EXAMPLE_LINE)} chars")
    print(f"Différence: {len(EXAMPLE_LINE) - total_expected:+d} chars\n")

    print(f"{'Champ':<35} {'Pos':<12} {'Largeur':<8} {'Valeur (repr)'}")
    print(f"{'-'*100}")

    for field_name, width in FIELD_SPECS:
        if pos + width > len(EXAMPLE_LINE):
            print(f"⚠️  ERREUR: position {pos} + largeur {width} dépasse longueur ligne")
            break

        value = EXAMPLE_LINE[pos:pos+width]
        value_repr = repr(value)

        # Détecter le formatage
        if value.strip():
            if value != value.strip():
                # Contient des espaces de padding
                if value.startswith(' '):
                    align = 'RIGHT'
                else:
                    align = 'LEFT'
            else:
                align = 'EXACT'
        else:
            align = 'EMPTY'

        print(f"{field_name:<35} [{pos:4d}-{pos+width:4d}] {width:<8} {value_repr} ({align})")

        pos += width

    print(f"\n{'-'*100}")
    print(f"Position finale: {pos} / {len(EXAMPLE_LINE)}")

    # Analyse des montants facturation
    print(f"\n{'='*100}")
    print("ANALYSE DÉTAILLÉE DES MONTANTS FACTURATION (8 chars)")
    print(f"{'='*100}\n")

    montant_positions = [
        (356, 'montantFacture'),
        (364, 'tarifApplique'),
        (372, 'cumulMontantsPrecedents'),
        (380, 'repriseFacturation'),
        (388, 'remiseEventuelle'),
    ]

    # Recalculer les positions exactes
    pos = 0
    for field_name, width in FIELD_SPECS:
        if field_name in ['montantFacture', 'tarifApplique', 'cumulMontantsPrecedents', 'repriseFacturation', 'remiseEventuelle']:
            value = EXAMPLE_LINE[pos:pos+width]
            print(f"{field_name:<30} pos={pos:4d} : {repr(value)}")

            # Analyser le formatage
            stripped = value.strip()
            if stripped:
                if '.' in stripped:
                    parts = stripped.split('.')
                    print(f"  → Séparateur décimal: POINT")
                    print(f"  → Partie entière: {repr(parts[0])}")
                    print(f"  → Partie décimale: {repr(parts[1])}")
                else:
                    print(f"  → Pas de séparateur décimal détecté")

                # Compter les espaces de padding
                leading_spaces = len(value) - len(value.lstrip(' '))
                print(f"  → Espaces de padding gauche: {leading_spaces}")
            else:
                print(f"  → VIDE (espaces)")
        pos += width

if __name__ == '__main__':
    analyze_line()
