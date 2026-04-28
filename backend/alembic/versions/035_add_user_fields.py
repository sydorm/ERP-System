"""Add phone, blocked_at, last_login_at, avatar_url to users

Revision ID: 035_add_user_fields
Revises: 3c81700abdaf
Create Date: 2026-04-29 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '035_add_user_fields'
down_revision = '3c81700abdaf'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if users table has columns
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'phone' not in columns:
        op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    if 'blocked_at' not in columns:
        op.add_column('users', sa.Column('blocked_at', sa.DateTime(), nullable=True))
    if 'last_login_at' not in columns:
        op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    if 'avatar_url' not in columns:
        op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))

    # Check if user_login_logs table exists
    res = bind.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name='user_login_logs'"))
    if not res.first():
        op.create_table(
            'user_login_logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('ip_address', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'avatar_url' in columns:
        op.drop_column('users', 'avatar_url')
    if 'last_login_at' in columns:
        op.drop_column('users', 'last_login_at')
    if 'blocked_at' in columns:
        op.drop_column('users', 'blocked_at')
    if 'phone' in columns:
        op.drop_column('users', 'phone')
        
    op.drop_table('user_login_logs')
