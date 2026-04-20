"""add bank_account_id to orders

Revision ID: 944c49d34d89
Revises: 030_add_contact_results_to_dictionary
Create Date: 2026-04-20 19:06:38.136619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '944c49d34d89'
down_revision = '030_add_contact_results_to_dictionary'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adding bank_account_id to orders table
    op.add_column('orders', sa.Column('bank_account_id', sa.UUID(), sa.ForeignKey('bank_accounts.id', ondelete='SET NULL'), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'bank_account_id')
