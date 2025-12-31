"""Créer table tarifs_client

Revision ID: 008_create_tarifs_client
Revises: 007_enq_cols
Create Date: 2025-12-31 23:00:00

Crée la table tarifs_client pour stocker les tarifs spécifiques aux clients (PARTNER, etc.)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_tarifs_client'
down_revision = '007_enq_cols'
branch_labels = None
depends_on = None


def upgrade():
    """Crée la table tarifs_client"""
    
    print("Création de la table tarifs_client...")
    
    op.create_table(
        'tarifs_client',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('code_lettre', sa.String(10), nullable=False),
        sa.Column('description', sa.String(100), nullable=True),
        sa.Column('montant', sa.Numeric(8, 2), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Créer les index
    op.create_index('ix_tarifs_client_client_id', 'tarifs_client', ['client_id'])
    op.create_index('ix_tarifs_client_code_lettre', 'tarifs_client', ['client_id', 'code_lettre', 'actif'])
    
    print("✓ Table tarifs_client créée")
    print("✓ Index créés")
    print("✅ Migration 008 : Table tarifs_client créée avec succès")


def downgrade():
    """Supprime la table tarifs_client"""
    
    op.drop_index('ix_tarifs_client_code_lettre', table_name='tarifs_client')
    op.drop_index('ix_tarifs_client_client_id', table_name='tarifs_client')
    op.drop_table('tarifs_client')
    
    print("✓ Table tarifs_client supprimée")

