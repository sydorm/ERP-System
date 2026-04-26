"""add tax settings json column

Revision ID: 028_add_tax_settings
Revises: 027_add_fop_finance
Create Date: 2026-04-19 17:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '028_add_tax_settings'
down_revision = '027_add_fop_finance'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='companies' AND column_name='tax_settings'"))
    if not res.first():
        op.add_column('companies', sa.Column('tax_settings', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('companies', 'tax_settings')
