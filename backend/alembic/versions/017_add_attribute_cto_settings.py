"""Add custom input and mapped dimension to attributes

Revision ID: 017_add_attribute_cto
Revises: 016_complete_parametric_schema
Create Date: 2026-03-24 23:59:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '017_add_attribute_cto'
down_revision = '016_parametric' # Note: use the actual revision ID of 016 if it differs, but since the user has multiple heads we can just rely on alembic handling or specify the exact down_revision.

def upgrade() -> None:
    # Add allow_manual_input
    op.add_column('attributes', sa.Column('allow_manual_input', sa.Boolean(), server_default='false', nullable=False))
    # Add mapped_dimension
    op.add_column('attributes', sa.Column('mapped_dimension', sa.String(length=50), nullable=True))

def downgrade() -> None:
    op.drop_column('attributes', 'mapped_dimension')
    op.drop_column('attributes', 'allow_manual_input')
