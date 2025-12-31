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
    
    # Utiliser des commandes SQL directes pour éviter les problèmes de conversion
    conn = op.get_bind()
    
    # Agrandir elements_retrouves à TEXT
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN elements_retrouves TYPE TEXT"))
    print("✓ elements_retrouves : VARCHAR → TEXT")
    
    # Agrandir code_resultat à TEXT
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN code_resultat TYPE TEXT"))
    print("✓ code_resultat : VARCHAR → TEXT")
    
    # Agrandir flag_etat_civil_errone à TEXT
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN flag_etat_civil_errone TYPE TEXT"))
    print("✓ flag_etat_civil_errone : VARCHAR → TEXT")
    
    print("✅ Migration 007 : Colonnes converties en TEXT dans donnees_enqueteur")


def downgrade():
    """Réduit les colonnes à leur taille originale"""
    
    conn = op.get_bind()
    
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN flag_etat_civil_errone TYPE VARCHAR(10)"))
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN code_resultat TYPE VARCHAR(10)"))
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur ALTER COLUMN elements_retrouves TYPE VARCHAR(10)"))
    
    print("✓ Colonnes réduites à VARCHAR(10)")

