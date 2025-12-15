"""Add multi-client support with dynamic import profiles

Revision ID: 002_multi_client
Revises: 001_initial
Create Date: 2025-12-10 16:00:00.000000

Cette migration ajoute le support multi-client à l'application:
- Crée la table clients
- Crée les tables import_profiles et import_field_mappings
- Ajoute client_id aux tables existantes
- Crée le client EOS par défaut avec son profil d'import
- Migre les données existantes vers le client EOS

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_multi_client'
down_revision = '001_initial'
branch_labels = None
depends_on = None


# Configuration d'import EOS (COLUMN_SPECS actuel)
EOS_COLUMN_SPECS = [
    ("numeroDossier", 0, 10),
    ("referenceDossier", 10, 15),
    ("numeroInterlocuteur", 25, 12),
    ("guidInterlocuteur", 37, 36),
    ("typeDemande", 73, 3),
    ("numeroDemande", 76, 11),
    ("numeroDemandeContestee", 87, 11),
    ("numeroDemandeInitiale", 98, 11),
    ("forfaitDemande", 109, 16),
    ("dateRetourEspere", 125, 10),
    ("qualite", 135, 10),
    ("nom", 145, 30),
    ("prenom", 175, 20),
    ("dateNaissance", 195, 10),
    ("lieuNaissance", 205, 50),
    ("codePostalNaissance", 255, 10),
    ("paysNaissance", 265, 32),
    ("nomPatronymique", 297, 30),
    ("adresse1", 327, 32),
    ("adresse2", 359, 32),
    ("adresse3", 391, 32),
    ("adresse4", 423, 32),
    ("ville", 455, 32),
    ("codePostal", 487, 10),
    ("paysResidence", 497, 32),
    ("telephonePersonnel", 529, 15),
    ("telephoneEmployeur", 544, 15),
    ("telecopieEmployeur", 559, 15),
    ("nomEmployeur", 574, 32),
    ("banqueDomiciliation", 606, 32),
    ("libelleGuichet", 638, 30),
    ("titulaireCompte", 668, 32),
    ("codeBanque", 700, 5),
    ("codeGuichet", 705, 5),
    ("numeroCompte", 710, 11),
    ("ribCompte", 721, 2),
    ("datedenvoie", 723, 10),
    ("elementDemandes", 733, 10),
    ("elementObligatoires", 743, 10),
    ("elementContestes", 753, 10),
    ("codeMotif", 763, 16),
    ("motifDeContestation", 779, 64),
    ("cumulMontantsPrecedents", 843, 8),
    ("codeSociete", 851, 2),
    ("urgence", 853, 1),
    ("commentaire", 854, 1000)
]


def upgrade():
    # ========================
    # 1. Créer la table clients
    # ========================
    op.create_table('clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('date_modification', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_clients_code', 'clients', ['code'])
    
    # ========================
    # 2. Créer la table import_profiles
    # ========================
    op.create_table('import_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('sheet_name', sa.String(length=255), nullable=True),
        sa.Column('encoding', sa.String(length=50), nullable=False, server_default='utf-8'),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('date_modification', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_profiles_client_id', 'import_profiles', ['client_id'])
    
    # ========================
    # 3. Créer la table import_field_mappings
    # ========================
    op.create_table('import_field_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('import_profile_id', sa.Integer(), nullable=False),
        sa.Column('internal_field', sa.String(length=100), nullable=False),
        sa.Column('start_pos', sa.Integer(), nullable=True),
        sa.Column('length', sa.Integer(), nullable=True),
        sa.Column('column_name', sa.String(length=255), nullable=True),
        sa.Column('column_index', sa.Integer(), nullable=True),
        sa.Column('strip_whitespace', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('default_value', sa.String(length=255), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['import_profile_id'], ['import_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_field_mapping_profile', 'import_field_mappings', ['import_profile_id'])
    op.create_index('idx_field_mapping_field', 'import_field_mappings', ['internal_field'])
    
    # ========================
    # 4. Ajouter client_id aux tables existantes
    # ========================
    
    # 4.1 Ajouter client_id à fichiers (temporairement nullable)
    op.add_column('fichiers', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_index('ix_fichiers_client_id', 'fichiers', ['client_id'])
    
    # 4.2 Ajouter client_id à donnees (temporairement nullable)
    op.add_column('donnees', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_index('idx_donnee_client_id', 'donnees', ['client_id'])
    op.create_index('idx_donnee_client_statut', 'donnees', ['client_id', 'statut_validation'])
    
    # 4.3 Ajouter client_id à donnees_enqueteur (temporairement nullable)
    op.add_column('donnees_enqueteur', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_index('idx_donnee_enqueteur_client_id', 'donnees_enqueteur', ['client_id'])
    
    # 4.4 Ajouter client_id à enquete_archive_files si existe (temporairement nullable)
    op.add_column('enquete_archive_files', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_index('idx_archive_file_client_id', 'enquete_archive_files', ['client_id'])
    
    # 4.5 Ajouter client_id à export_batches si existe (temporairement nullable)
    op.add_column('export_batches', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_index('idx_export_batch_client_id', 'export_batches', ['client_id'])
    
    # ========================
    # 5. Insérer le client EOS par défaut
    # ========================
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO clients (code, nom, actif, date_creation)
        VALUES ('EOS', 'EOS France', true, NOW())
    """))
    
    # ========================
    # 6. Créer le profil d'import EOS
    # ========================
    connection.execute(sa.text("""
        INSERT INTO import_profiles (client_id, name, file_type, encoding, actif, date_creation)
        VALUES (1, 'EOS TXT Format Standard', 'TXT_FIXED', 'utf-8', true, NOW())
    """))
    
    # ========================
    # 7. Insérer les mappings de champs pour EOS
    # ========================
    for field_name, start_pos, length in EOS_COLUMN_SPECS:
        connection.execute(sa.text(f"""
            INSERT INTO import_field_mappings 
                (import_profile_id, internal_field, start_pos, length, strip_whitespace, is_required, date_creation)
            VALUES 
                (1, '{field_name}', {start_pos}, {length}, true, false, NOW())
        """))
    
    # ========================
    # 8. Migrer les données existantes vers client EOS (client_id = 1)
    # ========================
    
    # 8.1 Mettre à jour fichiers
    connection.execute(sa.text("UPDATE fichiers SET client_id = 1 WHERE client_id IS NULL"))
    
    # 8.2 Mettre à jour donnees
    connection.execute(sa.text("UPDATE donnees SET client_id = 1 WHERE client_id IS NULL"))
    
    # 8.3 Mettre à jour donnees_enqueteur
    connection.execute(sa.text("UPDATE donnees_enqueteur SET client_id = 1 WHERE client_id IS NULL"))
    
    # 8.4 Mettre à jour enquete_archive_files
    connection.execute(sa.text("UPDATE enquete_archive_files SET client_id = 1 WHERE client_id IS NULL"))
    
    # 8.5 Mettre à jour export_batches
    connection.execute(sa.text("UPDATE export_batches SET client_id = 1 WHERE client_id IS NULL"))
    
    # ========================
    # 9. Rendre client_id NOT NULL et ajouter les contraintes FK
    # ========================
    
    # 9.1 fichiers
    op.alter_column('fichiers', 'client_id', nullable=False)
    op.create_foreign_key('fk_fichiers_client_id', 'fichiers', 'clients', ['client_id'], ['id'])
    
    # 9.2 donnees
    op.alter_column('donnees', 'client_id', nullable=False)
    op.create_foreign_key('fk_donnees_client_id', 'donnees', 'clients', ['client_id'], ['id'])
    
    # 9.3 donnees_enqueteur
    op.alter_column('donnees_enqueteur', 'client_id', nullable=False)
    op.create_foreign_key('fk_donnees_enqueteur_client_id', 'donnees_enqueteur', 'clients', ['client_id'], ['id'])
    
    # 9.4 enquete_archive_files
    op.alter_column('enquete_archive_files', 'client_id', nullable=False)
    op.create_foreign_key('fk_enquete_archive_files_client_id', 'enquete_archive_files', 'clients', ['client_id'], ['id'])
    
    # 9.5 export_batches
    op.alter_column('export_batches', 'client_id', nullable=False)
    op.create_foreign_key('fk_export_batches_client_id', 'export_batches', 'clients', ['client_id'], ['id'])


