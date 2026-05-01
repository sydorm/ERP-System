"""auto_merge

Revision ID: auto_merge_1777551077
Revises: auto_merge_1777550676, eaedb2bb097c
Create Date: 2026-04-30 12:11:17.768282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777551077'
down_revision = ('auto_merge_1777550676', 'eaedb2bb097c')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
