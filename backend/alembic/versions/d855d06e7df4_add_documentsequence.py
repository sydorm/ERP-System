"""Add DocumentSequence

Revision ID: d855d06e7df4
Revises: 008_add_counterparty_contract
Create Date: 2026-02-21 15:13:52.157372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd855d06e7df4'
down_revision = '008_add_counterparty_contract'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        op.create_table(
            'document_sequences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('document_type', sa.String(length=50), nullable=False),
            sa.Column('prefix', sa.String(length=20), nullable=False),
            sa.Column('next_number', sa.Integer(), nullable=False),
            sa.Column('padding', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_document_sequences_document_type'), 'document_sequences', ['document_type'], unique=True)
        op.create_index(op.f('ix_document_sequences_id'), 'document_sequences', ['id'], unique=False)
    except Exception as e:
        print(f"Skipping document_sequences creation: {e}")


def downgrade() -> None:
    op.drop_index(op.f('ix_document_sequences_id'), table_name='document_sequences')
    op.drop_index(op.f('ix_document_sequences_document_type'), table_name='document_sequences')
    op.drop_table('document_sequences')
