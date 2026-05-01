"""auto_merge

Revision ID: auto_merge_1777470141
Revises: 037_add_business_process_tables, auto_merge_1777415885
Create Date: 2026-04-29 13:42:21.866673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777470141'
down_revision = ('037_add_business_process_tables', 'auto_merge_1777415885')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
