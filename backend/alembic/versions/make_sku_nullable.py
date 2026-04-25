"""make sku nullable

Revision ID: make_sku_nullable
Revises: add_product_attributes_table
Create Date: 2026-04-25 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_sku_nullable'
down_revision = 'add_product_attributes_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter column sku to be nullable
    op.alter_column('products', 'sku',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)


def downgrade() -> None:
    # Alter column sku back to not nullable
    # Note: this may fail if there are null values
    op.alter_column('products', 'sku',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
