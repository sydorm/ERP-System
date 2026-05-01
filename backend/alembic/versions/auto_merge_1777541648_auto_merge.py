"""auto_merge

Revision ID: auto_merge_1777541648
Revises: 038_add_cost_tracking, auto_merge_1777470141
Create Date: 2026-04-30 09:34:09.205918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777541648'
down_revision = ('038_add_cost_tracking', 'auto_merge_1777470141')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
