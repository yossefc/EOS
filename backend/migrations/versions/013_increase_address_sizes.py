"""Augmenter la taille des colonnes adresse et ville

Revision ID: 013_increase_address_sizes
Revises: 23e63946daaf
Create Date: 2026-02-04

VARCHAR(32) est trop petit pour les adresses françaises.
adresse1-4 -> VARCHAR(100), ville -> VARCHAR(50)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013_increase_address_sizes'
down_revision = '23e63946daaf'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Augmenter adresse1-4 de 32 à 100
    for col in ['adresse1', 'adresse2', 'adresse3', 'adresse4']:
        conn.execute(sa.text(
            f'ALTER TABLE donnees ALTER COLUMN "{col}" TYPE VARCHAR(100)'
        ))

    # Augmenter ville de 32 à 50
    conn.execute(sa.text(
        'ALTER TABLE donnees ALTER COLUMN ville TYPE VARCHAR(50)'
    ))

    print("✓ Colonnes adresse1-4 -> VARCHAR(100), ville -> VARCHAR(50)")


def downgrade():
    conn = op.get_bind()

    for col in ['adresse1', 'adresse2', 'adresse3', 'adresse4']:
        conn.execute(sa.text(
            f'ALTER TABLE donnees ALTER COLUMN "{col}" TYPE VARCHAR(32)'
        ))

    conn.execute(sa.text(
        'ALTER TABLE donnees ALTER COLUMN ville TYPE VARCHAR(32)'
    ))
