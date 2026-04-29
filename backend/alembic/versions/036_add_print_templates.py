"""Add print templates table

Revision ID: 036_add_print_templates
Revises: 035_add_user_fields
Create Date: 2026-04-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '036_add_print_templates'
down_revision = '035_add_user_fields'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'print_templates' not in existing_tables:
        op.create_table(
            'print_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('document_type', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('html_template', sa.Text(), nullable=False),
            sa.Column('css_template', sa.Text(), nullable=True),
            sa.Column('is_default', sa.Boolean(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_print_templates_document_type', 'print_templates', ['document_type'])

def downgrade() -> None:
    op.drop_index('ix_print_templates_document_type', table_name='print_templates')
    op.drop_table('print_templates')
