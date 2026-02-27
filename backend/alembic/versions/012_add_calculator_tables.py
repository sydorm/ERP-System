"""add calculator tables

Revision ID: 012_add_calculator_tables
Revises: 011_fix_variant_fk
Create Date: 2026-02-27

"""
from alembic import op
import sqlalchemy as sa

revision = '012_add_calculator_tables'
down_revision = '011_fix_variant_fk'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === Матеріали (ЛДСП, ДВП, МДФ тощо) ===
    op.create_table(
        'calc_materials',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('thickness_mm', sa.Integer(), nullable=True),
        sa.Column('price_per_m2', sa.Numeric(12, 2), nullable=False, default=0),
        sa.Column('unit', sa.String(20), nullable=False, server_default='м²'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === Фурнітура (напрямні Muller, Blum тощо) ===
    op.create_table(
        'calc_hardware',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('length_mm', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False, server_default='направляючі'),
        sa.Column('price_per_unit', sa.Numeric(12, 2), nullable=False, default=0),
        sa.Column('unit', sa.String(20), nullable=False, server_default='пара'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === Послуги (складання, монтаж тощо) ===
    op.create_table(
        'calc_services',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False, default=0),
        sa.Column('unit', sa.String(50), nullable=False, server_default='шт'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === Збережені розрахунки (quotes) ===
    op.create_table(
        'calc_quotes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('client_name', sa.String(255), nullable=True),
        sa.Column('input_json', sa.Text(), nullable=False),
        sa.Column('result_json', sa.Text(), nullable=False),
        sa.Column('total_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === Seed data: базові матеріали ===
    op.execute("""
        INSERT INTO calc_materials (name, thickness_mm, price_per_m2, unit) VALUES
        ('ЛДСП 16мм білий', 16, 280, 'м²'),
        ('ЛДСП 18мм білий', 18, 320, 'м²'),
        ('ДВП 4мм (дно шухляди)', 4, 85, 'м²'),
        ('МДФ 16мм', 16, 360, 'м²'),
        ('ЛДСП 16мм сірий', 16, 290, 'м²')
    """)

    # === Seed data: фурнітура Muller + інші ===
    op.execute("""
        INSERT INTO calc_hardware (name, brand, length_mm, category, price_per_unit, unit) VALUES
        ('Напрямні роликові Muller 300мм', 'Muller', 300, 'направляючі', 85, 'пара'),
        ('Напрямні роликові Muller 350мм', 'Muller', 350, 'направляючі', 95, 'пара'),
        ('Напрямні роликові Muller 400мм', 'Muller', 400, 'направляючі', 105, 'пара'),
        ('Напрямні роликові Muller 450мм', 'Muller', 450, 'направляючі', 115, 'пара'),
        ('Напрямні роликові Muller 500мм', 'Muller', 500, 'направляючі', 125, 'пара'),
        ('Напрямні роликові Muller 550мм', 'Muller', 550, 'направляючі', 135, 'пара'),
        ('Напрямні кульові GTV 350мм', 'GTV', 350, 'направляючі', 145, 'пара'),
        ('Напрямні кульові GTV 450мм', 'GTV', 450, 'направляючі', 165, 'пара'),
        ('Ручка-рейлінг 128мм', NULL, NULL, 'ручки', 45, 'шт'),
        ('Ручка-рейлінг 192мм', NULL, NULL, 'ручки', 55, 'шт')
    """)

    # === Seed data: послуги ===
    op.execute("""
        INSERT INTO calc_services (name, price, unit) VALUES
        ('Різання матеріалу', 3, 'пог.м'),
        ('Крайкування (ПВХ 0.4мм)', 12, 'пог.м'),
        ('Крайкування (ПВХ 2мм)', 25, 'пог.м'),
        ('Складання шухляди', 150, 'шт'),
        ('Монтаж напрямних', 50, 'шт')
    """)


def downgrade() -> None:
    op.drop_table('calc_quotes')
    op.drop_table('calc_services')
    op.drop_table('calc_hardware')
    op.drop_table('calc_materials')
