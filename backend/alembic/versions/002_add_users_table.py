"""Add users table for authentication

Revision ID: 002_add_users
Revises: 001_initial
Create Date: 2026-01-16 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '002_add_users'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if users table already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        # Create users table
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('reset_token', sa.String(length=255), nullable=True),
            sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        # Create indexes for new table
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_reset_token'), 'users', ['reset_token'], unique=False)
    else:
        # Table exists, check and create indexes if they don't exist
        indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        
        if 'ix_users_id' not in indexes:
            op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        if 'ix_users_email' not in indexes:
            op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        if 'ix_users_reset_token' not in indexes:
            op.create_index(op.f('ix_users_reset_token'), 'users', ['reset_token'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_reset_token'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

