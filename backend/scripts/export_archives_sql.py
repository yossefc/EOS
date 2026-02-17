"""
Script d'export SQL des enquetes archivees.

Genere un fichier .sql portable contenant des INSERT INTO pour toutes les
enquetes avec statut_validation='archive' ou 'archivee', ainsi que leurs
donnees associees (donnees_enqueteur, fichiers).

Le fichier SQL genere peut etre execute sur un autre ordinateur via psql.

Usage:
    python export_archives_sql.py
    python export_archives_sql.py --output mon_export.sql
"""

import sys
import os
import argparse
import logging
from datetime import datetime, date
from decimal import Decimal

# Ajouter le dossier parent (backend/) au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Definir DATABASE_URL si non defini (PostgreSQL)
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee, Fichier
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def sql_escape(value):
    """Echappe une valeur pour l'insertion SQL"""
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return f"'{value.isoformat()}'"
    # String
    s = str(value)
    s = s.replace("'", "''")  # Echapper les apostrophes
    s = s.replace("\\", "\\\\")  # Echapper les backslashes
    s = s.replace("\n", "\\n")  # Echapper les retours a la ligne
    s = s.replace("\r", "")
    return f"'{s}'"


def generate_insert(table_name, columns, values):
    """Genere un INSERT INTO avec gestion des conflits"""
    cols_str = ', '.join(f'"{c}"' for c in columns)
    vals_str = ', '.join(sql_escape(v) for v in values)
    return f'INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str}) ON CONFLICT DO NOTHING;'


def export_clients(f, client_ids):
    """Exporte les clients necessaires"""
    clients = Client.query.filter(Client.id.in_(client_ids)).all()

    f.write('\n-- ============================================================\n')
    f.write('-- CLIENTS\n')
    f.write('-- ============================================================\n')

    for c in clients:
        cols = ['id', 'code', 'nom', 'actif', 'date_creation']
        vals = [c.id, c.code, c.nom, c.actif, c.date_creation]
        f.write(generate_insert('clients', cols, vals) + '\n')

    logger.info(f"  {len(clients)} clients exportes")


def export_fichiers(f, fichier_ids):
    """Exporte les fichiers references"""
    fichiers = Fichier.query.filter(Fichier.id.in_(fichier_ids)).all()

    f.write('\n-- ============================================================\n')
    f.write('-- FICHIERS (references des imports)\n')
    f.write('-- ============================================================\n')

    for fic in fichiers:
        cols = ['id', 'client_id', 'nom', 'chemin', 'date_upload']
        vals = [fic.id, fic.client_id, fic.nom, fic.chemin, fic.date_upload]
        f.write(generate_insert('fichiers', cols, vals) + '\n')

    logger.info(f"  {len(fichiers)} fichiers exportes")


def export_donnees(f, donnees):
    """Exporte les donnees (enquetes archivees)"""
    f.write('\n-- ============================================================\n')
    f.write('-- DONNEES (enquetes archivees)\n')
    f.write('-- ============================================================\n')

    cols = [
        'id', 'client_id', 'fichier_id', 'enqueteurId',
        'enquete_originale_id', 'est_contestation', 'date_contestation',
        'motif_contestation_code', 'motif_contestation_detail', 'historique',
        'statut_validation',
        'numeroDossier', 'referenceDossier', 'numeroInterlocuteur',
        'guidInterlocuteur', 'typeDemande', 'numeroDemande',
        'numeroDemandeContestee', 'numeroDemandeInitiale', 'forfaitDemande',
        'dateRetourEspere', 'qualite', 'nom', 'prenom',
        'dateNaissance', 'lieuNaissance', 'codePostalNaissance',
        'paysNaissance', 'nomPatronymique',
        'dateNaissance_maj', 'lieuNaissance_maj',
        'adresse1', 'adresse2', 'adresse3', 'adresse4',
        'ville', 'codePostal', 'paysResidence',
        'telephonePersonnel', 'telephoneEmployeur', 'telecopieEmployeur',
        'nomEmployeur', 'banqueDomiciliation', 'libelleGuichet',
        'titulaireCompte', 'codeBanque', 'codeGuichet',
        'numeroCompte', 'ribCompte',
        'datedenvoie', 'elementDemandes', 'elementObligatoires',
        'elementContestes', 'codeMotif', 'motifDeContestation',
        'cumulMontantsPrecedents', 'codesociete', 'urgence', 'commentaire',
        'date_butoir', 'exported', 'exported_at',
        'tarif_lettre', 'recherche', 'instructions',
        'date_jour', 'nom_complet', 'motif',
        'created_at', 'updated_at',
    ]

    for d in donnees:
        vals = [getattr(d, c, None) for c in cols]
        f.write(generate_insert('donnees', cols, vals) + '\n')


