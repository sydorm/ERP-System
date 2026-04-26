"""expand crm tables

Revision ID: expand_crm_tables
Revises: 481760018638
Create Date: 2026-04-24 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'expand_crm_tables'
down_revision = '481760018638'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    # 1. Update counterparties table
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='counterparties' AND column_name='payment_terms_id'"
    ))
    if not res.first():
        op.add_column('counterparties', sa.Column('payment_terms_id', sa.UUID(), sa.ForeignKey('dictionary_items.id', ondelete='SET NULL'), nullable=True))

    # 2. Create bank accounts table
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='counterparty_bank_accounts'"))
    if not res.first():
        op.create_table(
            'counterparty_bank_accounts',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('counterparty_id', sa.UUID(), sa.ForeignKey('counterparties.id', ondelete='CASCADE'), nullable=False),
            sa.Column('bank_name', sa.String(length=255), nullable=True),
            sa.Column('iban', sa.String(length=50), nullable=False),
            sa.Column('currency', sa.String(length=10), server_default='UAH', nullable=True),
            sa.Column('purpose', sa.String(length=500), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_counterparty_bank_accounts_counterparty_id'), 'counterparty_bank_accounts', ['counterparty_id'], unique=False)

    # 3. Create contacts table
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='counterparty_contacts'"))
    if not res.first():
        op.create_table(
            'counterparty_contacts',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('counterparty_id', sa.UUID(), sa.ForeignKey('counterparties.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('position', sa.String(length=255), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('telegram', sa.String(length=100), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_counterparty_contacts_counterparty_id'), 'counterparty_contacts', ['counterparty_id'], unique=False)

    # 4. Create materials table
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='counterparty_materials'"))
    if not res.first():
        op.create_table(
            'counterparty_materials',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('counterparty_id', sa.UUID(), sa.ForeignKey('counterparties.id', ondelete='CASCADE'), nullable=False),
            sa.Column('product_id', sa.UUID(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
            sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=10), server_default='UAH', nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_counterparty_materials_counterparty_id'), 'counterparty_materials', ['counterparty_id'], unique=False)

    # 5. Create documents table
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='counterparty_documents'"))
    if not res.first():
        op.create_table(
            'counterparty_documents',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('counterparty_id', sa.UUID(), sa.ForeignKey('counterparties.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('file_url', sa.String(length=1000), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_counterparty_documents_counterparty_id'), 'counterparty_documents', ['counterparty_id'], unique=False)


def downgrade() -> None:
    op.drop_table('counterparty_documents')
    op.drop_table('counterparty_materials')
    op.drop_table('counterparty_contacts')
    op.drop_table('counterparty_bank_accounts')
    op.drop_column('counterparties', 'payment_terms_id')
