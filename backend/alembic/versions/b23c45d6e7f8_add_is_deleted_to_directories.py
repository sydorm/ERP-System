"""add is_deleted to directories

Revision ID: b23c45d6e7f8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-04 23:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23c45d6e7f8'
down_revision = '013_add_audit_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Add is_deleted column to products, counterparties, and warehouses (safely)
    for table_name in ['products', 'counterparties', 'warehouses']:
        existing_columns = [c['name'] for c in inspector.get_columns(table_name)]
        if 'is_deleted' not in existing_columns:
            op.add_column(table_name, sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Remove is_deleted column
    op.drop_column('warehouses', 'is_deleted')
    op.drop_column('counterparties', 'is_deleted')
    op.drop_column('products', 'is_deleted')