def downgrade():
    """
    Rollback: Supprime le support multi-client
    ATTENTION: Cette opération supprimera les données de clients autres que EOS
    """
    
    # Supprimer les contraintes FK et colonnes client_id
    op.drop_constraint('fk_export_batches_client_id', 'export_batches', type_='foreignkey')
    op.drop_index('idx_export_batch_client_id', 'export_batches')
    op.drop_column('export_batches', 'client_id')
    
    op.drop_constraint('fk_enquete_archive_files_client_id', 'enquete_archive_files', type_='foreignkey')
    op.drop_index('idx_archive_file_client_id', 'enquete_archive_files')
    op.drop_column('enquete_archive_files', 'client_id')
    
    op.drop_constraint('fk_donnees_enqueteur_client_id', 'donnees_enqueteur', type_='foreignkey')
    op.drop_index('idx_donnee_enqueteur_client_id', 'donnees_enqueteur')
    op.drop_column('donnees_enqueteur', 'client_id')
    
    op.drop_constraint('fk_donnees_client_id', 'donnees', type_='foreignkey')
    op.drop_index('idx_donnee_client_statut', 'donnees')
    op.drop_index('idx_donnee_client_id', 'donnees')
    op.drop_column('donnees', 'client_id')
    
    op.drop_constraint('fk_fichiers_client_id', 'fichiers', type_='foreignkey')
    op.drop_index('ix_fichiers_client_id', 'fichiers')
    op.drop_column('fichiers', 'client_id')
    
    # Supprimer les tables
    op.drop_index('idx_field_mapping_field', 'import_field_mappings')
    op.drop_index('idx_field_mapping_profile', 'import_field_mappings')
    op.drop_table('import_field_mappings')
    
    op.drop_index('ix_import_profiles_client_id', 'import_profiles')
    op.drop_table('import_profiles')
    
    op.drop_index('ix_clients_code', 'clients')
    op.drop_table('clients')


