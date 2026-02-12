"""add attributes and variants

Revision ID: 005_add_attributes_and_variants
Revises: 004_add_dictionaries
Create Date: 2026-02-13 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_attributes_and_variants'
down_revision = '004_add_dictionaries'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Attributes Table
    op.create_table(
        'attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('TEXT', 'SELECT', 'NUMBER', 'COLOR', 'BOOLEAN', name='attributetype'), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_archived', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Attribute Options Table
    op.create_table(
        'attribute_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('color_code', sa.String(length=20), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=True),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Category Attributes (Link) Table
    op.create_table(
        'category_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('category_code', sa.String(length=255), nullable=False),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_required', sa.Boolean(), server_default='false', nullable=True),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_attributes_category_code'), 'category_attributes', ['category_code'], unique=False)

    # 4. Product Variants Table
    op.create_table(
        'product_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('price_override', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('cost_override', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_variants_sku'), 'product_variants', ['sku'], unique=False)

    # 5. Variant Values (Link) Table
    op.create_table(
        'variant_values',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('option_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('text_value', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['option_id'], ['attribute_options.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('variant_values')
    op.drop_index(op.f('ix_product_variants_sku'), table_name='product_variants')
    op.drop_table('product_variants')
    op.drop_index(op.f('ix_category_attributes_category_code'), table_name='category_attributes')
    op.drop_table('category_attributes')
    op.drop_table('attribute_options')
    op.drop_table('attributes')
    # Use execute to drop type if needed, but Enum name is shared often
    sa.Enum(name='attributetype').drop(op.get_bind())
