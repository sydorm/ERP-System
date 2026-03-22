"""add_audit_logs

Revision ID: 013_add_audit_logs
Revises: 012_add_calculator_tables
Create Date: 2026-03-07 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '013_add_audit_logs'
down_revision: Union[str, None] = '012_add_calculator_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    try:
        op.create_table('audit_logs',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('entity_type', sa.String(), nullable=False),
            sa.Column('entity_id', sa.UUID(), nullable=False),
            sa.Column('action', sa.String(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=True),
            sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
        op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    except Exception as e:
        print(f"Skipping audit_logs creation: {e}")

def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
