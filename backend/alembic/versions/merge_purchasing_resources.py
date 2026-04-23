"""merge purchasing and resources heads

Revision ID: merge_purchasing_resources
Revises: 032_purchasing_module_updates, 51a2b3c4d5e6
Create Date: 2026-04-23 19:53:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_purchasing_resources'
down_revision = ('032_purchasing_module_updates', '51a2b3c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
