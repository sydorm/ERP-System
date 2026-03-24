"""add purchase orders

Revision ID: a1b2c3d4e5f6
Revises: 4e4fff6d3b9a
Create Date: 2026-02-21 16:54:40.357755

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '4e4fff6d3b9a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Enum (safely)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    has_enum = bind.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'purchaseorderstatus'")).first()
    if not has_enum:
        sa.Enum('draft', 'confirmed', 'done', 'cancelled', name='purchaseorderstatus').create(bind)

    # 2. Create purchase_orders (safely)
    res = bind.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name = 'purchase_orders'")).first()
    if not res:
        op.create_table(
            'purchase_orders',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('order_number', sa.String(length=50), nullable=False),
            sa.Column('order_date', sa.DateTime(), nullable=False),
            sa.Column('expected_date', sa.DateTime(), nullable=True),
            sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('status', postgresql.ENUM('draft', 'confirmed', 'done', 'cancelled', name='purchaseorderstatus', create_type=False), nullable=False),
            sa.Column('currency', sa.String(length=3), nullable=False),
            sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
            sa.ForeignKeyConstraint(['supplier_id'], ['counterparties.id'], ),
            sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_purchase_orders_company_id'), 'purchase_orders', ['company_id'], unique=False)
        op.create_index(op.f('ix_purchase_orders_id'), 'purchase_orders', ['id'], unique=False)
        op.create_index(op.f('ix_purchase_orders_order_number'), 'purchase_orders', ['order_number'], unique=False)
    else:
        print("Table 'purchase_orders' already exists, skipping creation.")

    # 3. Create purchase_order_lines (safely)
    res_lines = bind.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name = 'purchase_order_lines'")).first()
    if not res_lines:
        op.create_table(
            'purchase_order_lines',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
            sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
            sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_purchase_order_lines_id'), 'purchase_order_lines', ['id'], unique=False)
        op.create_index(op.f('ix_purchase_order_lines_order_id'), 'purchase_order_lines', ['order_id'], unique=False)
    else:
        print("Table 'purchase_order_lines' already exists, skipping creation.")


def downgrade() -> None:
    op.drop_index(op.f('ix_purchase_order_lines_order_id'), table_name='purchase_order_lines')
    op.drop_index(op.f('ix_purchase_order_lines_id'), table_name='purchase_order_lines')
    op.drop_table('purchase_order_lines')
    
    op.drop_index(op.f('ix_purchase_orders_order_number'), table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_id'), table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_company_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    
    sa.Enum(name='purchaseorderstatus').drop(op.get_bind())
