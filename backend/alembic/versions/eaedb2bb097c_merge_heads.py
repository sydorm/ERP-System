"""Merge heads

Revision ID: eaedb2bb097c
Revises: 034_add_priority_dictionary, 936262064060
Create Date: 2026-04-30 15:03:57.412478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaedb2bb097c'
down_revision = ('034_add_priority_dictionary', '936262064060')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
