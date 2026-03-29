"""add production tables

Revision ID: 021_add_production_tables
Revises: 020_add_orderline_specification_id
Create Date: 2026-03-29 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '021_add_production_tables'
down_revision = '020_add_orderline_specification_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. create production_orders
    op.create_table('production_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('order_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('base_order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['base_order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_orders_id'), 'production_orders', ['id'], unique=False)
    op.create_index(op.f('ix_production_orders_order_number'), 'production_orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_production_orders_status'), 'production_orders', ['status'], unique=False)

    # 2. create production_order_lines
    op.create_table('production_order_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('specification_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('produced_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['specification_id'], ['product_specifications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_order_lines_id'), 'production_order_lines', ['id'], unique=False)

    # 3. create production_order_materials
    op.create_table('production_order_materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('component_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('required_quantity', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('issued_quantity', sa.Numeric(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=True),
        sa.Column('cost_estimate', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_order_materials_id'), 'production_order_materials', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_production_order_materials_id'), table_name='production_order_materials')
    op.drop_table('production_order_materials')
    
    op.drop_index(op.f('ix_production_order_lines_id'), table_name='production_order_lines')
    op.drop_table('production_order_lines')
    
    op.drop_index(op.f('ix_production_orders_status'), table_name='production_orders')
    op.drop_index(op.f('ix_production_orders_order_number'), table_name='production_orders')
    op.drop_index(op.f('ix_production_orders_id'), table_name='production_orders')
    op.drop_table('production_orders')
