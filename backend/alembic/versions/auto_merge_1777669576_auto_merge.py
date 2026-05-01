"""auto_merge

Revision ID: auto_merge_1777669576
Revises: 039_add_fabric_cutting_enum, auto_merge_1777553975
Create Date: 2026-05-01 21:06:16.451602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777669576'
down_revision = ('039_add_fabric_cutting_enum', 'auto_merge_1777553975')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
