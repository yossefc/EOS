"""Add proximite column to donnees_enqueteur

Revision ID: 016_add_proximite
Revises: 015_enlarge_sherlock_columns
Create Date: 2026-02-18
"""

from alembic import op
import sqlalchemy as sa


revision = "016_add_proximite"
down_revision = "015_enlarge_sherlock_columns"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("donnees_enqueteur", sa.Column("proximite", sa.Text(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE donnees_enqueteur "
            "SET proximite = elements_retrouves "
            "WHERE proximite IS NULL AND elements_retrouves IS NOT NULL"
        )
    )


def downgrade():
    op.drop_column("donnees_enqueteur", "proximite")
