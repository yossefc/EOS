"""Remove date_naissance_corrigee and lieu_naissance_corrige from DonneeEnqueteur

Revision ID: 010
Revises: 009
Create Date: 2025-12-18 15:43:48

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    """
    Supprime les colonnes date_naissance_corrigee et lieu_naissance_corrige 
    de la table donnees_enqueteur car ces données sont maintenant stockées 
    dans la table donnees (dateNaissance_maj et lieuNaissance_maj)
    """
    # Supprimer les colonnes de donnees_enqueteur
    op.drop_column('donnees_enqueteur', 'date_naissance_corrigee')
    op.drop_column('donnees_enqueteur', 'lieu_naissance_corrige')


def downgrade():
    """
    Restaure les colonnes si nécessaire (rollback)
    """
    # Recréer les colonnes si on fait un rollback
    op.add_column('donnees_enqueteur', sa.Column('date_naissance_corrigee', sa.Date(), nullable=True))
    op.add_column('donnees_enqueteur', sa.Column('lieu_naissance_corrige', sa.String(50), nullable=True))

