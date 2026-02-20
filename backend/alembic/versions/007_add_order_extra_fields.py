"""Add order shipping, contract, comment, discount fields

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa

revision = '007_add_order_extra_fields'
down_revision = '006_complete_erp_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('orders', sa.Column('shipping_date', sa.Date(), nullable=True))
    op.add_column('orders', sa.Column('contract', sa.String(255), nullable=True))
    op.add_column('orders', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True, server_default='0'))


def downgrade():
    op.drop_column('orders', 'discount_percent')
    op.drop_column('orders', 'comment')
    op.drop_column('orders', 'contract')
    op.drop_column('orders', 'shipping_date')
