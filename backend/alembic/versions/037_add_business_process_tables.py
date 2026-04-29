"""Add business process tables

Revision ID: 037_add_business_process_tables
Revises: 036_add_print_templates
Create Date: 2026-04-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '037_add_business_process_tables'
down_revision = '036_add_print_templates'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'business_process_rules' not in existing_tables:
        op.create_table(
            'business_process_rules',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('source_type', sa.String(length=50), nullable=False),
            sa.Column('event_type', sa.String(length=50), nullable=False),
            sa.Column('from_status', sa.String(length=50), nullable=True),
            sa.Column('to_status', sa.String(length=50), nullable=False),
            sa.Column('action_type', sa.String(length=50), nullable=False),
            sa.Column('mode', sa.String(length=30), nullable=False, server_default='ask_confirmation'),
            sa.Column('prevent_duplicates', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('log_execution', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_business_process_rules_company_id', 'business_process_rules', ['company_id'])

    if 'document_relations' not in existing_tables:
        op.create_table(
            'document_relations',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('source_type', sa.String(length=50), nullable=False),
            sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('target_type', sa.String(length=50), nullable=False),
            sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('relation_type', sa.String(length=50), nullable=False, server_default='created_from'),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_document_relations_source_type_source_id', 'document_relations', ['source_type', 'source_id'])
        op.create_index('ix_document_relations_target_id', 'document_relations', ['target_id'])
        op.create_index('ix_document_relations_company_id', 'document_relations', ['company_id'])

    if 'automation_logs' not in existing_tables:
        op.create_table(
            'automation_logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('business_process_rules.id', ondelete='SET NULL'), nullable=True),
            sa.Column('event_type', sa.String(length=50), nullable=False),
            sa.Column('source_type', sa.String(length=50), nullable=False),
            sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('action_type', sa.String(length=50), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=False),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('created_document_type', sa.String(length=50), nullable=True),
            sa.Column('created_document_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_automation_logs_source_id', 'automation_logs', ['source_id'])
        op.create_index('ix_automation_logs_rule_id', 'automation_logs', ['rule_id'])
        op.create_index('ix_automation_logs_company_id', 'automation_logs', ['company_id'])


def downgrade() -> None:
    op.drop_table('automation_logs')
    op.drop_table('document_relations')
    op.drop_table('business_process_rules')
