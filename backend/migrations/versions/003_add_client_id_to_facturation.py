"""
Migration pour ajouter client_id à EnqueteFacturation et contrainte unique

Date: 24 décembre 2025
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Ajoute:
    1. Colonne client_id à enquete_facturation
    2. Contrainte unique (donnee_id, donnee_enqueteur_id)
    3. Index sur client_id
    """
    
    # 1. Ajouter colonne client_id (nullable temporairement)
    op.add_column('enquete_facturation', 
        sa.Column('client_id', sa.Integer(), nullable=True)
    )
    
    # 2. Remplir client_id depuis la table donnees
    op.execute("""
        UPDATE enquete_facturation ef
        SET client_id = (
            SELECT d.client_id
            FROM donnees d
            WHERE d.id = ef.donnee_id
        )
        WHERE ef.client_id IS NULL
    """)
    
    # 3. Rendre client_id NOT NULL
    op.alter_column('enquete_facturation', 'client_id',
        existing_type=sa.Integer(),
        nullable=False
    )
    
    # 4. Ajouter contrainte FK
    op.create_foreign_key(
        'fk_enquete_facturation_client_id',
        'enquete_facturation', 'clients',
        ['client_id'], ['id']
    )
    
    # 5. Ajouter index sur client_id pour performance
    op.create_index(
        'ix_enquete_facturation_client_id',
        'enquete_facturation',
        ['client_id']
    )
    
    # 6. Ajouter contrainte unique pour éviter doublons
    # Vérifier d'abord s'il y a des doublons existants
    op.execute("""
        DELETE FROM enquete_facturation
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM enquete_facturation
            GROUP BY donnee_id, donnee_enqueteur_id
        )
    """)
    
    # Créer la contrainte unique
    op.create_unique_constraint(
        'uq_enquete_facturation_donnee',
        'enquete_facturation',
        ['donnee_id', 'donnee_enqueteur_id']
    )
    
    print("✅ Migration appliquée : client_id + contrainte unique ajoutés à enquete_facturation")


def downgrade():
    """
    Annule les changements :
    1. Supprime contrainte unique
    2. Supprime index client_id
    3. Supprime FK client_id
    4. Supprime colonne client_id
    """
    
    # 1. Supprimer contrainte unique
    op.drop_constraint(
        'uq_enquete_facturation_donnee',
        'enquete_facturation',
        type_='unique'
    )
    
    # 2. Supprimer index
    op.drop_index(
        'ix_enquete_facturation_client_id',
        'enquete_facturation'
    )
    
    # 3. Supprimer FK
    op.drop_constraint(
        'fk_enquete_facturation_client_id',
        'enquete_facturation',
        type_='foreignkey'
    )
    
    # 4. Supprimer colonne
    op.drop_column('enquete_facturation', 'client_id')
    
    print("✅ Migration annulée : client_id supprimé de enquete_facturation")

