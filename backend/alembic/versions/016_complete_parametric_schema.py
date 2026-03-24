"""complete parametric schema

Revision ID: 016_complete_parametric_schema
Revises: f8g9h0i1j2k3
Create Date: 2026-03-24 18:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '016_complete_parametric_schema'
down_revision = 'f8g9h0i1j2k3'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Update calculationdimension enum
    # Postgres doesn't allow adding values to Enum inside a transaction easily in older versions, 
    # but we can use op.execute
    op.execute("ALTER TYPE calculationdimension ADD VALUE IF NOT EXISTS 'area'")
    op.execute("ALTER TYPE calculationdimension ADD VALUE IF NOT EXISTS 'volume'")

    # 2. Create calculationtype enum
    bind = op.get_bind()
    has_type_enum = bind.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'calculationtype'")).first()
    if not has_type_enum:
        sa.Enum('fixed', 'interpolation', 'area', 'volume', 'formula', name='calculationtype').create(bind)

    # 3. Add columns to products
    op.add_column('products', sa.Column('length_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('width_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('height_cm', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('weight_kg', sa.Numeric(precision=10, scale=2), nullable=True))

    # 4. Add calc_type to specification_items
    op.add_column('specification_items', sa.Column('calc_type', sa.Enum('fixed', 'interpolation', 'area', 'volume', 'formula', name='calculationtype'), nullable=True, server_default='fixed'))

def downgrade():
    op.drop_column('specification_items', 'calc_type')
    op.drop_column('products', 'weight_kg')
    op.drop_column('products', 'height_cm')
    op.drop_column('products', 'width_cm')
    op.drop_column('products', 'length_cm')
    
    op.execute("DROP TYPE calculationtype")
    # Note: Removing values from Enum is not supported by Postgres without dropping and recreating
