"""Augmenter la taille des champs tarif_code pour PARTNER

Revision ID: 012
Revises: 011
Create Date: 2025-12-23 17:52:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """
    Augmente la taille des colonnes tarif_*_code de VARCHAR(10) à VARCHAR(100)
    pour supporter les textes de confirmation PARTNER (ex: "Confirmé par téléphone")
    """
    # Modifier les colonnes dans enquete_facturation
    op.alter_column('enquete_facturation', 'tarif_eos_code',
                    existing_type=sa.String(10),
                    type_=sa.String(100),
                    existing_nullable=True)
    
    op.alter_column('enquete_facturation', 'tarif_enqueteur_code',
                    existing_type=sa.String(10),
                    type_=sa.String(100),
                    existing_nullable=True)
    
    print("✓ Colonnes tarif_*_code augmentées à VARCHAR(100)")


def downgrade():
    """
    Retour à VARCHAR(10)
    ATTENTION : Si des valeurs > 10 caractères existent, elles seront tronquées !
    """
    op.alter_column('enquete_facturation', 'tarif_eos_code',
                    existing_type=sa.String(100),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    op.alter_column('enquete_facturation', 'tarif_enqueteur_code',
                    existing_type=sa.String(100),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    print("✓ Colonnes tarif_*_code réduites à VARCHAR(10)")

