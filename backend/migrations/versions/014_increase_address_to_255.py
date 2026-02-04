"""Augmenter adresse1-4 de VARCHAR(100) à VARCHAR(255)

Revision ID: 014_increase_address_to_255
Revises: 013_increase_address_sizes
Create Date: 2026-02-04

Certaines adresses PARTNER contiennent plusieurs lignes concaténées
qui dépassent 100 chars. On remet à la taille originale de 255.
"""
from alembic import op
import sqlalchemy as sa


revision = '014_increase_address_to_255'
down_revision = '013_increase_address_sizes'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    for col in ['adresse1', 'adresse2', 'adresse3', 'adresse4']:
        conn.execute(sa.text(
            f'ALTER TABLE donnees ALTER COLUMN "{col}" TYPE VARCHAR(255)'
        ))

    print("✓ Colonnes adresse1-4 -> VARCHAR(255)")


def downgrade():
    conn = op.get_bind()

    for col in ['adresse1', 'adresse2', 'adresse3', 'adresse4']:
        conn.execute(sa.text(
            f'ALTER TABLE donnees ALTER COLUMN "{col}" TYPE VARCHAR(100)'
        ))
