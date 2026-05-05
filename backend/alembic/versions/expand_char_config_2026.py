"""expand product_attribute settings

Revision ID: expand_char_config_2026
Revises: auto_merge_1777669576
Create Date: 2026-05-05 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'expand_char_config_2026'
down_revision = 'auto_merge_1777669576'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add to global attributes (Dictionary definition)
    op.add_column('attributes', sa.Column('show_in_purchase_receipt', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('attributes', sa.Column('show_in_purchase_order', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('attributes', sa.Column('show_in_sales_order', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('attributes', sa.Column('required', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('attributes', sa.Column('track_stock_separately', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('attributes', sa.Column('block_if_empty', sa.Boolean(), server_default='false', nullable=False))
    # op.add_column('attributes', sa.Column('affects_sku', sa.Boolean(), server_default='true', nullable=False)) # generates_variant exists

    # Add to product_attributes (Per-product link/override)
    op.add_column('product_attributes', sa.Column('show_in_purchase_receipt', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('product_attributes', sa.Column('show_in_purchase_order', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('product_attributes', sa.Column('show_in_sales_order', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('product_attributes', sa.Column('required', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('product_attributes', sa.Column('track_stock_separately', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('product_attributes', sa.Column('block_if_empty', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('product_attributes', sa.Column('affects_sku', sa.Boolean(), server_default='true', nullable=False))

def downgrade() -> None:
    # Remove from product_attributes
    op.drop_column('product_attributes', 'affects_sku')
    op.drop_column('product_attributes', 'block_if_empty')
    op.drop_column('product_attributes', 'track_stock_separately')
    op.drop_column('product_attributes', 'required')
    op.drop_column('product_attributes', 'show_in_sales_order')
    op.drop_column('product_attributes', 'show_in_purchase_order')
    op.drop_column('product_attributes', 'show_in_purchase_receipt')

    # Remove from attributes
    op.drop_column('attributes', 'block_if_empty')
    op.drop_column('attributes', 'track_stock_separately')
    op.drop_column('attributes', 'required')
    op.drop_column('attributes', 'show_in_sales_order')
    op.drop_column('attributes', 'show_in_purchase_order')
    op.drop_column('attributes', 'show_in_purchase_receipt')
