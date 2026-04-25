"""add variant_id to production_order_materials

Revision ID: add_variant_to_prod_materials
Revises: add_bom_material_mapping
Create Date: 2026-04-25 20:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_variant_to_prod_materials'
down_revision = 'add_bom_material_mapping'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('production_order_materials', sa.Column('variant_id', sa.UUID(), sa.ForeignKey('product_variants.id', ondelete='SET NULL'), nullable=True))

def downgrade():
    op.drop_column('production_order_materials', 'variant_id')
