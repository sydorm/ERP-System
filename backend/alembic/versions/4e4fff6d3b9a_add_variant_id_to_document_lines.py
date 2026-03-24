"""add variant_id to document lines

Revision ID: 4e4fff6d3b9a
Revises: d855d06e7df4
Create Date: 2026-02-21 16:54:40.357755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e4fff6d3b9a'
down_revision = 'd855d06e7df4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Add variant_id to order_lines (safely)
    columns = [c['name'] for c in inspector.get_columns('order_lines')]
    if 'variant_id' not in columns:
        op.add_column('order_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_order_lines_variant_id', 'order_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')

    # Add variant_id to purchase_receipt_lines (safely)
    columns = [c['name'] for c in inspector.get_columns('purchase_receipt_lines')]
    if 'variant_id' not in columns:
        op.add_column('purchase_receipt_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_purchase_receipt_lines_variant_id', 'purchase_receipt_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')

    # Add variant_id to sales_invoice_lines (safely)
    columns = [c['name'] for c in inspector.get_columns('sales_invoice_lines')]
    if 'variant_id' not in columns:
        op.add_column('sales_invoice_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_sales_invoice_lines_variant_id', 'sales_invoice_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    # Drop from sales_invoice_lines
    op.drop_constraint(None, 'sales_invoice_lines', type_='foreignkey')
    op.drop_column('sales_invoice_lines', 'variant_id')

    # Drop from purchase_receipt_lines
    op.drop_constraint(None, 'purchase_receipt_lines', type_='foreignkey')
    op.drop_column('purchase_receipt_lines', 'variant_id')

    # Drop from order_lines
    op.drop_constraint(None, 'order_lines', type_='foreignkey')
    op.drop_column('order_lines', 'variant_id')
