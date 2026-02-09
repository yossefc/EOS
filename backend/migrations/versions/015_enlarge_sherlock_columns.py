"""Agrandir les colonnes sherlock_donnees trop petites

Revision ID: 015_enlarge_sherlock_columns
Revises: 014_increase_address_to_255
Create Date: 2026-02-09

Le champ ec_civilite peut contenir "Madame (célibataire ou divorcée)" (32 chars)
et les champs CP/INSEE contiennent des floats pandas comme "2200.0" (6 chars).
On agrandit toutes les colonnes String(10) pour éviter les troncatures.
"""
from alembic import op
import sqlalchemy as sa


revision = '015_enlarge_sherlock_columns'
down_revision = '014_increase_address_to_255'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Vérifier si la table existe (elle peut ne pas exister sur certaines installations)
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sherlock_donnees')"
    ))
    if not result.scalar():
        print("⚠ Table sherlock_donnees inexistante, migration ignorée")
        return

    # Civilité: 10 -> 100 (ex: "Madame (célibataire ou divorcée)")
    for col in ['ec_civilite', 'rep_ec_civilite']:
        conn.execute(sa.text(
            f'ALTER TABLE sherlock_donnees ALTER COLUMN "{col}" TYPE VARCHAR(100)'
        ))

    # CP, INSEE, numéro, cedex: 10 -> 20 (ex: "2200.0", "2722.0")
    for col in [
        'naissance_cp', 'naissance_insee',
        'ad_l4_numero', 'ad_l6_cedex', 'ad_l6_cp', 'ad_l6_insee',
        'rep_naissance_cp', 'rep_naissance_insee',
        'rep_ad_l4_numero', 'rep_ad_l6_cedex', 'rep_ad_l6_cp', 'rep_ad_l6_insee',
        'rep_dcd_cp', 'rep_dcd_insee',
    ]:
        conn.execute(sa.text(
            f'ALTER TABLE sherlock_donnees ALTER COLUMN "{col}" TYPE VARCHAR(20)'
        ))

    print("✓ Colonnes sherlock_donnees agrandies (civilite->100, cp/insee/numero->20)")


def downgrade():
    conn = op.get_bind()

    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sherlock_donnees')"
    ))
    if not result.scalar():
        return

    for col in ['ec_civilite', 'rep_ec_civilite']:
        conn.execute(sa.text(
            f'ALTER TABLE sherlock_donnees ALTER COLUMN "{col}" TYPE VARCHAR(10)'
        ))

    for col in [
        'naissance_cp', 'naissance_insee',
        'ad_l4_numero', 'ad_l6_cedex', 'ad_l6_cp', 'ad_l6_insee',
        'rep_naissance_cp', 'rep_naissance_insee',
        'rep_ad_l4_numero', 'rep_ad_l6_cedex', 'rep_ad_l6_cp', 'rep_ad_l6_insee',
        'rep_dcd_cp', 'rep_dcd_insee',
    ]:
        conn.execute(sa.text(
            f'ALTER TABLE sherlock_donnees ALTER COLUMN "{col}" TYPE VARCHAR(10)'
        ))

    print("⚠ Colonnes sherlock_donnees réduites (risque de troncature)")
