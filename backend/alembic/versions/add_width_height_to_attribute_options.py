"""add width and height to attribute_options

Revision ID: add_width_height_to_attribute_options
Revises: add_attribute_values_to_lines
Create Date: 2026-04-26 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_width_height_to_attribute_options'
down_revision = 'add_attribute_values_to_lines'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='attribute_options' AND column_name='width'"
    ))
    if not res.first():
        op.add_column('attribute_options', sa.Column('width', sa.Integer(), nullable=True))
        op.add_column('attribute_options', sa.Column('height', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('attribute_options', 'height')
    op.drop_column('attribute_options', 'width')
