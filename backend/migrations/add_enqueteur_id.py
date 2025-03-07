from alembic import op
import sqlalchemy as sa

def upgrade():
    # Ajouter la colonne enqueteurId
    op.add_column('donnees', sa.Column('enqueteurId', sa.Integer(), nullable=True))
    
    # Ajouter la clé étrangère
    op.create_foreign_key(
        'fk_donnees_enqueteur',
        'donnees',
        'enqueteurs',
        ['enqueteurId'],
        ['id']
    )

def downgrade():
    # Supprimer la clé étrangère
    op.drop_constraint('fk_donnees_enqueteur', 'donnees', type_='foreignkey')
    
    # Supprimer la colonne
    op.drop_column('donnees', 'enqueteurId')
