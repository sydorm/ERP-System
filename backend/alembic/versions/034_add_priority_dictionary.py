"""add priority dictionary

Revision ID: 034_add_priority_dictionary
Revises: auto_merge_1777213904
Create Date: 2026-04-27 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '034_add_priority_dictionary'
down_revision = 'auto_merge_1777213904'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Get all company IDs
    connection = op.get_bind()
    companies = connection.execute(sa.text("SELECT id FROM companies")).fetchall()
    
    priorities = [
        ('LOW', 'Низький', '#94a3b8', 10),
        ('MEDIUM', 'Середній', '#3b82f6', 20),
        ('HIGH', 'Високий', '#f59e0b', 30),
        ('CRITICAL', 'Критичний', '#ef4444', 40),
    ]
    
    for company in companies:
        company_id = company[0]
        for code, name, color, order in priorities:
            # Check if already exists
            existing = connection.execute(
                sa.text("SELECT id FROM dictionary_items WHERE company_id = :cid AND category = 'PRIORITY' AND code = :code"),
                {"cid": company_id, "code": code}
            ).fetchone()
            
            if not existing:
                # Use sa.text for raw SQL insertion
                connection.execute(
                    sa.text("""
                        INSERT INTO dictionary_items (id, company_id, category, code, name, color, sort_order, "order", is_fixed, is_active, created_at, updated_at)
                        VALUES (:id, :cid, 'PRIORITY', :code, :name, :color, :order, :order, true, true, now(), now())
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "cid": company_id,
                        "code": code,
                        "name": name,
                        "color": color,
                        "order": order
                    }
                )


def downgrade() -> None:
    op.execute("DELETE FROM dictionary_items WHERE category = 'PRIORITY' AND is_fixed = true")
