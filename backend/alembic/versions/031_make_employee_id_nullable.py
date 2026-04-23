"""make employee_id nullable
 
Revision ID: 031_make_employee_id_nullable
Revises: b4e5f6a7c8d9
Create Date: 2026-04-23 15:52:00.000000
 
"""
from alembic import op
import sqlalchemy as sa
 
# revision identifiers, used by Alembic.
revision = '031_make_employee_id_nullable'
down_revision = 'b4e5f6a7c8d9'
branch_labels = None
depends_on = None
 
def upgrade() -> None:
    # 1. Update ProductionOrderWorkerAssignment table
    # We use batch_op for SQLite/Postgres compatibility if needed, but here raw op is fine
    op.alter_column('production_order_assignments', 'employee_id',
               existing_type=sa.UUID(),
               nullable=True)
 
def downgrade() -> None:
    op.alter_column('production_order_assignments', 'employee_id',
               existing_type=sa.UUID(),
               nullable=False)
