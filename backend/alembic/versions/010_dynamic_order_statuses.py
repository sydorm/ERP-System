"""dynamic order statuses

Revision ID: 010_dynamic_order_statuses
Revises: 009_sync_company_schema
Create Date: 2026-02-22 08:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_dynamic_order_statuses'
down_revision = '009_sync_company_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 1. Alter status column in orders table (safely)
    columns = inspector.get_columns('orders')
    status_col = next((c for c in columns if c['name'] == 'status'), None)
    
    if status_col and str(status_col['type']).lower() != 'varchar(50)':
        op.alter_column('orders', 'status',
                   existing_type=postgresql.ENUM('draft', 'confirmed', 'shipped', 'completed', 'cancelled', name='orderstatus'),
                   type_=sa.String(length=50),
                   existing_nullable=False,
                   postgresql_using='status::text')
    
    # 2. Add description column to dictionary_items if not exists (safely)
    dict_columns = [c['name'] for c in inspector.get_columns('dictionary_items')]
    if 'description' not in dict_columns:
        op.add_column('dictionary_items', sa.Column('description', sa.String(length=500), nullable=True))

    # 3. Seed initial order statuses for each company (safely)
    # We use NOT EXISTS to avoid duplicates
    statuses = [
        ('draft', 'Чернетка', 'gray', 1),
        ('confirmed', 'Підтверджено', 'blue', 2),
        ('shipped', 'Відправлено', 'orange', 3),
        ('completed', 'Виконано', 'green', 4),
        ('cancelled', 'Скасовано', 'red', 5)
    ]
    
    for code, name, color, order in statuses:
        op.execute(f"""
            INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
            SELECT 
                gen_random_uuid(), 
                id, 
                'ORDER_STATUS', 
                '{code}', 
                '{name}', 
                '{color}', 
                {order}, 
                true, 
                true
            FROM companies c
            WHERE NOT EXISTS (
                SELECT 1 FROM dictionary_items di 
                WHERE di.company_id = c.id AND di.category = 'ORDER_STATUS' AND di.code = '{code}'
            )
        """)

def downgrade() -> None:
    # 1. Remove seeded items
    op.execute("DELETE FROM dictionary_items WHERE category = 'ORDER_STATUS'")
    
    # 2. Drop description column
    op.drop_column('dictionary_items', 'description')

    # 3. Revert status column to Enum (Note: this is hard because we'd need to recreate the Enum type)
    # For now, we'll just keep it as String or throw an error if downgrade is strictly needed
    # op.alter_column('orders', 'status',
    #            type_=postgresql.ENUM('draft', 'confirmed', 'shipped', 'completed', 'cancelled', name='orderstatus'),
    #            postgresql_using='status::orderstatus')
    pass
