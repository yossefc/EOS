from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Informations de révision
revision = 'add_contestation_fields'
down_revision = 'add_enqueteur_id'  # Remplacez par la précédente migration
branch_labels = None
depends_on = None

def upgrade():
    # Ajouter les colonnes pour gérer les contestations
    op.add_column('donnees', sa.Column('enquete_originale_id', sa.Integer(), nullable=True))
    op.add_column('donnees', sa.Column('est_contestation', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('donnees', sa.Column('date_contestation', sa.Date(), nullable=True))
    op.add_column('donnees', sa.Column('motif_contestation_code', sa.String(16), nullable=True))
    op.add_column('donnees', sa.Column('motif_contestation_detail', sa.String(255), nullable=True))
    
    # Ajouter une colonne pour stocker l'historique au format JSON
    op.add_column('donnees', sa.Column('historique', sa.Text(), nullable=True))
    
    # Créer une clé étrangère pour lier l'enquête contestée à l'enquête originale
    op.create_foreign_key(
        'fk_donnees_enquete_originale',
        'donnees',
        'donnees',
        ['enquete_originale_id'],
        ['id']
    )
    
    # Mettre à jour les valeurs de est_contestation pour les enregistrements existants
    op.execute("UPDATE donnees SET est_contestation = 1 WHERE typeDemande = 'CON'")
    
    # Créer un index pour optimiser les recherches
    op.create_index('idx_donnees_contestation', 'donnees', ['est_contestation'])

def downgrade():
    # Supprimer l'index
    op.drop_index('idx_donnees_contestation', table_name='donnees')
    
    # Supprimer la clé étrangère
    op.drop_constraint('fk_donnees_enquete_originale', 'donnees', type_='foreignkey')
    
    # Supprimer les colonnes ajoutées
    op.drop_column('donnees', 'historique')
    op.drop_column('donnees', 'motif_contestation_detail')
    op.drop_column('donnees', 'motif_contestation_code')
    op.drop_column('donnees', 'date_contestation')
    op.drop_column('donnees', 'est_contestation')
    op.drop_column('donnees', 'enquete_originale_id')