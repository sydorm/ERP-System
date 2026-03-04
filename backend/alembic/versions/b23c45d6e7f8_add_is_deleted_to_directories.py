"""add is_deleted to directories

Revision ID: b23c45d6e7f8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-04 23:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23c45d6e7f8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_deleted column to products, counterparties, and warehouses
    op.add_column('products', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('counterparties', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('warehouses', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Remove is_deleted column
    op.drop_column('warehouses', 'is_deleted')
    op.drop_column('counterparties', 'is_deleted')
    op.drop_column('products', 'is_deleted')
