"""add detail bom line type

Revision ID: add_detail_bom_line_type
Revises: add_variant_physical_params
Create Date: 2026-04-25 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_detail_bom_line_type'
down_revision = 'add_variant_physical_params'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('specification_items', sa.Column('line_type', sa.String(length=20), server_default='material', nullable=False))
    op.add_column('specification_items', sa.Column('size_from_attr', sa.String(length=100), nullable=True))
    op.add_column('specification_items', sa.Column('size_multiplier', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('specification_items', sa.Column('fixed_length', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('specification_items', sa.Column('fixed_width', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column('specification_items', 'fixed_width')
    op.drop_column('specification_items', 'fixed_length')
    op.drop_column('specification_items', 'size_multiplier')
    op.drop_column('specification_items', 'size_from_attr')
    op.drop_column('specification_items', 'line_type')
