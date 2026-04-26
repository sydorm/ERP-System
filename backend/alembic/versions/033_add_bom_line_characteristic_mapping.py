"""add bom line characteristic mapping

Revision ID: 033_add_bom_line_characteristic_mapping
Revises: merge_purchasing_resources
Create Date: 2026-04-26 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '033_add_bom_mapping'
down_revision = 'merge_purchasing_resources'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='bom_line_characteristic_mappings'"))
    if not res.first():
        op.create_table('bom_line_characteristic_mappings',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('bom_line_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('component_characteristic_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('parent_characteristic_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['bom_line_id'], ['specification_items.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['component_characteristic_id'], ['attributes.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['parent_characteristic_id'], ['attributes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_bom_line_characteristic_mappings_bom_line_id'), 'bom_line_characteristic_mappings', ['bom_line_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_bom_line_characteristic_mappings_bom_line_id'), table_name='bom_line_characteristic_mappings')
    op.drop_table('bom_line_characteristic_mappings')
