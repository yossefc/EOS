"""Agrandir colonnes text dans donnees_enqueteur

Revision ID: 007_enlarge_donnees_enqueteur_columns
Revises: 006_add_confirmation_options
Create Date: 2025-12-31 22:10:00

Agrandir les colonnes de texte qui sont trop petites (VARCHAR(10) -> VARCHAR(255))
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_enlarge_donnees_enqueteur_columns'
down_revision = '006_add_confirmation_options'
branch_labels = None
depends_on = None


def upgrade():
    """Agrandit les colonnes de texte dans donnees_enqueteur"""
    
    print("Agrandissement des colonnes dans donnees_enqueteur...")
    
    # Agrandir elements_retrouves de VARCHAR(10) à VARCHAR(255)
    op.alter_column('donnees_enqueteur', 'elements_retrouves',
                    existing_type=sa.String(10),
                    type_=sa.String(255),
                    existing_nullable=True)
    print("✓ elements_retrouves : VARCHAR(10) → VARCHAR(255)")
    
    # Agrandir code_resultat de VARCHAR(10) à VARCHAR(50)
    op.alter_column('donnees_enqueteur', 'code_resultat',
                    existing_type=sa.String(10),
                    type_=sa.String(50),
                    existing_nullable=True)
    print("✓ code_resultat : VARCHAR(10) → VARCHAR(50)")
    
    # Agrandir flag_etat_civil_errone de VARCHAR(10) à VARCHAR(50)
    op.alter_column('donnees_enqueteur', 'flag_etat_civil_errone',
                    existing_type=sa.String(10),
                    type_=sa.String(50),
                    existing_nullable=True)
    print("✓ flag_etat_civil_errone : VARCHAR(10) → VARCHAR(50)")
    
    print("✅ Migration 007 : Colonnes agrandies dans donnees_enqueteur")


def downgrade():
    """Réduit les colonnes à leur taille originale"""
    
    op.alter_column('donnees_enqueteur', 'flag_etat_civil_errone',
                    existing_type=sa.String(50),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    op.alter_column('donnees_enqueteur', 'code_resultat',
                    existing_type=sa.String(50),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    op.alter_column('donnees_enqueteur', 'elements_retrouves',
                    existing_type=sa.String(255),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    print("✓ Colonnes réduites à leur taille originale")

