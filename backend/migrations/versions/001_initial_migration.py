"""Initial migration - Create all tables with indexes

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table fichiers
    op.create_table('fichiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('chemin', sa.String(length=500), nullable=True),
        sa.Column('date_upload', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table enqueteurs
    op.create_table('enqueteurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('prenom', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('telephone', sa.String(length=20), nullable=True),
        sa.Column('date_creation', sa.DateTime(), nullable=True),
        sa.Column('vpn_config_generated', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Créer la table donnees (enquêtes)
    op.create_table('donnees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fichier_id', sa.Integer(), nullable=False),
        sa.Column('enqueteurId', sa.Integer(), nullable=True),
        sa.Column('enquete_originale_id', sa.Integer(), nullable=True),
        sa.Column('est_contestation', sa.Boolean(), nullable=False),
        sa.Column('date_contestation', sa.Date(), nullable=True),
        sa.Column('motif_contestation_code', sa.String(length=16), nullable=True),
        sa.Column('motif_contestation_detail', sa.String(length=255), nullable=True),
        sa.Column('historique', sa.Text(), nullable=True),
        sa.Column('statut_validation', sa.String(length=20), nullable=False),
        sa.Column('numeroDossier', sa.String(length=10), nullable=True),
        sa.Column('referenceDossier', sa.String(length=15), nullable=True),
        sa.Column('numeroInterlocuteur', sa.String(length=12), nullable=True),
        sa.Column('guidInterlocuteur', sa.String(length=36), nullable=True),
        sa.Column('typeDemande', sa.String(length=3), nullable=True),
        sa.Column('numeroDemande', sa.String(length=11), nullable=True),
        sa.Column('numeroDemandeContestee', sa.String(length=11), nullable=True),
        sa.Column('numeroDemandeInitiale', sa.String(length=11), nullable=True),
        sa.Column('forfaitDemande', sa.String(length=16), nullable=True),
        sa.Column('dateRetourEspere', sa.Date(), nullable=True),
        sa.Column('qualite', sa.String(length=10), nullable=True),
        sa.Column('nom', sa.String(length=30), nullable=True),
        sa.Column('prenom', sa.String(length=20), nullable=True),
        sa.Column('dateNaissance', sa.Date(), nullable=True),
        sa.Column('lieuNaissance', sa.String(length=50), nullable=True),
        sa.Column('codePostalNaissance', sa.String(length=10), nullable=True),
        sa.Column('paysNaissance', sa.String(length=32), nullable=True),
        sa.Column('nomPatronymique', sa.String(length=30), nullable=True),
        sa.Column('adresse1', sa.String(length=32), nullable=True),
        sa.Column('adresse2', sa.String(length=32), nullable=True),
        sa.Column('adresse3', sa.String(length=32), nullable=True),
        sa.Column('adresse4', sa.String(length=32), nullable=True),
        sa.Column('ville', sa.String(length=32), nullable=True),
        sa.Column('codePostal', sa.String(length=10), nullable=True),
        sa.Column('paysResidence', sa.String(length=32), nullable=True),
        sa.Column('telephonePersonnel', sa.String(length=15), nullable=True),
        sa.Column('telephoneEmployeur', sa.String(length=15), nullable=True),
        sa.Column('telecopieEmployeur', sa.String(length=15), nullable=True),
        sa.Column('nomEmployeur', sa.String(length=32), nullable=True),
        sa.Column('banqueDomiciliation', sa.String(length=32), nullable=True),
        sa.Column('libelleGuichet', sa.String(length=30), nullable=True),
        sa.Column('titulaireCompte', sa.String(length=32), nullable=True),
        sa.Column('codeBanque', sa.String(length=5), nullable=True),
        sa.Column('codeGuichet', sa.String(length=5), nullable=True),
        sa.Column('numeroCompte', sa.String(length=11), nullable=True),
        sa.Column('ribCompte', sa.String(length=2), nullable=True),
        sa.Column('datedenvoie', sa.Date(), nullable=True),
        sa.Column('elementDemandes', sa.String(length=10), nullable=True),
        sa.Column('elementObligatoires', sa.String(length=10), nullable=True),
        sa.Column('elementContestes', sa.String(length=10), nullable=True),
        sa.Column('codeMotif', sa.String(length=16), nullable=True),
        sa.Column('motifDeContestation', sa.String(length=64), nullable=True),
        sa.Column('cumulMontantsPrecedents', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('codesociete', sa.String(length=2), nullable=True),
        sa.Column('urgence', sa.String(length=1), nullable=True),
        sa.Column('commentaire', sa.String(length=1000), nullable=True),
        sa.Column('date_butoir', sa.Date(), nullable=True),
        sa.Column('exported', sa.Boolean(), nullable=False),
        sa.Column('exported_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['enquete_originale_id'], ['donnees.id'], ),
        sa.ForeignKeyConstraint(['enqueteurId'], ['enqueteurs.id'], ),
        sa.ForeignKeyConstraint(['fichier_id'], ['fichiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Créer les index pour performance (20 000+ enquêtes)
    op.create_index('idx_donnee_created_at', 'donnees', ['created_at'], unique=False)
    op.create_index('idx_donnee_date_butoir', 'donnees', ['date_butoir'], unique=False)
    op.create_index('idx_donnee_enqueteurId', 'donnees', ['enqueteurId'], unique=False)
    op.create_index('idx_donnee_fichier_id', 'donnees', ['fichier_id'], unique=False)
    op.create_index('idx_donnee_nom', 'donnees', ['nom'], unique=False)
    op.create_index('idx_donnee_numeroDossier', 'donnees', ['numeroDossier'], unique=False)
    op.create_index('idx_donnee_statut_date', 'donnees', ['statut_validation', 'date_butoir'], unique=False)
    op.create_index('idx_donnee_statut_enqueteur', 'donnees', ['statut_validation', 'enqueteurId'], unique=False)
    op.create_index('idx_donnee_statut_validation', 'donnees', ['statut_validation'], unique=False)
    op.create_index('idx_donnee_typeDemande', 'donnees', ['typeDemande'], unique=False)

    # Créer la table donnees_enqueteur
    op.create_table('donnees_enqueteur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donnee_id', sa.Integer(), nullable=False),
        sa.Column('code_resultat', sa.String(length=1), nullable=True),
        sa.Column('elements_retrouves', sa.String(length=10), nullable=True),
        sa.Column('flag_etat_civil_errone', sa.String(length=1), nullable=True),
        sa.Column('date_retour', sa.Date(), nullable=True),
        sa.Column('qualite_corrigee', sa.String(length=10), nullable=True),
        sa.Column('nom_corrige', sa.String(length=30), nullable=True),
        sa.Column('prenom_corrige', sa.String(length=20), nullable=True),
        sa.Column('nom_patronymique_corrige', sa.String(length=30), nullable=True),
        sa.Column('date_naissance_corrigee', sa.Date(), nullable=True),
        sa.Column('lieu_naissance_corrige', sa.String(length=50), nullable=True),
        sa.Column('code_postal_naissance_corrige', sa.String(length=10), nullable=True),
        sa.Column('pays_naissance_corrige', sa.String(length=32), nullable=True),
        sa.Column('type_divergence', sa.String(length=20), nullable=True),
        sa.Column('adresse1', sa.String(length=32), nullable=True),
        sa.Column('adresse2', sa.String(length=32), nullable=True),
        sa.Column('adresse3', sa.String(length=32), nullable=True),
        sa.Column('adresse4', sa.String(length=32), nullable=True),
        sa.Column('code_postal', sa.String(length=10), nullable=True),
        sa.Column('ville', sa.String(length=32), nullable=True),
        sa.Column('pays_residence', sa.String(length=32), nullable=True),
        sa.Column('telephone_personnel', sa.String(length=15), nullable=True),
        sa.Column('telephone_chez_employeur', sa.String(length=15), nullable=True),
        sa.Column('nom_employeur', sa.String(length=32), nullable=True),
        sa.Column('telephone_employeur', sa.String(length=15), nullable=True),
        sa.Column('telecopie_employeur', sa.String(length=15), nullable=True),
        sa.Column('adresse1_employeur', sa.String(length=32), nullable=True),
        sa.Column('adresse2_employeur', sa.String(length=32), nullable=True),
        sa.Column('adresse3_employeur', sa.String(length=32), nullable=True),
        sa.Column('adresse4_employeur', sa.String(length=32), nullable=True),
        sa.Column('code_postal_employeur', sa.String(length=10), nullable=True),
        sa.Column('ville_employeur', sa.String(length=32), nullable=True),
        sa.Column('pays_employeur', sa.String(length=32), nullable=True),
        sa.Column('banque_domiciliation', sa.String(length=32), nullable=True),
        sa.Column('libelle_guichet', sa.String(length=30), nullable=True),
        sa.Column('titulaire_compte', sa.String(length=32), nullable=True),
        sa.Column('code_banque', sa.String(length=5), nullable=True),
        sa.Column('code_guichet', sa.String(length=5), nullable=True),
        sa.Column('date_deces', sa.Date(), nullable=True),
        sa.Column('numero_acte_deces', sa.String(length=10), nullable=True),
        sa.Column('code_insee_deces', sa.String(length=5), nullable=True),
        sa.Column('code_postal_deces', sa.String(length=10), nullable=True),
        sa.Column('localite_deces', sa.String(length=32), nullable=True),
        sa.Column('commentaires_revenus', sa.String(length=128), nullable=True),
        sa.Column('montant_salaire', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('periode_versement_salaire', sa.Integer(), nullable=True),
        sa.Column('frequence_versement_salaire', sa.String(length=2), nullable=True),
        sa.Column('nature_revenu1', sa.String(length=30), nullable=True),
        sa.Column('montant_revenu1', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('periode_versement_revenu1', sa.Integer(), nullable=True),
        sa.Column('frequence_versement_revenu1', sa.String(length=2), nullable=True),
        sa.Column('nature_revenu2', sa.String(length=30), nullable=True),
        sa.Column('montant_revenu2', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('periode_versement_revenu2', sa.Integer(), nullable=True),
        sa.Column('frequence_versement_revenu2', sa.String(length=2), nullable=True),
        sa.Column('nature_revenu3', sa.String(length=30), nullable=True),
        sa.Column('montant_revenu3', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('periode_versement_revenu3', sa.Integer(), nullable=True),
        sa.Column('frequence_versement_revenu3', sa.String(length=2), nullable=True),
        sa.Column('numero_facture', sa.String(length=9), nullable=True),
        sa.Column('date_facture', sa.Date(), nullable=True),
        sa.Column('montant_facture', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('tarif_applique', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('cumul_montants_precedents', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('reprise_facturation', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('remise_eventuelle', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('memo1', sa.String(length=64), nullable=True),
        sa.Column('memo2', sa.String(length=64), nullable=True),
        sa.Column('memo3', sa.String(length=64), nullable=True),
        sa.Column('memo4', sa.String(length=64), nullable=True),
        sa.Column('memo5', sa.String(length=1000), nullable=True),
        sa.Column('notes_personnelles', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['donnee_id'], ['donnees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table export_batches
    op.create_table('export_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('filepath', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('enquete_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('utilisateur', sa.String(length=100), nullable=True),
        sa.Column('enquete_ids', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table enquetes_archive_files
    op.create_table('enquetes_archive_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donnee_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['donnee_id'], ['donnees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table tarifs_eos
    op.create_table('tarifs_eos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_demande', sa.String(length=50), nullable=False),
        sa.Column('code_resultat', sa.String(length=10), nullable=True),
        sa.Column('elements_retrouves', sa.String(length=10), nullable=True),
        sa.Column('montant', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer la table enquete_facturation
    op.create_table('enquete_facturation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donnee_enqueteur_id', sa.Integer(), nullable=False),
        sa.Column('montant_eos', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('resultat_enqueteur_montant', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('paye', sa.Boolean(), nullable=True),
        sa.Column('date_paiement', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['donnee_enqueteur_id'], ['donnees_enqueteur.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('enquete_facturation')
    op.drop_table('tarifs_eos')
    op.drop_table('enquetes_archive_files')
    op.drop_table('export_batches')
    op.drop_table('donnees_enqueteur')
    
    op.drop_index('idx_donnee_typeDemande', table_name='donnees')
    op.drop_index('idx_donnee_statut_validation', table_name='donnees')
    op.drop_index('idx_donnee_statut_enqueteur', table_name='donnees')
    op.drop_index('idx_donnee_statut_date', table_name='donnees')
    op.drop_index('idx_donnee_numeroDossier', table_name='donnees')
    op.drop_index('idx_donnee_nom', table_name='donnees')
    op.drop_index('idx_donnee_fichier_id', table_name='donnees')
    op.drop_index('idx_donnee_enqueteurId', table_name='donnees')
    op.drop_index('idx_donnee_date_butoir', table_name='donnees')
    op.drop_index('idx_donnee_created_at', table_name='donnees')
    op.drop_table('donnees')
    
    op.drop_table('enqueteurs')
    op.drop_table('fichiers')





