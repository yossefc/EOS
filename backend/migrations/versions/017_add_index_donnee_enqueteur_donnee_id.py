"""Add index on donnees_enqueteur.donnee_id for performance

Revision ID: 017
"""
from alembic import op

def upgrade():
    op.create_index('idx_donnee_enqueteur_donnee_id', 'donnees_enqueteur', ['donnee_id'])

def downgrade():
    op.drop_index('idx_donnee_enqueteur_donnee_id', table_name='donnees_enqueteur')
