"""add hr module v1

Revision ID: 7d2e9f1a0e8c
Revises: 3c81700abdaf
Create Date: 2026-04-22 18:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2e9f1a0e8c'
down_revision = '3c81700abdaf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # Check if table exists
    res = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='departments'"))
    if not res.first():
        # 1. Create Departments table
        op.create_table(
            'departments',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('company_id', sa.UUID(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('head_id', sa.UUID(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
        op.create_index(op.f('ix_departments_company_id'), 'departments', ['company_id'], unique=False)

        # 2. Create Employees table
        op.create_table(
            'employees',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('company_id', sa.UUID(), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=False),
            sa.Column('position', sa.String(length=255), nullable=False),
            sa.Column('department_id', sa.UUID(), nullable=False),
            sa.Column('status_id', sa.UUID(), nullable=False),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('birth_date', sa.Date(), nullable=True),
            sa.Column('hire_date', sa.Date(), nullable=True),
            sa.Column('photo_url', sa.String(length=500), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT'),
            sa.ForeignKeyConstraint(['status_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
        op.create_index(op.f('ix_employees_company_id'), 'employees', ['company_id'], unique=False)
        op.create_index(op.f('ix_employees_full_name'), 'employees', ['full_name'], unique=False)

        # Add head_id FK back to departments (cross-reference)
        op.create_foreign_key('fk_departments_head_id_employees', 'departments', 'employees', ['head_id'], ['id'], ondelete='SET NULL')

        # 3. Create Employee Roles table
        op.create_table(
            'employee_roles',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('employee_id', sa.UUID(), nullable=False),
            sa.Column('role_id', sa.UUID(), nullable=False),
            sa.Column('role_type_id', sa.UUID(), nullable=False),
            sa.Column('accrual_type_id', sa.UUID(), nullable=False),
            sa.Column('rate', sa.Numeric(precision=15, scale=2), server_default='0.00', nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['role_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
            sa.ForeignKeyConstraint(['role_type_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
            sa.ForeignKeyConstraint(['accrual_type_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_employee_roles_id'), 'employee_roles', ['id'], unique=False)
        op.create_index(op.f('ix_employee_roles_employee_id'), 'employee_roles', ['employee_id'], unique=False)


def downgrade() -> None:
    op.drop_table('employee_roles')
    # Must remove FK before dropping table due to circular dependency if any (though SET NULL handles it)
    op.drop_constraint('fk_departments_head_id_employees', 'departments', type_='foreignkey')
    op.drop_table('employees')
    op.drop_table('departments')
