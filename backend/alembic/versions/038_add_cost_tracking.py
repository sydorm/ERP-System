"""Add cost tracking: product_cost_history table, cost_method on companies, cost_source on products

Revision ID: 038_add_cost_tracking
Revises: 037_add_business_process_tables
Create Date: 2026-04-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '038_add_cost_tracking'
down_revision = '037_add_business_process_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    existing_cols = {c['name'] for c in inspector.get_columns('products')}
    company_cols = {c['name'] for c in inspector.get_columns('companies')}

    # 1. Add cost_source to products
    if 'cost_source' not in existing_cols:
        op.add_column('products', sa.Column('cost_source', sa.String(200), nullable=True))

    # 2. Add cost_method to companies
    if 'cost_method' not in company_cols:
        op.add_column('companies', sa.Column(
            'cost_method', sa.String(30), nullable=False, server_default='last_price'
        ))

    # 3. Create product_cost_history table
    if 'product_cost_history' not in existing_tables:
        op.create_table(
            'product_cost_history',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('product_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
            sa.Column('variant_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('product_variants.id', ondelete='SET NULL'), nullable=True),
            sa.Column('document_type', sa.String(50), nullable=False),
            sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('document_number', sa.String(100), nullable=False),
            sa.Column('supplier_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('counterparties.id', ondelete='SET NULL'), nullable=True),
            sa.Column('old_stock', sa.Numeric(15, 4), nullable=False, server_default='0'),
            sa.Column('old_cost', sa.Numeric(15, 2), nullable=True),
            sa.Column('incoming_qty', sa.Numeric(15, 4), nullable=False),
            sa.Column('incoming_price', sa.Numeric(15, 2), nullable=False),
            sa.Column('new_cost', sa.Numeric(15, 2), nullable=False),
            sa.Column('method', sa.String(30), nullable=False),
            sa.Column('changed_by', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('company_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_product_cost_history_product_id', 'product_cost_history', ['product_id'])
        op.create_index('ix_product_cost_history_document_id', 'product_cost_history', ['document_id'])
        op.create_index('ix_product_cost_history_company_id', 'product_cost_history', ['company_id'])


def downgrade() -> None:
    op.drop_table('product_cost_history')
    op.drop_column('companies', 'cost_method')
    op.drop_column('products', 'cost_source')
