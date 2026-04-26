"""auto_merge

Revision ID: auto_merge_1777213904
Revises: 033_add_bom_mapping, auto_merge_1777152308
Create Date: 2026-04-26 14:31:44.986496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777213904'
down_revision = ('033_add_bom_mapping', 'auto_merge_1777152308')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
