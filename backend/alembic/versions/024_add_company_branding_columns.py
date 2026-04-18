"""Add branding columns to companies table

Revision ID: 024_add_company_branding_columns
Revises: 023_add_crm_fields_to_orders
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = '024_add_company_branding_columns'
down_revision = '023_add_crm_fields_to_orders'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = [c['name'] for c in inspector.get_columns('companies')]

    cols = [
        ('logo_url',      sa.String(255)),
        ('stamp_url',     sa.String(255)),
        ('signature_url', sa.String(255)),
    ]
    for col_name, col_type in cols:
        if col_name not in existing:
            op.add_column('companies', sa.Column(col_name, col_type, nullable=True))


def downgrade() -> None:
    for col in ['signature_url', 'stamp_url', 'logo_url']:
        op.drop_column('companies', col)
