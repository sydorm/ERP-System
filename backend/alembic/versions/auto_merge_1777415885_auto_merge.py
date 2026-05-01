"""auto_merge

Revision ID: auto_merge_1777415885
Revises: 034_add_priority_dictionary, 035_add_user_fields
Create Date: 2026-04-28 22:38:05.331827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777415885'
down_revision = ('034_add_priority_dictionary', '035_add_user_fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
