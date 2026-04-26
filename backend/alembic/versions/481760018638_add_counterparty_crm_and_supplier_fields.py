"""add_counterparty_crm_and_supplier_fields

Revision ID: 481760018638
Revises: merge_purchasing_resources
Create Date: 2026-04-23 23:35:21.131064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '481760018638'
down_revision = 'merge_purchasing_resources'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # Check if column exists
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='counterparties' AND column_name='acquisition_channel_id'"
    ))
    if not res.first():
        # Adding new fields to counterparties table
        op.add_column('counterparties', sa.Column('acquisition_channel_id', sa.UUID(), sa.ForeignKey('dictionary_items.id', ondelete='SET NULL'), nullable=True))
        op.add_column('counterparties', sa.Column('city', sa.String(length=255), nullable=True))
        op.add_column('counterparties', sa.Column('np_department', sa.String(length=255), nullable=True))
        op.add_column('counterparties', sa.Column('discount_percent', sa.Integer(), nullable=True, server_default='0'))
        op.add_column('counterparties', sa.Column('notes', sa.Text(), nullable=True))
        op.add_column('counterparties', sa.Column('tags', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        op.add_column('counterparties', sa.Column('min_order_amount', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0.00'))
        op.add_column('counterparties', sa.Column('contact_person', sa.String(length=255), nullable=True))
        op.add_column('counterparties', sa.Column('supplied_materials', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('counterparties', 'supplied_materials')
    op.drop_column('counterparties', 'contact_person')
    op.drop_column('counterparties', 'min_order_amount')
    op.drop_column('counterparties', 'tags')
    op.drop_column('counterparties', 'notes')
    op.drop_column('counterparties', 'discount_percent')
    op.drop_column('counterparties', 'np_department')
    op.drop_column('counterparties', 'city')
    op.drop_column('counterparties', 'acquisition_channel_id')
