"""add variant physical params

Revision ID: add_variant_physical_params
Revises: make_sku_nullable
Create Date: 2026-04-25 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_variant_physical_params'
down_revision = 'make_sku_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to product_variants
    op.add_column('product_variants', sa.Column('length_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('product_variants', sa.Column('width_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('product_variants', sa.Column('height_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('product_variants', sa.Column('weight_kg', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Add column to products
    op.add_column('products', sa.Column('variant_config', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove column from products
    op.drop_column('products', 'variant_config')
    
    # Remove columns from product_variants
    op.drop_column('product_variants', 'weight_kg')
    op.drop_column('product_variants', 'height_cm')
    op.drop_column('product_variants', 'width_cm')
    op.drop_column('product_variants', 'length_cm')
