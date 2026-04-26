"""add attribute_values to document lines

Revision ID: add_attribute_values_to_lines
Revises: add_variant_to_registers
Create Date: 2026-04-25 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_attribute_values_to_lines'
down_revision = 'add_variant_to_registers'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='order_lines' AND column_name='attribute_values'"
    ))
    if not res.first():
        # Add attribute_values to order_lines
        op.add_column('order_lines', sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        # Add attribute_values to purchase_order_lines
        op.add_column('purchase_order_lines', sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        # Add attribute_values to purchase_receipt_lines
        op.add_column('purchase_receipt_lines', sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        # Add attribute_values to sales_invoice_lines
        op.add_column('sales_invoice_lines', sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        # Add attribute_values to accumulation_registers
        op.add_column('accumulation_registers', sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

def downgrade():
    op.drop_column('accumulation_registers', 'attribute_values')
    op.drop_column('sales_invoice_lines', 'attribute_values')
    op.drop_column('purchase_receipt_lines', 'attribute_values')
    op.drop_column('purchase_order_lines', 'attribute_values')
    op.drop_column('order_lines', 'attribute_values')
