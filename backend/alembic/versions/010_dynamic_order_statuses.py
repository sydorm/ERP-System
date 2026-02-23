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
    # 1. Alter status column in orders table
    # We use USING status::text to convert the Enum value to a String
    op.alter_column('orders', 'status',
               existing_type=postgresql.ENUM('draft', 'confirmed', 'shipped', 'completed', 'cancelled', name='orderstatus'),
               type_=sa.String(length=50),
               existing_nullable=False,
               postgresql_using='status::text')
    
    # 2. Add description column to dictionary_items if not exists (it was missing from 004)
    # Actually let's check dictionary_items columns first. 
    # From 004 it doesn't have 'description'. Let's add it as it's used in the frontend.
    op.add_column('dictionary_items', sa.Column('description', sa.String(length=500), nullable=True))

    # 3. Seed initial order statuses for each company
    # We'll insert defaults: draft, confirmed, shipped, completed, cancelled
    op.execute("""
        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
        SELECT 
            gen_random_uuid(), 
            id, 
            'ORDER_STATUS', 
            'draft', 
            'Чернетка', 
            'gray', 
            1, 
            true, 
            true
        FROM companies
    """)
    op.execute("""
        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
        SELECT 
            gen_random_uuid(), 
            id, 
            'ORDER_STATUS', 
            'confirmed', 
            'Підтверджено', 
            'blue', 
            2, 
            true, 
            true
        FROM companies
    """)
    op.execute("""
        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
        SELECT 
            gen_random_uuid(), 
            id, 
            'ORDER_STATUS', 
            'shipped', 
            'Відправлено', 
            'orange', 
            3, 
            true, 
            true
        FROM companies
    """)
    op.execute("""
        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
        SELECT 
            gen_random_uuid(), 
            id, 
            'ORDER_STATUS', 
            'completed', 
            'Виконано', 
            'green', 
            4, 
            true, 
            true
        FROM companies
    """)
    op.execute("""
        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, is_fixed, is_active)
        SELECT 
            gen_random_uuid(), 
            id, 
            'ORDER_STATUS', 
            'cancelled', 
            'Скасовано', 
            'red', 
            5, 
            true, 
            true
        FROM companies
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
