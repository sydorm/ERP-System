"""add specification calculation rules

Revision ID: f8g9h0i1j2k3
Revises: e7f8g9h0i1j2
Create Date: 2026-03-22 00:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8g9h0i1j2k3'
down_revision = 'e7f8g9h0i1j2'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create Enum
    sa.Enum('height_cm', 'width_cm', 'length_cm', 'custom', name='calculationdimension').create(op.get_bind())

    # 2. Create specification_calculation_rules
    op.create_table(
        'specification_calculation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('specification_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dimension', sa.Enum('height_cm', 'width_cm', 'length_cm', 'custom', name='calculationdimension', create_type=False), nullable=False),
        sa.Column('data_points', postgresql.JSON(), nullable=False),
        sa.Column('formula', sa.String(length=500), nullable=True),
        sa.Column('waste_factor', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['specification_item_id'], ['specification_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('specification_item_id')
    )
    op.create_index(op.f('ix_specification_calculation_rules_id'), 'specification_calculation_rules', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_specification_calculation_rules_id'), table_name='specification_calculation_rules')
    op.drop_table('specification_calculation_rules')
    sa.Enum(name='calculationdimension').drop(op.get_bind())
