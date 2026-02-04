"""add client_id to export_batch

Revision ID: 23e63946daaf
Revises: 008_tarifs_client
Create Date: 2026-01-01 13:09:37.057852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '23e63946daaf'
down_revision = '008_tarifs_client'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Supprimer confirmation_options (peut ne pas exister selon l'état de la base)
    conn.execute(sa.text("DROP TABLE IF EXISTS confirmation_options CASCADE"))

    # Tronquer les données existantes avant de réduire les tailles de colonnes
    truncations_donnees = {
        'nom': 30, 'prenom': 20, 'lieuNaissance': 50, 'codePostalNaissance': 10,
        'paysNaissance': 32, 'nomPatronymique': 30, 'adresse1': 32, 'adresse2': 32,
        'adresse3': 32, 'adresse4': 32, 'ville': 32, 'codePostal': 10,
        'paysResidence': 32, 'telephonePersonnel': 15, 'telephoneEmployeur': 15,
        'nomEmployeur': 32, 'banqueDomiciliation': 32, 'libelleGuichet': 30,
        'titulaireCompte': 32, 'codeBanque': 5, 'codeGuichet': 5,
        'numeroCompte': 11, 'ribCompte': 2, 'elementDemandes': 10,
        'elementObligatoires': 10, 'elementContestes': 10, 'motifDeContestation': 64,
        'commentaire': 1000, 'nom_complet': 100, 'motif': 255,
    }
    for col, length in truncations_donnees.items():
        conn.execute(sa.text(
            f'UPDATE donnees SET "{col}" = LEFT("{col}", {length}) WHERE LENGTH("{col}") > {length}'
        ))

    conn.execute(sa.text(
        "UPDATE donnees_enqueteur SET elements_retrouves = LEFT(elements_retrouves, 10) "
        "WHERE LENGTH(elements_retrouves) > 10"
    ))
    conn.execute(sa.text(
        "UPDATE enquete_facturation SET tarif_eos_code = LEFT(tarif_eos_code, 10) "
        "WHERE LENGTH(tarif_eos_code) > 10"
    ))
    conn.execute(sa.text(
        "UPDATE enquete_facturation SET tarif_enqueteur_code = LEFT(tarif_enqueteur_code, 10) "
        "WHERE LENGTH(tarif_enqueteur_code) > 10"
    ))

    # Supprimer les index avant ALTER (IF EXISTS pour éviter erreur si absents)
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_donnee_datenaissance_maj"))
    conn.execute(sa.text('DROP INDEX IF EXISTS "idx_donnee_dateNaissance_maj"'))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_tarifs_enqueteur_client_id"))

    # Réduire les tailles de colonnes sur donnees
    with op.batch_alter_table('donnees', schema=None) as batch_op:
        batch_op.alter_column('nom',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=30),
               existing_nullable=True)
        batch_op.alter_column('prenom',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=20),
               existing_nullable=True)
        batch_op.alter_column('lieuNaissance',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('codePostalNaissance',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('paysNaissance',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('nomPatronymique',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=30),
               existing_nullable=True)
        batch_op.alter_column('adresse1',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('adresse2',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('adresse3',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('adresse4',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('ville',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('codePostal',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('paysResidence',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('telephonePersonnel',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=15),
               existing_nullable=True)
        batch_op.alter_column('telephoneEmployeur',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=15),
               existing_nullable=True)
        batch_op.alter_column('nomEmployeur',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('banqueDomiciliation',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('libelleGuichet',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=30),
               existing_nullable=True)
        batch_op.alter_column('titulaireCompte',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=32),
               existing_nullable=True)
        batch_op.alter_column('codeBanque',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=5),
               existing_nullable=True)
        batch_op.alter_column('codeGuichet',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=5),
               existing_nullable=True)
        batch_op.alter_column('numeroCompte',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=11),
               existing_nullable=True)
        batch_op.alter_column('ribCompte',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=2),
               existing_nullable=True)
        batch_op.alter_column('elementDemandes',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('elementObligatoires',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('elementContestes',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('motifDeContestation',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('commentaire',
               existing_type=sa.VARCHAR(length=2000),
               type_=sa.String(length=1000),
               existing_nullable=True)
        batch_op.alter_column('nom_complet',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('motif',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.String(length=255),
               existing_nullable=True)

    # Réduire les tailles de colonnes sur donnees_enqueteur
    with op.batch_alter_table('donnees_enqueteur', schema=None) as batch_op:
        batch_op.alter_column('elements_retrouves',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=10),
               existing_nullable=True)

    # Réduire les tailles de colonnes sur enquete_facturation
    with op.batch_alter_table('enquete_facturation', schema=None) as batch_op:
        batch_op.alter_column('tarif_eos_code',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('tarif_enqueteur_code',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=10),
               existing_nullable=True)

    # Créer les index (IF NOT EXISTS pour éviter doublons)
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_donnees_client_id ON donnees (client_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_donnees_enqueteur_client_id ON donnees_enqueteur (client_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_enquete_archive_files_client_id ON enquete_archive_files (client_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_export_batches_client_id ON export_batches (client_id)"))

    # Clé étrangère sur donnees_enqueteur : DROP IF EXISTS puis re-créer si absente
    conn.execute(sa.text("ALTER TABLE donnees_enqueteur DROP CONSTRAINT IF EXISTS donnees_enqueteur_donnee_id_fkey"))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint c
                JOIN pg_class cl ON c.conrelid = cl.oid
                WHERE cl.relname = 'donnees_enqueteur' AND c.contype = 'f'
            ) THEN
                ALTER TABLE donnees_enqueteur ADD FOREIGN KEY (donnee_id) REFERENCES donnees (id);
            END IF;
        END $$;
    """))

    # Contrainte unique sur partner_case_requests
    conn.execute(sa.text("ALTER TABLE partner_case_requests DROP CONSTRAINT IF EXISTS partner_case_requests_donnee_id_request_code_key"))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_partner_case_request') THEN
                ALTER TABLE partner_case_requests ADD CONSTRAINT uq_partner_case_request UNIQUE (donnee_id, request_code);
            END IF;
        END $$;
    """))

    # Contrainte unique sur partner_tarif_rules
    conn.execute(sa.text("ALTER TABLE partner_tarif_rules DROP CONSTRAINT IF EXISTS partner_tarif_rules_client_id_tarif_lettre_request_key_key"))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_partner_tarif_rule') THEN
                ALTER TABLE partner_tarif_rules ADD CONSTRAINT uq_partner_tarif_rule UNIQUE (client_id, tarif_lettre, request_key);
            END IF;
        END $$;
    """))


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tarifs_enqueteur', schema=None) as batch_op:
        batch_op.create_index('ix_tarifs_enqueteur_client_id', ['client_id'], unique=False)

    with op.batch_alter_table('partner_tarif_rules', schema=None) as batch_op:
        batch_op.drop_constraint('uq_partner_tarif_rule', type_='unique')
        batch_op.create_unique_constraint('partner_tarif_rules_client_id_tarif_lettre_request_key_key', ['client_id', 'tarif_lettre', 'request_key'], postgresql_nulls_not_distinct=False)

    with op.batch_alter_table('partner_case_requests', schema=None) as batch_op:
        batch_op.drop_constraint('uq_partner_case_request', type_='unique')
        batch_op.create_unique_constraint('partner_case_requests_donnee_id_request_code_key', ['donnee_id', 'request_code'], postgresql_nulls_not_distinct=False)

    with op.batch_alter_table('export_batches', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_export_batches_client_id'))

    with op.batch_alter_table('enquete_facturation', schema=None) as batch_op:
        batch_op.alter_column('tarif_enqueteur_code',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('tarif_eos_code',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)

    with op.batch_alter_table('enquete_archive_files', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_enquete_archive_files_client_id'))

    with op.batch_alter_table('donnees_enqueteur', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('donnees_enqueteur_donnee_id_fkey', 'donnees', ['donnee_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_index(batch_op.f('ix_donnees_enqueteur_client_id'))
        batch_op.alter_column('elements_retrouves',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)

    with op.batch_alter_table('donnees', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_donnees_client_id'))
        batch_op.create_index('idx_donnee_datenaissance_maj', ['dateNaissance_maj'], unique=False)
        batch_op.alter_column('motif',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=500),
               existing_nullable=True)
        batch_op.alter_column('nom_complet',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('commentaire',
               existing_type=sa.String(length=1000),
               type_=sa.VARCHAR(length=2000),
               existing_nullable=True)
        batch_op.alter_column('motifDeContestation',
               existing_type=sa.String(length=64),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=True)
        batch_op.alter_column('elementContestes',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('elementObligatoires',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('elementDemandes',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('ribCompte',
               existing_type=sa.String(length=2),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('numeroCompte',
               existing_type=sa.String(length=11),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('codeGuichet',
               existing_type=sa.String(length=5),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('codeBanque',
               existing_type=sa.String(length=5),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('titulaireCompte',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('libelleGuichet',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('banqueDomiciliation',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('nomEmployeur',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('telephoneEmployeur',
               existing_type=sa.String(length=15),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('telephonePersonnel',
               existing_type=sa.String(length=15),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('paysResidence',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('codePostal',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('ville',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('adresse4',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('adresse3',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('adresse2',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('adresse1',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('nomPatronymique',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('paysNaissance',
               existing_type=sa.String(length=32),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('codePostalNaissance',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('lieuNaissance',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('prenom',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('nom',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)

    op.create_table('confirmation_options',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('option_text', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('usage_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name='confirmation_options_client_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='confirmation_options_pkey'),
    sa.UniqueConstraint('client_id', 'option_text', name='uq_client_option', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    with op.batch_alter_table('confirmation_options', schema=None) as batch_op:
        batch_op.create_index('ix_confirmation_options_client_id', ['client_id'], unique=False)

    # ### end Alembic commands ###
