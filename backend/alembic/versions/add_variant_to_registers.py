"""add variant_id to accumulation_registers

Revision ID: add_variant_to_registers
Revises: add_variant_to_prod_materials
Create Date: 2026-04-25 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_variant_to_registers'
down_revision = 'add_variant_to_prod_materials'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='accumulation_registers' AND column_name='variant_id'"
    ))
    if not res.first():
        op.add_column('accumulation_registers', sa.Column('variant_id', sa.UUID(), sa.ForeignKey('product_variants.id'), nullable=True))
        op.create_index(op.f('ix_accumulation_registers_variant_id'), 'accumulation_registers', ['variant_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_accumulation_registers_variant_id'), table_name='accumulation_registers')
    op.drop_column('accumulation_registers', 'variant_id')
