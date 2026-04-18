"""Add CRM fields to orders table

Revision ID: 023_add_crm_fields_to_orders
Revises: 022_add_dimensions_attribute_type
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '023_add_crm_fields_to_orders'
down_revision = '022_add_dimensions_attribute_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('crm_stage', sa.String(50), nullable=False, server_default='new'))
    op.add_column('orders', sa.Column('attributes_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('orders', sa.Column('channel', sa.String(50), nullable=True))
    op.add_column('orders', sa.Column('city', sa.String(255), nullable=True))
    op.add_column('orders', sa.Column('delivery_type', sa.String(50), nullable=True))
    op.add_column('orders', sa.Column('prepayment_percent', sa.Numeric(5, 2), nullable=True))
    op.add_column('orders', sa.Column('prepayment_amount', sa.Numeric(15, 2), nullable=True))
    op.add_column('orders', sa.Column('paid_amount', sa.Numeric(15, 2), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('payment_status', sa.String(50), nullable=False, server_default='unpaid'))
    op.add_column('orders', sa.Column('deadline_date', sa.Date(), nullable=True))
    op.add_column('orders', sa.Column('priority', sa.String(20), nullable=False, server_default='normal'))
    op.add_column('orders', sa.Column('manager_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('orders', sa.Column('next_contact_date', sa.Date(), nullable=True))
    op.add_column('orders', sa.Column('internal_notes', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('reference_photo', sa.String(500), nullable=True))

    op.create_foreign_key(
        'fk_orders_manager_id', 'orders', 'users',
        ['manager_id'], ['id'], ondelete='SET NULL'
    )
    op.create_index('ix_orders_crm_stage', 'orders', ['crm_stage'])
    op.create_index('ix_orders_payment_status', 'orders', ['payment_status'])


def downgrade() -> None:
    op.drop_index('ix_orders_payment_status', table_name='orders')
    op.drop_index('ix_orders_crm_stage', table_name='orders')
    op.drop_constraint('fk_orders_manager_id', 'orders', type_='foreignkey')
    for col in ['reference_photo', 'internal_notes', 'next_contact_date', 'manager_id',
                'priority', 'deadline_date', 'payment_status', 'paid_amount',
                'prepayment_amount', 'prepayment_percent', 'delivery_type',
                'city', 'channel', 'attributes_values', 'crm_stage']:
        op.drop_column('orders', col)
