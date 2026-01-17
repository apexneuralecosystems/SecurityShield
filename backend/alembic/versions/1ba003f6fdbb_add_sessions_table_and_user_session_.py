"""add_sessions_table_and_user_session_fields

Revision ID: 1ba003f6fdbb
Revises: 91782b460205
Create Date: 2026-01-16 23:47:39.279235

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '1ba003f6fdbb'
down_revision = '91782b460205'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns already exist in users table
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Add current_session_id if it doesn't exist
        if 'current_session_id' not in columns:
            op.add_column('users', sa.Column('current_session_id', sa.String(255), nullable=True))
            op.create_index('ix_users_current_session_id', 'users', ['current_session_id'])
        
        # Add last_login_at if it doesn't exist
        if 'last_login_at' not in columns:
            op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create sessions table if it doesn't exist
    if 'sessions' not in tables:
        op.create_table(
            'sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.String(255), nullable=False),
            sa.Column('refresh_token_hash', sa.String(255), nullable=False),
            sa.Column('access_token_jti', sa.String(255), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_sessions_id', 'sessions', ['id'], unique=False)
        op.create_index('ix_sessions_user_id', 'sessions', ['user_id'], unique=False)
        op.create_index('ix_sessions_session_id', 'sessions', ['session_id'], unique=True)
        op.create_index('ix_sessions_refresh_token_hash', 'sessions', ['refresh_token_hash'], unique=False)
        op.create_index('ix_sessions_access_token_jti', 'sessions', ['access_token_jti'], unique=False)
        op.create_index('ix_sessions_is_active', 'sessions', ['is_active'], unique=False)
        op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'], unique=False)


def downgrade() -> None:
    # Drop sessions table
    op.drop_index('ix_sessions_expires_at', table_name='sessions')
    op.drop_index('ix_sessions_is_active', table_name='sessions')
    op.drop_index('ix_sessions_access_token_jti', table_name='sessions')
    op.drop_index('ix_sessions_refresh_token_hash', table_name='sessions')
    op.drop_index('ix_sessions_session_id', table_name='sessions')
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_index('ix_sessions_id', table_name='sessions')
    op.drop_table('sessions')
    
    # Remove columns from users table
    op.drop_index('ix_users_current_session_id', table_name='users')
    op.drop_column('users', 'current_session_id')
    op.drop_column('users', 'last_login_at')

