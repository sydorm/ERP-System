"""Rename product dimensions to mm and convert values

Revision ID: 8ffef82c1304
Revises: eaedb2bb097c
Create Date: 2026-04-30 15:17:41.684634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ffef82c1304'
down_revision = 'eaedb2bb097c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename columns
    op.alter_column('products', 'length_cm', new_column_name='length_mm')
    op.alter_column('products', 'width_cm', new_column_name='width_mm')
    op.alter_column('products', 'height_cm', new_column_name='height_mm')
    
    # Convert data (x10)
    op.execute("UPDATE products SET length_mm = length_mm * 10 WHERE length_mm IS NOT NULL")
    op.execute("UPDATE products SET width_mm = width_mm * 10 WHERE width_mm IS NOT NULL")
    op.execute("UPDATE products SET height_mm = height_mm * 10 WHERE height_mm IS NOT NULL")


def downgrade() -> None:
    # Convert data back (/10)
    op.execute("UPDATE products SET length_mm = length_mm / 10 WHERE length_mm IS NOT NULL")
    op.execute("UPDATE products SET width_mm = width_mm / 10 WHERE width_mm IS NOT NULL")
    op.execute("UPDATE products SET height_mm = height_mm / 10 WHERE height_mm IS NOT NULL")

    # Rename columns back
    op.alter_column('products', 'length_mm', new_column_name='length_cm')
    op.alter_column('products', 'width_mm', new_column_name='width_cm')
    op.alter_column('products', 'height_mm', new_column_name='height_cm')
