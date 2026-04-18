"""Add CRM communication tables (crm_contacts, crm_tasks) and contact tracking columns to orders

Revision ID: 025_add_crm_communication_tables
Revises: 024_add_company_branding_columns
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '025_add_crm_communication_tables'
down_revision = '024_add_company_branding_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ── Add columns to orders ──────────────────────────────────────────────────
    existing_order_cols = [c['name'] for c in inspector.get_columns('orders')]

    if 'next_contact_at' not in existing_order_cols:
        op.add_column('orders', sa.Column('next_contact_at', sa.DateTime(), nullable=True))

    if 'contact_attempts' not in existing_order_cols:
        op.add_column('orders', sa.Column(
            'contact_attempts', sa.Integer(), nullable=False, server_default='0'
        ))

    # ── Create crm_contacts ───────────────────────────────────────────────────
    existing_tables = inspector.get_table_names()

    if 'crm_contacts' not in existing_tables:
        op.create_table(
            'crm_contacts',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text('gen_random_uuid()')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('order_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
            sa.Column('result', sa.String(50), nullable=False),
            sa.Column('note', sa.Text(), nullable=True),
            sa.Column('manager_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('contacted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        )
        op.create_index('ix_crm_contacts_order_id', 'crm_contacts', ['order_id'])

    # ── Create crm_tasks ──────────────────────────────────────────────────────
    if 'crm_tasks' not in existing_tables:
        op.create_table(
            'crm_tasks',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text('gen_random_uuid()')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('order_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
            sa.Column('scheduled_at', sa.DateTime(), nullable=False),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('manager_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        )
        op.create_index('ix_crm_tasks_manager_scheduled', 'crm_tasks', ['manager_id', 'scheduled_at'])


def downgrade() -> None:
    op.drop_table('crm_tasks')
    op.drop_table('crm_contacts')
    op.drop_column('orders', 'contact_attempts')
    op.drop_column('orders', 'next_contact_at')
