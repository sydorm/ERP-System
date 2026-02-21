"""sync company schema

Revision ID: 009_sync_company_schema
Revises: a1b2c3d4e5f6
Create Date: 2026-02-21 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_sync_company_schema'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create TaxGroup enum
    tax_group_enum = sa.Enum('GROUP_1', 'GROUP_2', 'GROUP_3', 'GENERAL', name='taxgroup')
    tax_group_enum.create(op.get_bind())

    # 2. Add new columns to companies
    op.add_column('companies', sa.Column('full_name_uk', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('short_name_uk', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('full_name_en', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('website', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('edrpou', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('ipn', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('kved', sa.String(length=10), nullable=True))
    op.add_column('companies', sa.Column('director_name', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('director_position', sa.String(length=100), nullable=True))
    op.add_column('companies', sa.Column('accountant_name', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('legal_address', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('physical_address', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('tax_group', sa.Enum('GROUP_1', 'GROUP_2', 'GROUP_3', 'GENERAL', name='taxgroup'), nullable=True))
    op.add_column('companies', sa.Column('vat_payer', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('companies', sa.Column('vat_number', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('tax_rate_single', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('tax_amount_esv', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('military_tax_rate', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('last_tax_update', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False))

    # 3. Migrate existing data
    op.execute("UPDATE companies SET full_name_uk = legal_name, edrpou = tax_id")

    # 4. Create indices
    op.create_index(op.f('ix_companies_edrpou'), 'companies', ['edrpou'], unique=False)
    
    # 5. Drop old columns
    op.drop_column('companies', 'tax_id')
    op.drop_column('companies', 'legal_name')


def downgrade() -> None:
    # 1. Restore old columns
    op.add_column('companies', sa.Column('tax_id', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('legal_name', sa.String(length=500), nullable=True))
    
    # 2. Migrate data back
    op.execute("UPDATE companies SET tax_id = edrpou, legal_name = full_name_uk")
    
    # 3. Make them nullable=False if needed (matching original schema)
    # Note: If there's no data, this might fail, but for downgrade it's usually acceptable
    op.alter_column('companies', 'tax_id', nullable=False)
    op.alter_column('companies', 'legal_name', nullable=False)

    # 4. Remove new stuff
    op.drop_index(op.f('ix_companies_edrpou'), table_name='companies')
    op.drop_column('companies', 'is_default')
    op.drop_column('companies', 'last_tax_update')
    op.drop_column('companies', 'military_tax_rate')
    op.drop_column('companies', 'tax_amount_esv')
    op.drop_column('companies', 'tax_rate_single')
    op.drop_column('companies', 'vat_number')
    op.drop_column('companies', 'vat_payer')
    op.drop_column('companies', 'tax_group')
    op.drop_column('companies', 'email')
    op.drop_column('companies', 'phone')
    op.drop_column('companies', 'physical_address')
    op.drop_column('companies', 'legal_address')
    op.drop_column('companies', 'accountant_name')
    op.drop_column('companies', 'director_position')
    op.drop_column('companies', 'director_name')
    op.drop_column('companies', 'kved')
    op.drop_column('companies', 'edrpou')
    op.add_column('companies', sa.Column('tax_id', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('companies', sa.Column('legal_name', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    # Note: re-adding columns in downgrade is tricky with types, better to just drop table if it's initial
    
    op.drop_column('companies', 'website')
    op.drop_column('companies', 'full_name_en')
    op.drop_column('companies', 'short_name_uk')
    op.drop_column('companies', 'full_name_uk')
    
    sa.Enum(name='taxgroup').drop(op.get_bind())
