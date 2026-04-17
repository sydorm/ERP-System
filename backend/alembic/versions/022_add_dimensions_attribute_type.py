"""Add DIMENSIONS value to attributetype enum

Revision ID: 022_add_dimensions_attribute_type
Revises: 021_add_production_tables
Create Date: 2026-04-17 14:45:00.000000

"""
from alembic import op

revision = '022_add_dimensions_attribute_type'
down_revision = '021_add_production_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE attributetype ADD VALUE IF NOT EXISTS 'DIMENSIONS'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type
    pass
