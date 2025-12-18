"""Add dateNaissance_maj and lieuNaissance_maj to Donnee table

Revision ID: 009
Revises: 008
Create Date: 2025-12-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les champs de naissance mise à jour dans la table donnees
    op.add_column('donnees', sa.Column('dateNaissance_maj', sa.Date(), nullable=True))
    op.add_column('donnees', sa.Column('lieuNaissance_maj', sa.String(length=50), nullable=True))
    
    # Créer des index pour optimiser les requêtes
    op.create_index('idx_donnee_dateNaissance_maj', 'donnees', ['dateNaissance_maj'], unique=False)


def downgrade():
    # Supprimer les index
    op.drop_index('idx_donnee_dateNaissance_maj', table_name='donnees')
    
    # Supprimer les colonnes
    op.drop_column('donnees', 'lieuNaissance_maj')
    op.drop_column('donnees', 'dateNaissance_maj')

