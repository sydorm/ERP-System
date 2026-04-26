"""auto_merge

Revision ID: auto_merge_1777152308
Revises: add_dim_format_to_attr, add_width_height_attr_opts
Create Date: 2026-04-25 21:25:09.100487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auto_merge_1777152308'
down_revision = ('add_dim_format_to_attr', 'add_width_height_attr_opts')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
