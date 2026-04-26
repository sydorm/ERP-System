"""purchasing module updates

Revision ID: 032_purchasing_module_updates
Revises: 031_make_employee_id_nullable
Create Date: 2026-04-23 16:16:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '032_purchasing_module_updates'
down_revision = '031_make_employee_id_nullable'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update Products
    conn = op.get_bind()
    
    # helper for multiple checks
    def col_exists(table, column):
        res = conn.execute(sa.text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='{column}'"))
        return res.first() is not None

    if not col_exists('products', 'min_stock'):
        op.add_column('products', sa.Column('min_stock', sa.Numeric(precision=15, scale=3), nullable=True, server_default='0.0'))
    if not col_exists('products', 'optimal_stock'):
        op.add_column('products', sa.Column('optimal_stock', sa.Numeric(precision=15, scale=3), nullable=True, server_default='0.0'))
    if not col_exists('products', 'default_supplier_id'):
        op.add_column('products', sa.Column('default_supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('counterparties.id', ondelete='SET NULL'), nullable=True))
    if not col_exists('products', 'delivery_days'):
        op.add_column('products', sa.Column('delivery_days', sa.Integer(), nullable=True, server_default='0'))

    # 2. Update Counterparties
    if not col_exists('counterparties', 'delivery_days'):
        op.add_column('counterparties', sa.Column('delivery_days', sa.Integer(), nullable=True, server_default='0'))
    if not col_exists('counterparties', 'payment_terms'):
        op.add_column('counterparties', sa.Column('payment_terms', sa.String(length=255), nullable=True))

    # 3. Update Purchase Receipts
    if not col_exists('purchase_receipts', 'base_order_id'):
        op.add_column('purchase_receipts', sa.Column('base_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchase_orders.id', ondelete='SET NULL'), nullable=True))

    # 4. Create Supplier Prices table
    # Check if table exists
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='supplier_prices'"))
    if not res.first():
        op.create_table('supplier_prices',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.0'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['supplier_id'], ['counterparties.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_supplier_prices_product_id'), 'supplier_prices', ['product_id'], unique=False)
        op.create_index(op.f('ix_supplier_prices_supplier_id'), 'supplier_prices', ['supplier_id'], unique=False)
        op.create_index(op.f('ix_supplier_prices_company_id'), 'supplier_prices', ['company_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_supplier_prices_company_id'), table_name='supplier_prices')
    op.drop_index(op.f('ix_supplier_prices_supplier_id'), table_name='supplier_prices')
    op.drop_index(op.f('ix_supplier_prices_product_id'), table_name='supplier_prices')
    op.drop_table('supplier_prices')
    op.drop_column('purchase_receipts', 'base_order_id')
    op.drop_column('counterparties', 'payment_terms')
    op.drop_column('counterparties', 'delivery_days')
    op.drop_column('products', 'delivery_days')
    op.drop_column('products', 'default_supplier_id')
    op.drop_column('products', 'optimal_stock')
    op.drop_column('products', 'min_stock')
