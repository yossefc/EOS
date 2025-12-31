"""Ajouter colonnes PARTNER à la table donnees

Revision ID: 005_add_partner_columns
Revises: 004_tarif_enqueteur_client
Create Date: 2025-12-31 16:45:00

Ajoute les colonnes spécifiques PARTNER à la table donnees :
- tarif_lettre : Code lettre du tarif (A, B, C, etc.)
- recherche : Texte de recherche PARTNER
- instructions : Instructions particulières
- date_jour : Date du jour (pour PARTNER)
- nom_complet : Nom complet formaté
- motif : Motif de la demande
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_partner_columns'
down_revision = '004_tarif_enqueteur_client'
branch_labels = None
depends_on = None


def upgrade():
    """Ajoute les colonnes PARTNER à la table donnees"""
    
    # Vérifier si les colonnes existent déjà avant de les ajouter
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('donnees')]
    
    if 'tarif_lettre' not in columns:
        op.add_column('donnees', sa.Column('tarif_lettre', sa.String(10), nullable=True))
        print("✓ Colonne tarif_lettre ajoutée")
    else:
        print("⚠ Colonne tarif_lettre existe déjà")
    
    if 'recherche' not in columns:
        op.add_column('donnees', sa.Column('recherche', sa.Text(), nullable=True))
        print("✓ Colonne recherche ajoutée")
    else:
        print("⚠ Colonne recherche existe déjà")
    
    if 'instructions' not in columns:
        op.add_column('donnees', sa.Column('instructions', sa.Text(), nullable=True))
        print("✓ Colonne instructions ajoutée")
    else:
        print("⚠ Colonne instructions existe déjà")
    
    if 'date_jour' not in columns:
        op.add_column('donnees', sa.Column('date_jour', sa.Date(), nullable=True))
        print("✓ Colonne date_jour ajoutée")
    else:
        print("⚠ Colonne date_jour existe déjà")
    
    if 'nom_complet' not in columns:
        op.add_column('donnees', sa.Column('nom_complet', sa.String(200), nullable=True))
        print("✓ Colonne nom_complet ajoutée")
    else:
        print("⚠ Colonne nom_complet existe déjà")
    
    if 'motif' not in columns:
        op.add_column('donnees', sa.Column('motif', sa.Text(), nullable=True))
        print("✓ Colonne motif ajoutée")
    else:
        print("⚠ Colonne motif existe déjà")
    
    print("✅ Migration 005 : Colonnes PARTNER ajoutées à la table donnees")


def downgrade():
    """Supprime les colonnes PARTNER de la table donnees"""
    
    # Vérifier si les colonnes existent avant de les supprimer
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('donnees')]
    
    if 'motif' in columns:
        op.drop_column('donnees', 'motif')
    
    if 'nom_complet' in columns:
        op.drop_column('donnees', 'nom_complet')
    
    if 'date_jour' in columns:
        op.drop_column('donnees', 'date_jour')
    
    if 'instructions' in columns:
        op.drop_column('donnees', 'instructions')
    
    if 'recherche' in columns:
        op.drop_column('donnees', 'recherche')
    
    if 'tarif_lettre' in columns:
        op.drop_column('donnees', 'tarif_lettre')
    
    print("✅ Colonnes PARTNER supprimées de la table donnees")

