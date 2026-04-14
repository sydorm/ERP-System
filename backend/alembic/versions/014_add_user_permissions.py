"""add user permissions

Revision ID: e7f8g9h0i1j2
Revises: 4e4fff6d3b9a
Create Date: 2026-03-17 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f8g9h0i1j2'
down_revision = 'b23c45d6e7f8'
branch_labels = None
depends_on = None


def upgrade():
    # Add permissions column to users table
    op.add_column('users', sa.Column('permissions', sa.JSON(), nullable=False, server_default='{}'))


def downgrade():
    # Remove permissions column from users table
    op.drop_column('users', 'permissions')
