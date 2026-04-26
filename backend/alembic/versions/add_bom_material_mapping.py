"""add conditional material mapping

Revision ID: add_bom_material_mapping
Revises: add_detail_bom_line_type
Create Date: 2026-04-25 20:18:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_bom_material_mapping'
down_revision = 'add_detail_bom_line_type'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='specification_items' AND column_name='mapping_attr'"
    ))
    if not res.first():
        op.add_column('specification_items', sa.Column('mapping_attr', sa.String(length=100), nullable=True))
        op.add_column('specification_items', sa.Column('material_mapping', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('specification_items', 'material_mapping')
    op.drop_column('specification_items', 'mapping_attr')
