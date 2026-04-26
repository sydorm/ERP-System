"""add dimension_format to attributes

Revision ID: add_dimension_format_to_attributes
Revises: add_attribute_values_to_lines
Create Date: 2026-04-25 23:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_dimension_format_to_attributes'
down_revision = 'add_attribute_values_to_lines'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='attributes' AND column_name='dimension_format'"
    ))
    if not res.first():
        op.add_column('attributes', sa.Column('dimension_format', sa.String(length=50), nullable=True, server_default='{width}×{height}'))

def downgrade():
    op.drop_column('attributes', 'dimension_format')
