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
    # 1. Create Enum (with check for existence)
    bind = op.get_bind()
    
    has_enum = bind.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'calculationdimension'")).first()
    if not has_enum:
        sa.Enum('height_cm', 'width_cm', 'length_cm', 'custom', name='calculationdimension').create(bind)

    # 2. Add columns to specification_items
    inspector = sa.inspect(bind)
    existing_columns = [c['name'] for c in inspector.get_columns('specification_items')]

    if 'is_calculated' not in existing_columns:
        op.add_column('specification_items', sa.Column('is_calculated', sa.Boolean(), nullable=False, server_default='false'))
    
    if 'calc_dimension' not in existing_columns:
        op.add_column('specification_items', sa.Column('calc_dimension', sa.Enum('height_cm', 'width_cm', 'length_cm', 'custom', name='calculationdimension'), nullable=True))
    
    if 'calc_data_points' not in existing_columns:
        op.add_column('specification_items', sa.Column('calc_data_points', postgresql.JSON(), nullable=True))
    
    if 'calc_formula' not in existing_columns:
        op.add_column('specification_items', sa.Column('calc_formula', sa.String(length=500), nullable=True))
    
    if 'calc_waste_factor' not in existing_columns:
        op.add_column('specification_items', sa.Column('calc_waste_factor', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('specification_items', 'calc_waste_factor')
    op.drop_column('specification_items', 'calc_formula')
    op.drop_column('specification_items', 'calc_data_points')
    op.drop_column('specification_items', 'calc_dimension')
    op.drop_column('specification_items', 'is_calculated')
    
    bind = op.get_bind()
    bind.execute(sa.text("DROP TYPE calculationdimension"))
