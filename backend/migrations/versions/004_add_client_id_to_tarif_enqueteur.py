"""Add client_id to tarif_enqueteur

Revision ID: 004_tarif_enqueteur_client
Revises: 012_enlarge_tarif_code_columns
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_tarif_enqueteur_client'
down_revision = '003_client_id_facturation'  # Après l'ajout de client_id à facturation
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne client_id (nullable pour les tarifs existants)
    op.add_column('tarifs_enqueteur', 
        sa.Column('client_id', sa.Integer(), nullable=True)
    )
    
    # Ajouter la clé étrangère
    op.create_foreign_key(
        'fk_tarif_enqueteur_client_id',
        'tarifs_enqueteur', 'clients',
        ['client_id'], ['id']
    )
    
    # Créer un index pour améliorer les performances
    op.create_index(
        'ix_tarifs_enqueteur_client_id',
        'tarifs_enqueteur',
        ['client_id']
    )


def downgrade():
    # Supprimer l'index
    op.drop_index('ix_tarifs_enqueteur_client_id', table_name='tarifs_enqueteur')
    
    # Supprimer la clé étrangère
    op.drop_constraint('fk_tarif_enqueteur_client_id', 'tarifs_enqueteur', type_='foreignkey')
    
    # Supprimer la colonne
    op.drop_column('tarifs_enqueteur', 'client_id')




