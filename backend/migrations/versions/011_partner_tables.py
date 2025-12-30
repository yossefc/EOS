"""Add PARTNER tables for keywords, requests, and tarif rules

Revision ID: 011
Revises: 010
Create Date: 2025-12-18 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    """
    Crée les tables pour la gestion PARTNER:
    - partner_request_keywords: Mots-clés pour parser RECHERCHE
    - partner_case_requests: Demandes par dossier (normalisées)
    - partner_tarif_rules: Tarifs combinés (lettre + demandes)
    """
    
    # 1. Table des mots-clés (admin editable)
    op.create_table(
        'partner_request_keywords',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('request_code', sa.String(20), nullable=False),  # ADDRESS|PHONE|EMPLOYER|BANK|BIRTH
        sa.Column('pattern', sa.String(100), nullable=False),      # ex: "ADRESSE", "EMPLOYEUR"
        sa.Column('is_regex', sa.Boolean(), default=False),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_partner_keywords_client', 'partner_request_keywords', ['client_id'])
    op.create_index('idx_partner_keywords_code', 'partner_request_keywords', ['request_code'])
    
    # 2. Table des demandes par dossier (normalisation)
    op.create_table(
        'partner_case_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donnee_id', sa.Integer(), nullable=False),
        sa.Column('request_code', sa.String(20), nullable=False),  # ADDRESS|PHONE|EMPLOYER|BANK|BIRTH
        sa.Column('requested', sa.Boolean(), default=True),        # Demandé dans RECHERCHE
        sa.Column('found', sa.Boolean(), default=False),           # Trouvé par l'enquêteur
        sa.Column('status', sa.String(10), nullable=True),         # POS|NEG
        sa.Column('memo', sa.Text(), nullable=True),               # Explication si NEG
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['donnee_id'], ['donnees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('donnee_id', 'request_code', name='uq_partner_case_request')
    )
    op.create_index('idx_partner_requests_donnee', 'partner_case_requests', ['donnee_id'])
    op.create_index('idx_partner_requests_status', 'partner_case_requests', ['status'])
    
    # 3. Table des tarifs combinés (lettre + demandes)
    op.create_table(
        'partner_tarif_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('tarif_lettre', sa.String(5), nullable=False),   # A, B, C, etc.
        sa.Column('request_key', sa.String(100), nullable=False),  # "ADDRESS" ou "ADDRESS+EMPLOYER"
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id', 'tarif_lettre', 'request_key', name='uq_partner_tarif_rule')
    )
    op.create_index('idx_partner_tarifs_client', 'partner_tarif_rules', ['client_id', 'tarif_lettre'])


def downgrade():
    """
    Supprime les tables PARTNER
    """
    op.drop_index('idx_partner_tarifs_client', table_name='partner_tarif_rules')
    op.drop_table('partner_tarif_rules')
    
    op.drop_index('idx_partner_requests_status', table_name='partner_case_requests')
    op.drop_index('idx_partner_requests_donnee', table_name='partner_case_requests')
    op.drop_table('partner_case_requests')
    
    op.drop_index('idx_partner_keywords_code', table_name='partner_request_keywords')
    op.drop_index('idx_partner_keywords_client', table_name='partner_request_keywords')
    op.drop_table('partner_request_keywords')



