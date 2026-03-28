"""add calc_dim_config to specification_items

Revision ID: 019_add_calc_dim_config
Revises: 018
Create Date: 2026-03-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '019_add_calc_dim_config'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add calc_dim_config column if not already present
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [c['name'] for c in inspector.get_columns('specification_items')]

    if 'calc_dim_config' not in existing_columns:
        op.add_column(
            'specification_items',
            sa.Column('calc_dim_config', postgresql.JSON(), nullable=True)
        )


def downgrade():
    op.drop_column('specification_items', 'calc_dim_config')
