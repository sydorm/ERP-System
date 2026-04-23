"""add brigades and resource mgmt

Revision ID: 51a2b3c4d5e6
Revises: b4e5f6a7c8d9
Create Date: 2026-04-23 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '51a2b3c4d5e6'
down_revision = 'b4e5f6a7c8d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Check if brigades table exists
    bind = op.get_bind()
    inspect_obj = sa.inspect(bind)
    
    if not inspect_obj.has_table('brigades'):
        op.create_table(
            'brigades',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('stage_id', sa.UUID(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['stage_id'], ['dictionary_items.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    if not inspect_obj.has_table('brigade_members'):
        op.create_table(
            'brigade_members',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('brigade_id', sa.UUID(), nullable=False),
            sa.Column('employee_id', sa.UUID(), nullable=False),
            sa.Column('role_type', sa.String(length=50), nullable=True, server_default='main'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['brigade_id'], ['brigades.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_brigade_members_brigade_id'), 'brigade_members', ['brigade_id'], unique=False)

    # 2. Update specification_stages
    stages_columns = [c['name'] for c in inspect_obj.get_columns('specification_stages')]
    if 'brigade_id' not in stages_columns:
        op.add_column('specification_stages', sa.Column('brigade_id', sa.UUID(), nullable=True))
        op.create_foreign_key('fk_spec_stages_brigade_id', 'specification_stages', 'brigades', ['brigade_id'], ['id'], ondelete='RESTRICT')
    
    # Optional: remove role_id if it exists
    if 'role_id' in stages_columns:
        op.drop_column('specification_stages', 'role_id')

    # 3. Update production_order_assignments
    assign_columns = [c['name'] for c in inspect_obj.get_columns('production_order_assignments')]
    if 'brigade_id' not in assign_columns:
        op.add_column('production_order_assignments', sa.Column('brigade_id', sa.UUID(), nullable=True))
        op.create_foreign_key('fk_prod_assign_brigade_id', 'production_order_assignments', 'brigades', ['brigade_id'], ['id'], ondelete='SET NULL')
    
    if 'planned_hours' not in assign_columns:
        op.add_column('production_order_assignments', sa.Column('planned_hours', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'))
    
    if 'status' not in assign_columns:
        op.add_column('production_order_assignments', sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'))


def downgrade() -> None:
    # We don't usually need a complex downgrade for these manual fixes but let's be clean
    op.drop_column('production_order_assignments', 'status')
    op.drop_column('production_order_assignments', 'planned_hours')
    op.drop_constraint('fk_prod_assign_brigade_id', 'production_order_assignments', type_='foreignkey')
    op.drop_column('production_order_assignments', 'brigade_id')
    
    op.drop_constraint('fk_spec_stages_brigade_id', 'specification_stages', type_='foreignkey')
    op.drop_column('specification_stages', 'brigade_id')
    
    op.drop_index(op.f('ix_brigade_members_brigade_id'), table_name='brigade_members')
    op.drop_table('brigade_members')
    op.drop_table('brigades')
