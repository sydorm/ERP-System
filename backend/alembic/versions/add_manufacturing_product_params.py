"""add manufacturing product params

Revision ID: add_manufacturing_product_params
Revises: add_attendance_detailed_hours
Create Date: 2026-04-25 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_manufacturing_product_params'
down_revision = 'add_attendance_detailed_hours'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='products' AND column_name='production_time_hours'"
    ))
    if not res.first():
        # Manufacturing Parameters
        op.add_column('products', sa.Column('production_time_hours', sa.Numeric(precision=10, scale=2), nullable=True))
        op.add_column('products', sa.Column('complexity_code', sa.String(length=50), nullable=True))
        # min_production_batch might already exist if complexity_code exists, but let's be safe
        op.add_column('products', sa.Column('min_production_batch', sa.Integer(), nullable=True, server_default='1'))
        op.add_column('products', sa.Column('max_production_per_day', sa.Integer(), nullable=True))
        op.add_column('products', sa.Column('special_production_conditions', sa.Text(), nullable=True))
        
        # Performer Restrictions
        op.add_column('products', sa.Column('performer_restriction_type', sa.String(length=50), nullable=True, server_default='any_role'))
        op.add_column('products', sa.Column('restricted_brigade_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.add_column('products', sa.Column('restricted_employee_id', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Foreign keys
        op.create_foreign_key('fk_products_restricted_brigade', 'products', 'brigades', ['restricted_brigade_id'], ['id'], ondelete='SET NULL')
        op.create_foreign_key('fk_products_restricted_employee', 'products', 'employees', ['restricted_employee_id'], ['id'], ondelete='SET NULL')

def downgrade() -> None:
    op.drop_constraint('fk_products_restricted_employee', 'products', type_='foreignkey')
    op.drop_constraint('fk_products_restricted_brigade', 'products', type_='foreignkey')
    
    op.drop_column('products', 'restricted_employee_id')
    op.drop_column('products', 'restricted_brigade_id')
    op.drop_column('products', 'performer_restriction_type')
    op.drop_column('products', 'special_production_conditions')
    op.drop_column('products', 'max_production_per_day')
    op.drop_column('products', 'min_production_batch')
    op.drop_column('products', 'complexity_code')
    op.drop_column('products', 'production_time_hours')
