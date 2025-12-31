"""Agrandir les colonnes tarif_*_code pour PARTNER

Revision ID: 012
Revises: 011
Create Date: 2025-12-23 17:52:00

Pour PARTNER, les codes de tarif peuvent être des phrases complètes
comme "Confirmé par téléphone" au lieu de codes courts comme "A" ou "AT".
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_enlarge_tarif_code_columns'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """Agrandit les colonnes de codes tarif de 10 à 100 caractères"""
    
    # Modifier les colonnes dans enquete_facturation
    with op.batch_alter_table('enquete_facturation', schema=None) as batch_op:
        # Agrandir tarif_eos_code de VARCHAR(10) à VARCHAR(100)
        batch_op.alter_column('tarif_eos_code',
                            existing_type=sa.String(length=10),
                            type_=sa.String(length=100),
                            existing_nullable=True)
        
        # Agrandir tarif_enqueteur_code de VARCHAR(10) à VARCHAR(100)
        batch_op.alter_column('tarif_enqueteur_code',
                            existing_type=sa.String(length=10),
                            type_=sa.String(length=100),
                            existing_nullable=True)
    
    print("✓ Colonnes tarif_*_code agrandies à 100 caractères")


def downgrade():
    """Réduit les colonnes à leur taille originale (risque de perte de données)"""
    
    with op.batch_alter_table('enquete_facturation', schema=None) as batch_op:
        # Réduire tarif_eos_code à VARCHAR(10)
        batch_op.alter_column('tarif_eos_code',
                            existing_type=sa.String(length=100),
                            type_=sa.String(length=10),
                            existing_nullable=True)
        
        # Réduire tarif_enqueteur_code à VARCHAR(10)
        batch_op.alter_column('tarif_enqueteur_code',
                            existing_type=sa.String(length=100),
                            type_=sa.String(length=10),
                            existing_nullable=True)
    
    print("⚠ Colonnes tarif_*_code réduites à 10 caractères (risque de troncature)")

