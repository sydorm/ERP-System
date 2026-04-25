"""add product_attributes table

Revision ID: add_product_attributes_table
Revises: add_variants_pricing_schema
Create Date: 2026-04-25 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_product_attributes_table'
down_revision = 'add_variants_pricing_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create product_attributes table
    op.create_table(
        'product_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('generates_sku', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_attributes_id'), 'product_attributes', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_product_attributes_id'), table_name='product_attributes')
    op.drop_table('product_attributes')