def export_donnees_enqueteur(f, donnee_ids):
    """Exporte les donnees enqueteur associees"""
    des = DonneeEnqueteur.query.filter(DonneeEnqueteur.donnee_id.in_(donnee_ids)).all()

    f.write('\n-- ============================================================\n')
    f.write('-- DONNEES ENQUETEUR (reponses associees aux archives)\n')
    f.write('-- ============================================================\n')

    cols = [
        'id', 'client_id', 'donnee_id',
        'code_resultat', 'elements_retrouves', 'flag_etat_civil_errone',
        'date_retour',
        'qualite_corrigee', 'nom_corrige', 'prenom_corrige',
        'nom_patronymique_corrige', 'code_postal_naissance_corrige',
        'pays_naissance_corrige', 'type_divergence',
        'adresse1', 'adresse2', 'adresse3', 'adresse4',
        'code_postal', 'ville', 'pays_residence',
        'telephone_personnel', 'telephone_chez_employeur',
        'nom_employeur', 'telephone_employeur', 'telecopie_employeur',
        'adresse1_employeur', 'adresse2_employeur',
        'adresse3_employeur', 'adresse4_employeur',
        'code_postal_employeur', 'ville_employeur', 'pays_employeur',
        'banque_domiciliation', 'libelle_guichet', 'titulaire_compte',
        'code_banque', 'code_guichet',
        'date_deces', 'numero_acte_deces', 'code_insee_deces',
        'code_postal_deces', 'localite_deces',
        'commentaires_revenus', 'montant_salaire',
        'periode_versement_salaire', 'frequence_versement_salaire',
        'nature_revenu1', 'montant_revenu1',
        'periode_versement_revenu1', 'frequence_versement_revenu1',
        'nature_revenu2', 'montant_revenu2',
        'periode_versement_revenu2', 'frequence_versement_revenu2',
        'nature_revenu3', 'montant_revenu3',
        'periode_versement_revenu3', 'frequence_versement_revenu3',
        'numero_facture', 'date_facture', 'montant_facture',
        'tarif_applique', 'cumul_montants_precedents',
        'reprise_facturation', 'remise_eventuelle',
        'memo1', 'memo2', 'memo3', 'memo4', 'memo5',
        'notes_personnelles',
        'created_at', 'updated_at',
    ]

    for de in des:
        vals = [getattr(de, c, None) for c in cols]
        f.write(generate_insert('donnees_enqueteur', cols, vals) + '\n')

    logger.info(f"  {len(des)} donnees_enqueteur exportees")


def main():
    parser = argparse.ArgumentParser(description="Export SQL des enquetes archivees")
    parser.add_argument('--output', '-o', default=None,
                        help='Nom du fichier SQL de sortie')
    args = parser.parse_args()

    # Nom de fichier par defaut avec timestamp
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'export_archives_{timestamp}.sql'

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        args.output
    )

    logger.info(f"Export SQL des archives vers: {output_path}")

    app = create_app()

    with app.app_context():
        # Recuperer toutes les enquetes archivees
        donnees = Donnee.query.filter(
            Donnee.statut_validation.in_(['archive', 'archivee'])
        ).order_by(Donnee.id).all()

        logger.info(f"Enquetes archivees trouvees: {len(donnees)}")

        if not donnees:
            logger.warning("Aucune enquete archivee trouvee. Rien a exporter.")
            return

        # Collecter les IDs necessaires
        donnee_ids = [d.id for d in donnees]
        fichier_ids = list(set(d.fichier_id for d in donnees if d.fichier_id))
        client_ids = list(set(d.client_id for d in donnees if d.client_id))

        # Generer le fichier SQL
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('-- ============================================================\n')
            f.write(f'-- Export des enquetes archivees\n')
            f.write(f'-- Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'-- Total enquetes: {len(donnees)}\n')
            f.write('-- ============================================================\n')
            f.write('\n')
            f.write('BEGIN;\n')
            f.write('\n')

            # 1. Exporter les clients (dependance racine)
            export_clients(f, client_ids)

            # 2. Exporter les fichiers (dependance de donnees)
            export_fichiers(f, fichier_ids)

            # 3. Exporter les donnees
            f.write('\n-- ============================================================\n')
            f.write('-- DONNEES (enquetes archivees)\n')
            f.write(f'-- Total: {len(donnees)} enquetes\n')
            f.write('-- ============================================================\n')
            export_donnees(f, donnees)
            logger.info(f"  {len(donnees)} donnees exportees")

            # 4. Exporter les donnees enqueteur
            export_donnees_enqueteur(f, donnee_ids)

            # 5. Mettre a jour les sequences auto-increment
            f.write('\n-- ============================================================\n')
            f.write('-- MISE A JOUR DES SEQUENCES (pour eviter les conflits d\'ID)\n')
            f.write('-- ============================================================\n')
            f.write("SELECT setval('clients_id_seq', (SELECT COALESCE(MAX(id), 1) FROM clients), true);\n")
            f.write("SELECT setval('fichiers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM fichiers), true);\n")
            f.write("SELECT setval('donnees_id_seq', (SELECT COALESCE(MAX(id), 1) FROM donnees), true);\n")
            f.write("SELECT setval('donnees_enqueteur_id_seq', (SELECT COALESCE(MAX(id), 1) FROM donnees_enqueteur), true);\n")

            f.write('\nCOMMIT;\n')
            f.write('\n-- Fin de l\'export\n')

        # Stats
        file_size = os.path.getsize(output_path)
        logger.info("")
        logger.info("=" * 60)
        logger.info("EXPORT TERMINE")
        logger.info("=" * 60)
        logger.info(f"  Fichier: {output_path}")
        logger.info(f"  Taille: {file_size / 1024:.1f} Ko")
        logger.info(f"  Enquetes: {len(donnees)}")
        logger.info(f"  Clients: {len(client_ids)}")
        logger.info(f"  Fichiers ref: {len(fichier_ids)}")
        logger.info("")
        logger.info("Pour importer sur l'autre machine:")
        logger.info(f"  psql -U eos_user -d eos_db -f {args.output}")


if __name__ == '__main__':
    main()
