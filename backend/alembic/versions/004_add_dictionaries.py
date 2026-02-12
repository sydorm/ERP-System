"""add dictionary items

Revision ID: 004_add_dictionaries
Revises: 003_update_products
Create Date: 2026-02-12 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_dictionaries'
down_revision = '003_update_products'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'dictionary_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_fixed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dictionary_items_company_id'), 'dictionary_items', ['company_id'], unique=False)
    op.create_index(op.f('ix_dictionary_items_category'), 'dictionary_items', ['category'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_dictionary_items_category'), table_name='dictionary_items')
    op.drop_index(op.f('ix_dictionary_items_company_id'), table_name='dictionary_items')
    op.drop_table('dictionary_items')
