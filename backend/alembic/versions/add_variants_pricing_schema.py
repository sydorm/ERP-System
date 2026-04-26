"""add variants pricing schema

Revision ID: add_variants_pricing_schema
Revises: add_mfg_product_params
Create Date: 2026-04-25 16:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_variants_pricing_schema'
down_revision = 'add_mfg_product_params'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='attributes' AND column_name='generates_variant'"
    ))
    if not res.first():
        # 1. Add generates_variant to attributes
        op.add_column('attributes', sa.Column('generates_variant', sa.Boolean(), server_default='true', nullable=False))
        
        # 2. Create product_price_rules table
        op.create_table(
            'product_price_rules',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('pricing_mode', sa.String(length=50), nullable=False, server_default='manual'),
            sa.Column('base_price', sa.Numeric(precision=15, scale=2), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
            sa.UniqueConstraint('product_id')
        )
        
        # 3. Create product_price_markups table
        op.create_table(
            'product_price_markups',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('attribute_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('option_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('text_value', sa.String(length=255), nullable=True),
            sa.Column('markup', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['rule_id'], ['product_price_rules.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['option_id'], ['attribute_options.id'], ondelete='CASCADE')
        )

def downgrade() -> None:
    op.drop_table('product_price_markups')
    op.drop_table('product_price_rules')
    op.drop_column('attributes', 'generates_variant')
