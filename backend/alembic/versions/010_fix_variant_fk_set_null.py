"""fix variant fk set null

Revision ID: 010_fix_variant_fk
Revises: 
Create Date: 2026-02-24

"""
from alembic import op
import sqlalchemy as sa

revision = '010_fix_variant_fk'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old RESTRICT constraint and recreate as SET NULL
    op.drop_constraint(
        'order_lines_variant_id_fkey',
        'order_lines',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'order_lines_variant_id_fkey',
        'order_lines',
        'product_variants',
        ['variant_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint(
        'order_lines_variant_id_fkey',
        'order_lines',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'order_lines_variant_id_fkey',
        'order_lines',
        'product_variants',
        ['variant_id'],
        ['id'],
        ondelete='RESTRICT'
    )
