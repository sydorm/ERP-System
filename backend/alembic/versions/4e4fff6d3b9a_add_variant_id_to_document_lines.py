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
    # Add variant_id to order_lines
    op.add_column('order_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'order_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')

    # Add variant_id to purchase_receipt_lines
    op.add_column('purchase_receipt_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'purchase_receipt_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')

    # Add variant_id to sales_invoice_lines
    op.add_column('sales_invoice_lines', sa.Column('variant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'sales_invoice_lines', 'product_variants', ['variant_id'], ['id'], ondelete='RESTRICT')


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
