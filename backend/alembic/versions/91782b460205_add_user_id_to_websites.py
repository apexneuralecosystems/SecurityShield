"""add_user_id_to_websites

Revision ID: 91782b460205
Revises: 002_add_users
Create Date: 2026-01-16 23:27:42.916925

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '91782b460205'
down_revision = '002_add_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if websites table exists and has data
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'websites' in tables:
        # Get first user ID to assign existing websites
        result = conn.execute(text("SELECT id FROM users ORDER BY id LIMIT 1"))
        first_user = result.fetchone()
        default_user_id = first_user[0] if first_user else None
        
        # Drop the old unique constraint on url if it exists
        # First, get the constraint name
        indexes = inspector.get_indexes('websites')
        for idx in indexes:
            if idx['unique'] and 'url' in idx.get('column_names', []):
                op.drop_index(idx['name'], table_name='websites')
                break
        
        # Add user_id column (nullable first for existing data)
        op.add_column('websites', sa.Column('user_id', sa.Integer(), nullable=True))
        
        # If we have a default user, assign existing websites to that user
        if default_user_id:
            op.execute(text(f"UPDATE websites SET user_id = {default_user_id} WHERE user_id IS NULL"))
        
        # Make user_id NOT NULL and add foreign key
        op.alter_column('websites', 'user_id', nullable=False)
        op.create_foreign_key(
            'fk_websites_user_id',
            'websites', 'users',
            ['user_id'], ['id'],
            ondelete='CASCADE'
        )
        
        # Create index on user_id
        op.create_index('ix_websites_user_id', 'websites', ['user_id'])
        
        # Create composite unique constraint on (user_id, url)
        op.create_unique_constraint(
            'uq_websites_user_url',
            'websites',
            ['user_id', 'url']
        )


def downgrade() -> None:
    # Drop composite unique constraint
    op.drop_constraint('uq_websites_user_url', 'websites', type_='unique')
    
    # Drop foreign key and index
    op.drop_index('ix_websites_user_id', table_name='websites')
    op.drop_constraint('fk_websites_user_id', 'websites', type_='foreignkey')
    
    # Remove user_id column
    op.drop_column('websites', 'user_id')
    
    # Restore unique constraint on url (if needed)
    op.create_index('ix_websites_url', 'websites', ['url'], unique=True)

