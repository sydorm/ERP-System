"""add communication_type to contact and seed dictionary

Revision ID: 029_add_communication_type_to_contact
Revises: 028_add_tax_settings
Create Date: 2026-04-20 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '029_add_comm_type_contact'
down_revision = '028_add_tax_settings'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add column to crm_contacts
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='crm_contacts' AND column_name='communication_type'"))
    if not res.first():
        op.add_column('crm_contacts', sa.Column('communication_type', sa.String(length=50), nullable=True))
    
    # 2. Seed communication types for all existing companies
    # We use a raw SQL approach to insert initial dictionary items for each company
    # The DictionaryItem model has: company_id, category, code, name, icon, is_active, is_fixed, order
    
    connection = op.get_bind()
    
    # Get all company IDs
    companies = connection.execute(sa.text("SELECT id FROM companies")).fetchall()
    
    initial_types = [
        ('CALL', 'Телефонний дзвінок', '📞', 1),
        ('VIBER', 'Повідомлення Viber', '💬', 2),
        ('TELEGRAM', 'Повідомлення Telegram', '✈️', 3),
        ('INSTAGRAM', 'Instagram Direct', '📸', 4),
        ('SMS', 'SMS', '📱', 5),
        ('EMAIL', 'Email', '✉️', 6),
        ('MEET', 'Особиста зустріч', '🤝', 7),
    ]
    
    for company in companies:
        company_id = company[0]
        for code, name, icon, order in initial_types:
            item_id = str(uuid.uuid4())
            connection.execute(sa.text(
                "INSERT INTO dictionary_items (id, company_id, category, type, code, name, icon, \"order\", sort_order, is_active, is_fixed, created_at, updated_at) "
                "VALUES (:id, :company_id, 'COMMUNICATION_TYPE', 'COMMUNICATION_TYPE', :code, :name, :icon, :order, :order, true, false, now(), now())"
            ), {
                "id": item_id,
                "company_id": company_id,
                "code": code,
                "name": name,
                "icon": icon,
                "order": order
            })

def downgrade() -> None:
    # 1. Remove dictionary items
    op.execute(sa.text("DELETE FROM dictionary_items WHERE category = 'COMMUNICATION_TYPE'"))
    
    # 2. Drop column
    op.drop_column('crm_contacts', 'communication_type')
