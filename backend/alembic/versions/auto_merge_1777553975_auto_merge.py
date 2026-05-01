"""auto_merge

Revision ID: auto_merge_1777553975
Revises: 1a2b3c4d5e6f, auto_merge_1777551077
Create Date: 2026-04-30 12:59:36.211587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777553975'
down_revision = ('1a2b3c4d5e6f', 'auto_merge_1777551077')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
