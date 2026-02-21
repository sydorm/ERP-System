"""Add default_contract to counterparty

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa

revision = '008_add_counterparty_contract'
down_revision = '007_add_order_extra_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('counterparties', sa.Column('default_contract', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('counterparties', 'default_contract')
