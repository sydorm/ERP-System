"""add fop finance and limit

Revision ID: 027_add_fop_finance
Revises: 026_universal_dictionaries
Create Date: 2026-04-19 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '027_add_fop_finance'
down_revision = '026_universal_dictionaries'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create financial_transactions table
    op.create_table(
        'financial_transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('bank_account_id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=True),
        sa.Column('transaction_type', sa.Enum('IN', 'OUT', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='UAH', nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_transactions_company_id'), 'financial_transactions', ['company_id'], unique=False)
    op.create_index(op.f('ix_financial_transactions_transaction_date'), 'financial_transactions', ['transaction_date'], unique=False)

    # 2. Add fop_income_limit to companies
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='companies' AND column_name='fop_income_limit'"))
    if not res.first():
        op.add_column('companies', sa.Column('fop_income_limit', sa.Numeric(precision=15, scale=2), nullable=True))

def downgrade() -> None:
    op.drop_column('companies', 'fop_income_limit')
    op.drop_index(op.f('ix_financial_transactions_transaction_date'), table_name='financial_transactions')
    op.drop_index(op.f('ix_financial_transactions_company_id'), table_name='financial_transactions')
    op.drop_table('financial_transactions')
    op.execute('DROP TYPE transactiontype')
