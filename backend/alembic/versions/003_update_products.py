"""update products

Revision ID: 003_update_products
Revises: 002_add_role
Create Date: 2026-02-12 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_update_products'
down_revision = '002_add_role'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Rename 'code' to 'sku'
    op.alter_column('products', 'code', new_column_name='sku')
    
    # 2. Add new columns
    op.add_column('products', sa.Column('image_url', sa.String(length=500), nullable=True))
    op.add_column('products', sa.Column('currency', sa.String(length=3), nullable=False, server_default='UAH'))
    
    # 3. Create indexes if needed (renaming column might preserve index, but let's be safe)
    # op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)
    # Note: 'code' was indexed, renaming it usually keeps the index but might rename it.
    # Postgres usually handles this, but let's verify if we need to explicitly rename index.
    
    # 4. Remove default value for currency after adding it (optional, but clean)
    op.alter_column('products', 'currency', server_default=None)


def downgrade():
    # 1. Remove new columns
    op.drop_column('products', 'currency')
    op.drop_column('products', 'image_url')
    
    # 2. Rename 'sku' back to 'code'
    op.alter_column('products', 'sku', new_column_name='code')
