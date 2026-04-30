"""Add contact fields to orders

Revision ID: 936262064060
Revises: 038_add_cost_tracking
Create Date: 2026-04-30 15:02:10.021784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '936262064060'
down_revision = '038_add_cost_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('next_contact_channel', sa.String(length=50), nullable=True))
    op.add_column('orders', sa.Column('next_contact_comment', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'next_contact_comment')
    op.drop_column('orders', 'next_contact_channel')
