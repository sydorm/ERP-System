"""Fix variants and specification dimensions

Revision ID: 1a2b3c4d5e6f
Revises: 8ffef82c1304
Create Date: 2026-04-30 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '8ffef82c1304'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Rename columns in product_variants
    op.alter_column('product_variants', 'length_cm', new_column_name='length_mm')
    op.alter_column('product_variants', 'width_cm', new_column_name='width_mm')
    op.alter_column('product_variants', 'height_cm', new_column_name='height_mm')
    
    # 2. Convert data in product_variants (x10)
    op.execute("UPDATE product_variants SET length_mm = length_mm * 10 WHERE length_mm IS NOT NULL")
    op.execute("UPDATE product_variants SET width_mm = width_mm * 10 WHERE width_mm IS NOT NULL")
    op.execute("UPDATE product_variants SET height_mm = height_mm * 10 WHERE height_mm IS NOT NULL")

    # 3. Update ENUM values for calculationdimension
    # PostgreSQL specific ALTER TYPE RENAME VALUE
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'height_cm' TO 'height_mm'")
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'width_cm' TO 'width_mm'")
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'length_cm' TO 'length_mm'")

    # 4. Add PROPORTIONAL to calculationtype if not exists
    # We check if it's already there to avoid errors
    op.execute("COMMIT") # Can't do ALTER TYPE in transaction in some cases, but here we might need it
    op.execute("ALTER TYPE calculationtype ADD VALUE IF NOT EXISTS 'proportional'")


def downgrade() -> None:
    # 1. Convert data back (/10)
    op.execute("UPDATE product_variants SET length_mm = length_mm / 10 WHERE length_mm IS NOT NULL")
    op.execute("UPDATE product_variants SET width_mm = width_mm / 10 WHERE width_mm IS NOT NULL")
    op.execute("UPDATE product_variants SET height_mm = height_mm / 10 WHERE height_mm IS NOT NULL")

    # 2. Rename columns back
    op.alter_column('product_variants', 'length_mm', new_column_name='length_cm')
    op.alter_column('product_variants', 'width_mm', new_column_name='width_cm')
    op.alter_column('product_variants', 'height_mm', new_column_name='height_cm')

    # 3. Rename ENUM values back
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'height_mm' TO 'height_cm'")
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'width_mm' TO 'width_cm'")
    op.execute("ALTER TYPE calculationdimension RENAME VALUE 'length_mm' TO 'length_cm'")

    # Note: Removing enum values is not supported in PostgreSQL without recreating the type
