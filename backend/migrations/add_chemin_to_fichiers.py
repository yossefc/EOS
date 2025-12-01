"""
Migration pour ajouter la colonne 'chemin' à la table 'fichiers'
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Ajouter la colonne chemin à la table fichiers"""
    # Vérifier si la colonne n'existe pas déjà avant de l'ajouter
    op.add_column('fichiers', sa.Column('chemin', sa.String(500), nullable=True))

def downgrade():
    """Supprimer la colonne chemin de la table fichiers"""
    op.drop_column('fichiers', 'chemin')



