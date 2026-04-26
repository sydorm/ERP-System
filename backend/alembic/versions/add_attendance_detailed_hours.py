"""add attendance detailed hours

Revision ID: add_attendance_detailed_hours
Revises: expand_crm_tables
Create Date: 2026-04-24 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_attendance_detailed_hours'
down_revision = 'expand_crm_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='attendance_records' AND column_name='start_time'"
    ))
    if not res.first():
        op.add_column('attendance_records', sa.Column('start_time', sa.String(length=5), nullable=True))
        op.add_column('attendance_records', sa.Column('end_time', sa.String(length=5), nullable=True))
        op.add_column('attendance_records', sa.Column('break_hours', sa.Numeric(precision=5, scale=2), server_default='1.0', nullable=True))
        op.add_column('attendance_records', sa.Column('actual_hours', sa.Numeric(precision=5, scale=2), server_default='0.0', nullable=True))


def downgrade() -> None:
    op.drop_column('attendance_records', 'actual_hours')
    op.drop_column('attendance_records', 'break_hours')
    op.drop_column('attendance_records', 'end_time')
    op.drop_column('attendance_records', 'start_time')
