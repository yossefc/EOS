#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de vérification de la longueur des lignes d'export EOS
Format "Réponses" attendu: 2618 caractères + CRLF
"""

import sys
import os

EXPECTED_LENGTH = 2618


def verify_export_file(filepath):
    """Vérifie qu'un fichier d'export EOS est conforme"""
    print(f"\n{'='*80}")
    print(f"VÉRIFICATION EXPORT EOS: {os.path.basename(filepath)}")
    print(f"{'='*80}\n")

    if not os.path.exists(filepath):
        print(f"❌ ERREUR: Fichier introuvable: {filepath}")
        return False

    errors = 0
    warnings = 0
    ok_count = 0

    try:
        with open(filepath, 'r', encoding='cp1252') as f:
            for line_num, line in enumerate(f, 1):
                # Vérifier CRLF
                if not line.endswith('\r\n'):
                    print(f"❌ Ligne {line_num}: pas de CRLF (\\r\\n)")
                    errors += 1

                # Vérifier longueur
                line_data = line.rstrip('\r\n')
                length = len(line_data)

                if length != EXPECTED_LENGTH:
                    print(f"❌ Ligne {line_num}: longueur {length} (attendu {EXPECTED_LENGTH})")
                    print(f"   Différence: {length - EXPECTED_LENGTH:+d} caractères")
                    errors += 1
                else:
                    ok_count += 1

                # Vérifier quelques positions clés (rapide)
                if length >= 73:
                    type_demande = line_data[73:76].strip()
                    if type_demande not in ['ENQ', 'CON', '']:
                        print(f"⚠️  Ligne {line_num}: TYPE_DEMANDE suspect '{type_demande}'")
                        warnings += 1

    except UnicodeDecodeError as e:
        print(f"❌ ERREUR encodage: {e}")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

    # Résumé
    print(f"\n{'-'*80}")
    print(f"RÉSUMÉ:")
    print(f"  ✅ Lignes conformes: {ok_count}")
    print(f"  ❌ Erreurs: {errors}")
    print(f"  ⚠️  Warnings: {warnings}")
    print(f"{'-'*80}\n")

    if errors == 0:
        print("✅ FICHIER CONFORME AU FORMAT 'RÉPONSES EOS' (2618 chars + CRLF)")
        return True
    else:
        print("❌ FICHIER NON CONFORME - Corrections nécessaires")
        return False


def calculate_field_positions():
    """Calcule et affiche les positions des champs principaux"""
    print(f"\n{'='*80}")
    print("POSITIONS DES CHAMPS PRINCIPAUX (format 'Réponses EOS')")
    print(f"{'='*80}\n")

    positions = [
        (0, 10, "N° DOSSIER"),
        (10, 15, "RÉFÉRENCE DOSSIER"),
        (25, 12, "N° INTERLOCUTEUR"),
        (37, 36, "GUID INTERLOCUTEUR"),
        (73, 3, "TYPE DEMANDE (ENQ/CON)"),
        (76, 11, "N° DEMANDE"),
        (87, 11, "N° DEMANDE CONTESTÉE"),
        (98, 11, "N° DEMANDE INITIALE"),
        (109, 16, "FORFAIT DEMANDE"),
        (125, 10, "DATE RETOUR ESPÉRÉ"),
        # État civil
        (135, 10, "QUALITÉ"),
        (145, 30, "NOM"),
        (175, 20, "PRÉNOM"),
        # Résultat
        (327, 1, "CODE RÉSULTAT"),
        (328, 10, "ÉLÉMENTS RETROUVÉS"),
        # Facturation
        (330, 9, "N° FACTURE"),
        (339, 10, "DATE FACTURE"),
        (349, 8, "MONTANT FACTURE"),
        (357, 8, "TARIF APPLIQUÉ"),
        # Revenus (début)
        (1490, 128, "COMMENTAIRES REVENUS"),
        (1618, 8, "MONTANT SALAIRE"),
        # Mémos (début)
        (1754, 64, "MEMO1"),
        (2618, 0, "FIN (avant CRLF)"),
    ]

    pos = 0
    for start, width, name in positions:
        if start != pos and width > 0:
            print(f"  ... ({start - pos} chars)")
        print(f"  [{start:4d}-{start+width:4d}] ({width:3d}) : {name}")
        pos = start + width

    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    # Afficher positions des champs
    calculate_field_positions()

    # Vérifier fichier si fourni en argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Chercher le fichier d'export le plus récent
        exports_dir = os.path.join(os.path.dirname(__file__), 'exports', 'batches')
        if os.path.exists(exports_dir):
            files = [f for f in os.listdir(exports_dir) if f.endswith('.txt')]
            if files:
                files.sort(key=lambda f: os.path.getmtime(os.path.join(exports_dir, f)), reverse=True)
                filepath = os.path.join(exports_dir, files[0])
                print(f"Fichier le plus récent: {files[0]}\n")
            else:
                print("❌ Aucun fichier d'export trouvé dans backend/exports/batches/")
                sys.exit(1)
        else:
            print("❌ Dossier exports/batches introuvable")
            sys.exit(1)

    # Vérifier
    success = verify_export_file(filepath)
    sys.exit(0 if success else 1)
