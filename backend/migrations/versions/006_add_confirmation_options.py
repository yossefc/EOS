"""Ajouter table confirmation_options pour PARTNER

Revision ID: 006_add_confirmation_options
Revises: 005_add_partner_columns
Create Date: 2025-12-31 22:00:00

Table pour gérer les options de confirmation PARTNER (téléphone, présentiel, etc.)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_confirmation_options'
down_revision = '005_add_partner_columns'
branch_labels = None
depends_on = None


def upgrade():
    """Crée la table confirmation_options"""
    
    # Vérifier si la table existe déjà
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'confirmation_options' not in tables:
        op.create_table(
            'confirmation_options',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('option_text', sa.String(100), nullable=False),
            sa.Column('usage_count', sa.Integer(), default=0, nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
            sa.UniqueConstraint('client_id', 'option_text', name='uq_confirmation_option')
        )
        
        # Créer les index
        op.create_index('idx_confirmation_client', 'confirmation_options', ['client_id'])
        op.create_index('idx_confirmation_usage', 'confirmation_options', ['usage_count'])
        
        print("✓ Table confirmation_options créée")
        
        # Insérer les options par défaut pour PARTNER
        conn.execute(sa.text("""
            INSERT INTO confirmation_options (client_id, option_text, usage_count, created_at)
            VALUES 
                (11, 'Confirmé par téléphone', 0, NOW()),
                (11, 'Confirmé sur place', 0, NOW()),
                (11, 'Confirmé par email', 0, NOW()),
                (11, 'Non confirmé', 0, NOW())
            ON CONFLICT DO NOTHING
        """))
        
        print("✓ Options de confirmation par défaut ajoutées pour PARTNER")
    else:
        print("⚠ Table confirmation_options existe déjà")
    
    print("✅ Migration 006 : Table confirmation_options créée")


def downgrade():
    """Supprime la table confirmation_options"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'confirmation_options' in tables:
        op.drop_index('idx_confirmation_usage', 'confirmation_options')
        op.drop_index('idx_confirmation_client', 'confirmation_options')
        op.drop_table('confirmation_options')
        print("✓ Table confirmation_options supprimée")

