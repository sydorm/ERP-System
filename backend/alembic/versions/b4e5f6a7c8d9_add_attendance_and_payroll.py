"""add attendance and payroll

Revision ID: b4e5f6a7c8d9
Revises: 7d2e9f1a0e8c
Create Date: 2026-04-22 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4e5f6a7c8d9'
down_revision = '7d2e9f1a0e8c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Update Users table - link to employee
    op.add_column('users', sa.Column('employee_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_users_employee_id_employees', 'users', 'employees', ['employee_id'], ['id'], ondelete='SET NULL')

    # 2. Attendance Records
    op.create_table(
        'attendance_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status_id', sa.UUID(), nullable=False),
        sa.Column('notes', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['status_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'date', name='uix_employee_attendance_date')
    )
    op.create_index(op.f('ix_attendance_records_id'), 'attendance_records', ['id'], unique=False)
    op.create_index(op.f('ix_attendance_records_employee_id'), 'attendance_records', ['employee_id'], unique=False)
    op.create_index(op.f('ix_attendance_records_date'), 'attendance_records', ['date'], unique=False)

    # 3. Payroll Transactions
    op.create_table(
        'payroll_transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=False),
        sa.Column('production_order_id', sa.UUID(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['dictionary_items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_transactions_id'), 'payroll_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_payroll_transactions_employee_id'), 'payroll_transactions', ['employee_id'], unique=False)
    op.create_index(op.f('ix_payroll_transactions_date'), 'payroll_transactions', ['date'], unique=False)


def downgrade() -> None:
    op.drop_table('payroll_transactions')
    op.drop_table('attendance_records')
    op.drop_constraint('fk_users_employee_id_employees', 'users', type_='foreignkey')
    op.drop_column('users', 'employee_id')
