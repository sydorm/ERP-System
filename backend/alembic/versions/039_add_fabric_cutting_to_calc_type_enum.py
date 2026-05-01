"""Add fabric_cutting and characteristic_mapping to calculationtype enum

Revision ID: 039_add_fabric_cutting_enum
Revises: 1a2b3c4d5e6f
Create Date: 2026-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '039_add_fabric_cutting_enum'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block in PostgreSQL
    op.execute("COMMIT")
    op.execute("ALTER TYPE calculationtype ADD VALUE IF NOT EXISTS 'fabric_cutting'")
    op.execute("ALTER TYPE calculationtype ADD VALUE IF NOT EXISTS 'characteristic_mapping'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type without recreating it.
    pass
