"""add specification_id to order_lines

Revision ID: 020_add_orderline_spec
Revises: 019_add_calc_dim_config
Create Date: 2026-03-29 01:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '020_add_orderline_spec'
down_revision = '019_add_calc_dim_config'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add specification_id to order_lines
    op.add_column('order_lines', sa.Column('specification_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_order_lines_specification_id',
        'order_lines', 'product_specifications',
        ['specification_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade() -> None:
    op.drop_constraint('fk_order_lines_specification_id', 'order_lines', type_='foreignkey')
    op.drop_column('order_lines', 'specification_id')
