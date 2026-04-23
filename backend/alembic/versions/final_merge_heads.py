"""final merge of all migration heads

Revision ID: final_merge_heads
Revises: merge_purchasing_resources, auto_merge_1776959694
Create Date: 2026-04-23 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'final_merge_heads'
down_revision = ('merge_purchasing_resources', 'auto_merge_1776959694')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
