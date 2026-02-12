"""Add role to users

Revision ID: 002_add_role
Revises: 001_initial
Create Date: 2026-02-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_role'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='worker'))


def downgrade() -> None:
    # Remove role column from users table
    op.drop_column('users', 'role')
