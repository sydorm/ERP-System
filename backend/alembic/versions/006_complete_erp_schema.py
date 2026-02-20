"""complete erp schema

Revision ID: 006_complete_erp_schema
Revises: 005_add_attributes_and_variants
Create Date: 2026-02-20 17:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_complete_erp_schema'
down_revision = '005_add_attributes_and_variants'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Bank Accounts
    op.create_table(
        'bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_name', sa.String(length=255), nullable=True),
        sa.Column('mfo', sa.String(length=10), nullable=True),
        sa.Column('iban', sa.String(length=34), nullable=False),
        sa.Column('currency', sa.Enum('UAH', 'USD', 'EUR', name='currency'), nullable=False, server_default='UAH'),
        sa.Column('is_primary', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_company_id'), 'bank_accounts', ['company_id'], unique=False)

    # 2. Accumulation Registers
    op.create_table(
        'accumulation_registers',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('register_type', sa.Enum('STOCK', 'FINANCE', 'AR_AP', name='registertype'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('counterparty_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), server_default='0', nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), server_default='0', nullable=True),
        sa.Column('currency', sa.String(length=3), server_default='UAH', nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['counterparty_id'], ['counterparties.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accumulation_registers_company_id'), 'accumulation_registers', ['company_id'], unique=False)
    op.create_index(op.f('ix_accumulation_registers_document_id'), 'accumulation_registers', ['document_id'], unique=False)
    op.create_index(op.f('ix_accumulation_registers_document_type'), 'accumulation_registers', ['document_type'], unique=False)
    op.create_index(op.f('ix_accumulation_registers_product_id'), 'accumulation_registers', ['product_id'], unique=False)
    op.create_index(op.f('ix_accumulation_registers_register_type'), 'accumulation_registers', ['register_type'], unique=False)

    # 3. Product Specifications
    op.create_table(
        'product_specifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_specifications_product_id'), 'product_specifications', ['product_id'], unique=False)

    # 4. Specification Items
    op.create_table(
        'specification_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('specification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('component_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), server_default='1.0', nullable=False),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['component_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['specification_id'], ['product_specifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_specification_items_specification_id'), 'specification_items', ['specification_id'], unique=False)

    # 5. Product Files
    op.create_table(
        'product_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_url', sa.String(length=1000), nullable=False),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_files_product_id'), 'product_files', ['product_id'], unique=False)

    # 6. Purchase Receipts
    op.create_table(
        'purchase_receipts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('receipt_number', sa.String(length=50), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'POSTED', 'CANCELLED', name='purchasereceiptstatus'), server_default='DRAFT', nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), server_default='0.00', nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='UAH', nullable=True),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['supplier_id'], ['counterparties.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_receipts_receipt_number'), 'purchase_receipts', ['receipt_number'], unique=True)

    # 7. Purchase Receipt Lines
    op.create_table(
        'purchase_receipt_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('receipt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['receipt_id'], ['purchase_receipts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Sales Invoices
    op.create_table(
        'sales_invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'POSTED', 'CANCELLED', name='salesinvoicestatus'), server_default='DRAFT', nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), server_default='0.00', nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='UAH', nullable=True),
        sa.Column('counterparty_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['counterparty_id'], ['counterparties.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_invoices_invoice_number'), 'sales_invoices', ['invoice_number'], unique=True)

    # 9. Sales Invoice Lines
    op.create_table(
        'sales_invoice_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['sales_invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('sales_invoice_lines')
    op.drop_index(op.f('ix_sales_invoices_invoice_number'), table_name='sales_invoices')
    op.drop_table('sales_invoices')
    op.drop_table('purchase_receipt_lines')
    op.drop_index(op.f('ix_purchase_receipts_receipt_number'), table_name='purchase_receipts')
    op.drop_table('purchase_receipts')
    op.drop_index(op.f('ix_product_files_product_id'), table_name='product_files')
    op.drop_table('product_files')
    op.drop_index(op.f('ix_specification_items_specification_id'), table_name='specification_items')
    op.drop_table('specification_items')
    op.drop_index(op.f('ix_product_specifications_product_id'), table_name='product_specifications')
    op.drop_table('product_specifications')
    op.drop_index(op.f('ix_accumulation_registers_register_type'), table_name='accumulation_registers')
    op.drop_index(op.f('ix_accumulation_registers_product_id'), table_name='accumulation_registers')
    op.drop_index(op.f('ix_accumulation_registers_document_type'), table_name='accumulation_registers')
    op.drop_index(op.f('ix_accumulation_registers_document_id'), table_name='accumulation_registers')
    op.drop_index(op.f('ix_accumulation_registers_company_id'), table_name='accumulation_registers')
    op.drop_table('accumulation_registers')
    op.drop_index(op.f('ix_bank_accounts_company_id'), table_name='bank_accounts')
    op.drop_table('bank_accounts')
    
    # Drop Enums
    sa.Enum(name='currency').drop(op.get_bind())
    sa.Enum(name='registertype').drop(op.get_bind())
    sa.Enum(name='purchasereceiptstatus').drop(op.get_bind())
    sa.Enum(name='salesinvoicestatus').drop(op.get_bind())
