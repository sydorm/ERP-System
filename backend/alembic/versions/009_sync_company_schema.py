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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 1. Create TaxGroup enum (safely)
    has_enum = bind.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'taxgroup'")).first()
    if not has_enum:
        sa.Enum('GROUP_1', 'GROUP_2', 'GROUP_3', 'GENERAL', name='taxgroup').create(bind)

    # 2. Add new columns to companies (safely)
    existing_columns = [c['name'] for c in inspector.get_columns('companies')]
    new_columns = [
        ('full_name_uk', sa.String(length=500)),
        ('short_name_uk', sa.String(length=255)),
        ('full_name_en', sa.String(length=500)),
        ('website', sa.String(length=255)),
        ('edrpou', sa.String(length=20)),
        ('ipn', sa.String(length=20)),
        ('kved', sa.String(length=10)),
        ('director_name', sa.String(length=255)),
        ('director_position', sa.String(length=100)),
        ('accountant_name', sa.String(length=255)),
        ('legal_address', sa.String(length=500)),
        ('physical_address', sa.String(length=500)),
        ('phone', sa.String(length=50)),
        ('email', sa.String(length=255)),
        ('tax_group', sa.Enum('GROUP_1', 'GROUP_2', 'GROUP_3', 'GENERAL', name='taxgroup')),
        ('vat_payer', sa.Boolean(), sa.sql.expression.false()),
        ('vat_number', sa.String(length=50)),
        ('tax_rate_single', sa.String(length=20)),
        ('tax_amount_esv', sa.String(length=20)),
        ('military_tax_rate', sa.String(length=20)),
        ('last_tax_update', sa.String(length=50)),
        ('is_default', sa.Boolean(), sa.sql.expression.false()),
    ]
    
    for col_name, col_type, *extra in new_columns:
        if col_name not in existing_columns:
            server_default = extra[0] if extra else None
            is_nullable = False if col_name in ['vat_payer', 'is_default'] else True
            op.add_column('companies', sa.Column(col_name, col_type, server_default=server_default, nullable=is_nullable))

    # 3. Migrate existing data (safely)
    # Check if old columns still exist before trying to migrate
    if 'legal_name' in existing_columns and 'tax_id' in existing_columns:
        op.execute("UPDATE companies SET full_name_uk = legal_name, edrpou = tax_id WHERE full_name_uk IS NULL OR edrpou IS NULL")

    # 4. Create indices (safely)
    existing_indices = [idx['name'] for idx in inspector.get_indexes('companies')]
    if 'ix_companies_edrpou' not in existing_indices:
        op.create_index(op.f('ix_companies_edrpou'), 'companies', ['edrpou'], unique=False)
    
    # 5. Drop old columns (safely)
    for col_name in ['tax_id', 'legal_name']:
        if col_name in existing_columns:
            op.drop_column('companies', col_name)


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
