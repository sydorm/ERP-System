"""add contact results to dictionary

Revision ID: 030_add_contact_results_to_dictionary
Revises: 029_add_communication_type_to_contact
Create Date: 2026-04-20 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import uuid

# revision identifiers, used by Alembic.
revision = '030_add_contact_results_to_dictionary'
down_revision = '029_add_communication_type_to_contact'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Get all companies
    connection = op.get_bind()
    companies = connection.execute(text("SELECT id FROM companies")).fetchall()
    
    # 2. Results to seed
    results = [
        ('NO_ANSWER', 'Не відповів', '📵', 1, '#f97316'), # orange
        ('THINKING', 'Думає', '🤔', 2, '#eab308'),     # yellow
        ('REFUSED', 'Відмовився', '❌', 3, '#ef4444'),   # red
        ('CONFIRMED', 'Підтвердив замовлення', '✅', 4, '#22c55e') # green
    ]
    
    # 3. Seed for each company
    for company in companies:
        company_id = company[0]
        
        for code, name, icon, order, color in results:
            item_id = str(uuid.uuid4())
            connection.execute(
                text(
                    "INSERT INTO dictionary_items (id, company_id, category, type, code, name, icon, color, \"order\", sort_order, is_active, is_fixed, created_at, updated_at) "
                    "VALUES (:id, :company_id, 'CONTACT_RESULT', 'CONTACT_RESULT', :code, :name, :icon, :color, :order, :order, true, false, now(), now())"
                ),
                {
                    "id": item_id,
                    "company_id": company_id,
                    "code": code,
                    "name": name,
                    "icon": icon,
                    "order": order,
                    "color": color
                }
            )

def downgrade():
    op.execute("DELETE FROM dictionary_items WHERE category = 'CONTACT_RESULT'")
