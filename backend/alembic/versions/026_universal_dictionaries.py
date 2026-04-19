"""Universal dictionaries and linking them to orders

Revision ID: 026_universal_dictionaries
Revises: 025_add_crm_communication_tables
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = '026_universal_dictionaries'
down_revision = '025_add_crm_communication_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Update dictionary_items table
    existing_dict_cols = [c['name'] for c in inspector.get_columns('dictionary_items')]
    
    if 'type' not in existing_dict_cols:
        op.add_column('dictionary_items', sa.Column('type', sa.String(50), nullable=True))
        op.create_index('ix_dictionary_items_type', 'dictionary_items', ['type'])
    
    if 'order' not in existing_dict_cols:
        op.add_column('dictionary_items', sa.Column('order', sa.Integer(), nullable=False, server_default='0'))

    # 2. Update orders table
    existing_order_cols = [c['name'] for c in inspector.get_columns('orders')]
    
    columns_to_add = [
        ('lead_source_id', 'dictionary_items'),
        ('cancel_reason_id', 'dictionary_items'),
        ('delivery_method_id', 'dictionary_items'),
        ('client_type_id', 'dictionary_items'),
        ('priority_id', 'dictionary_items'),
        ('payment_status_id', 'dictionary_items'),
    ]

    for col_name, ref_table in columns_to_add:
        if col_name not in existing_order_cols:
            op.add_column('orders', sa.Column(col_name, postgresql.UUID(as_uuid=True), 
                                             sa.ForeignKey(f'{ref_table}.id', ondelete='SET NULL'), 
                                             nullable=True))

    # 3. Data Migration: Lead Sources
    # Fetch all orders with a channel string
    connection = op.get_bind()
    orders = connection.execute(sa.text("SELECT id, channel, company_id FROM orders WHERE channel IS NOT NULL")).fetchall()
    
    for row in orders:
        order_id, channel_name, company_id = row
        if not channel_name:
            continue
            
        # Check if dictionary item exists for this company and name (case insensitive)
        dict_item = connection.execute(sa.text(
            "SELECT id FROM dictionary_items WHERE company_id = :cid AND UPPER(name) = :name AND (category = 'LEAD_SOURCE' OR type = 'lead_source')"
        ), {"cid": company_id, "name": channel_name.upper()}).first()
        
        if not dict_item:
            # Create new dictionary item
            item_id = uuid.uuid4()
            code = channel_name.upper().replace(' ', '_')[:50]
            connection.execute(sa.text(
                "INSERT INTO dictionary_items (id, company_id, category, type, code, name, is_active, is_fixed, \"order\", created_at, updated_at) "
                "VALUES (:id, :cid, 'LEAD_SOURCE', 'lead_source', :code, :name, true, false, 0, now(), now())"
            ), {"id": item_id, "cid": company_id, "code": code, "name": channel_name})
            lead_source_id = item_id
        else:
            lead_source_id = dict_item[0]
            
        # Link order to lead source
        connection.execute(sa.text(
            "UPDATE orders SET lead_source_id = :lsid WHERE id = :oid"
        ), {"lsid": lead_source_id, "oid": order_id})

    # 4. Data Migration: Priorities, Payment Statuses, Delivery Types (Optional but good)
    # Mapping for priorities
    # priorities: low/normal/urgent/critical
    # payment_status: unpaid/partial/paid (or from Order model status)
    
    # [Skipping detailed migration for these as lead_source was the primary focus, 
    # but the structure is the same. We can add more if needed later.]

def downgrade() -> None:
    op.drop_column('orders', 'payment_status_id')
    op.drop_column('orders', 'priority_id')
    op.drop_column('orders', 'client_type_id')
    op.drop_column('orders', 'delivery_method_id')
    op.drop_column('orders', 'cancel_reason_id')
    op.drop_column('orders', 'lead_source_id')
    op.drop_index('ix_dictionary_items_type', 'dictionary_items')
    op.drop_column('dictionary_items', 'order')
    op.drop_column('dictionary_items', 'type')
